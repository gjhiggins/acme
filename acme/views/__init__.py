"""ACME blockchain explorer for Slimcoin."""
import json
import re
import textwrap
from copy import deepcopy
import pyqrcode
import base64
import io
import requests
import textwrap
from collections import defaultdict
from datetime import datetime
from binascii import unhexlify
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from acme.lib.helpers import (
    difflag,
    iso22iso3,
    genesisblockhash,
    genesistxhash
)
import acme.lib.svgdatashapes as sd
import acme.lib.svgdatashapes_dt as sdt   # for da
from acme.lib import base58

blockfields = [
    "hash",  # "00000023b7804672de7559631ff6efc289be6cc7769fb8b896b426e586dec50e",
    "height",  # 1022289,
    "merkleroot",  # "fdc2bfea56e34cd7151daf003a0cec15cec609894d855e64cb4d94da72b9a313",
    "time",  # "2017-06-22 04:42:33 UTC",
    "difficulty",  # 0.01316071,
    "previousblockhash",  # "0000003bc14e3e76127e581a04abcec2d63d2bd5d57c0c74ad53eca4c5f0a1ab",
    "nextblockhash",  # "290ead74bd4f1ab33824da7d3b39fe74d066957df0a5051949ff753fbf9e2455",
    "tx",  # ["ea2d62761c79f84a416793f68430e5c161ec0a1fab52c427c276efe42a29d0ec base", "2017-06-22 11:39:52 UTC", " 0000000000000000000000000000000000000000000000000000000000000000 -1", " out 18.02 03578ab34f OP_CHECKSIG"]
]


genesistx = {
    "txid": "bae3867d5e5d35c321adaf9610b9e4147a855f9ad319fdcf70913083d783753f",
    "version": 1,
    "is_coinbase": True,
    "is_coinstake": False,
    "time": 1401308003,
    "locktime": 1401308003,
    "IsBurnTx": False,
    "height": 0,
    "blockhash": "00000766be5a4bb74c040b85a98d2ba2b433c5f4c673912b3331ea6f18d61bea",
    "vin": [
        {
            "coinbase": "04ffff001d020f274552543a203220736f7574686561737420556b72616e69616e20726567696f6e7320746f20686f6c64207265666572656e64756d204d617920313120617320706c616e6e6564",
            "sequence": 4294967295
        }
    ],
    "vout": [
        {
            "value": 0.00000000,
            "n": 0,
            "scriptPubKey": {
                "asm": "",
                "hex": "",
                "type": "nonstandard"
            }
        }
    ]
}


def calendarise(request, blocks):
    for i in range(0, len(blocks)):
        btime = blocks[i][5]
        try:
            blocks[i][6] = int((btime - blocks[i + 1][5]).total_seconds())
        except:
            tm = blocks[i - 1][5]
            blocks[i][6] = int((btime - tm).total_seconds())
    return blocks


@view_config(route_name='home', renderer='acme:templates/index.mako')
def home(request):
    request.tmpl_context.net = request.matchdict.get('net', 'main')
    if request.tmpl_context.net == 'main':
        request.tmpl_context.coin['binfo']['connections'] = len(
            request.tmpl_context.coin.get('addrs'))
    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.timestamp = datetime.now()
    blcn = request.tmpl_context.acmerpc.call(
        'getblock', request.tmpl_context.acmerpc.call(
            'getblockhash', binfo['blocks']))
    val = request.query_string
    try:
        request.tmpl_context.coin['lastblocktime'] = datetime.fromtimestamp(
            blcn['time'])
    except TypeError:
        request.tmpl_context.coin['lastblocktime'] = datetime.strptime(
            blcn['time'], "%Y-%m-%d %H:%M:%S %Z")
    request.tmpl_context.now = datetime.utcnow()
    query = request.tmpl_context.endpoint + '/' + request.tmpl_context.dataset + "/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0Aselect++(SUM(%3Fvalue)+as+%3Ftotal_slm_burned)+WHERE%0A%7B+%3Ftxo+ccy%3Aaddress+ccy%3ASfSLMCoinMainNetworkBurnAddr1DeTK5+.%0A++%3Ftxo+ccy%3Avalue+%3Fvalue%0A%7D" if 'proof-of-burn' in request.tmpl_context.scheme else ''
    request.tmpl_context.netburnedcoins = json.loads(requests.get(query).content.decode('utf-8'))['results']['bindings'][0]['total_slm_burned']['value']if 'proof-of-burn' in request.tmpl_context.scheme else 0

    diff = request.tmpl_context.acmerpc.call('getdifficulty')
    request.tmpl_context.curpowdiff = '{:.6f}'.format(diff['proof-of-work'] if isinstance(diff, dict) else diff) if 'proof-of-work' in request.tmpl_context.scheme else 0
    request.tmpl_context.curposdiff = '{:.6f}'.format(diff['proof-of-stake']) if 'proof-of-stake' in request.tmpl_context.scheme else 0
    request.tmpl_context.curhashrate = request.tmpl_context.acmerpc.call(request.tmpl_context.coin.get('nethashcmd'))

    blocks = []
    toffset = int(val) if val is not None and val != '' else binfo['blocks']
    for bnum in range(toffset, toffset - 60, -1):
        bhash = request.tmpl_context.acmerpc.call('getblockhash', bnum)
        bblock = request.tmpl_context.acmerpc.call('getblock', bhash)
        bdiff = bblock.get('difficulty', -1)
        btime = datetime.fromtimestamp(bblock['time']) if isinstance(bblock['time'], int) else datetime.strptime(bblock['time'], request.tmpl_context.coin.get('strftimeformat'))
        valout_accumulator = 0
        for numtx, txid in enumerate(bblock['tx']):
            tx = request.tmpl_context.acmerpc.call('getrawtransaction', txid, 1)
            if tx is not False:
                for vout in tx['vout']:
                    valout_accumulator += vout['value']
        blocks.append(
            [bnum, bhash, bdiff, bblock.get('flags', 'proof-of-work'), bblock['time'],
             btime, 0, numtx + 1, valout_accumulator])

    blocks = calendarise(request, blocks)
    request.tmpl_context.blocks = blocks
    request.tmpl_context.difflag = difflag(blocks, scheme=['proof-of-work', 'proof-of-stake', 'proof-of-burn'])
    return request.tmpl_context.__dict__


@view_config(route_name='index', renderer='acme:templates/index.mako')
def index(request):
    request.tmpl_context.net = request.matchdict.get('net', 'main')
    if request.tmpl_context.net == 'main':
        request.tmpl_context.coin['binfo']['connections'] = len(
            request.tmpl_context.acmerpc.call('getpeerinfo'))
    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.timestamp = datetime.now()
    blcn = request.tmpl_context.acmerpc.call(
        'getblock', request.tmpl_context.acmerpc.call(
            'getblockhash', binfo['blocks']))
    val = request.query_string
    try:
        request.tmpl_context.coin['lastblocktime'] = datetime.fromtimestamp(
            blcn['time'])
    except TypeError:
        request.tmpl_context.coin['lastblocktime'] = datetime.strptime(
            blcn['time'], "%Y-%m-%d %H:%M:%S %Z")
    request.tmpl_context.now = datetime.utcnow()
    query = request.tmpl_context.endpoint + '/' + request.tmpl_context.dataset + "/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0Aselect++(SUM(%3Fvalue)+as+%3Ftotal_slm_burned)+WHERE%0A%7B+%3Ftxo+ccy%3Aaddress+ccy%3ASfSLMCoinMainNetworkBurnAddr1DeTK5+.%0A++%3Ftxo+ccy%3Avalue+%3Fvalue%0A%7D" if 'proof-of-burn' in request.tmpl_context.scheme else ''
    request.tmpl_context.netburnedcoins = json.loads(requests.get(query).content.decode('utf-8'))['results']['bindings'][0]['total_slm_burned']['value'] if 'proof-of-burn' in request.tmpl_context.scheme else 0
    diff = request.tmpl_context.acmerpc.call('getdifficulty')
    request.tmpl_context.curpowdiff = '{:.6f}'.format(diff['proof-of-work'] if isinstance(diff, dict) else diff) if 'proof-of-work' in request.tmpl_context.scheme else 0
    request.tmpl_context.curposdiff = '{:.6f}'.format(diff['proof-of-stake']) if 'proof-of-stake' in request.tmpl_context.scheme else 0
    request.tmpl_context.curhashrate = request.tmpl_context.acmerpc.call(request.tmpl_context.coin.get('nethashcmd'))

    blocks = []
    toffset = int(val) if val is not None and val != '' else binfo['blocks']
    for bnum in range(toffset, toffset - 60, -1):
        bhash = request.tmpl_context.acmerpc.call('getblockhash', bnum)
        bblock = request.tmpl_context.acmerpc.call('getblock', bhash)
        bdiff = bblock.get('difficulty', -1)
        if request.tmpl_context.coin.get('blockdateformat', 'formatted') == 'seconds':
            btime = datetime.fromtimestamp(bblock['time'])
        else:
            btime = datetime.strptime(bblock['time'], request.tmpl_context.coin.get('strftimeformat'))
        valout_accumulator = 0
        for numtx, txid in enumerate(bblock['tx']):
            tx = request.tmpl_context.acmerpc.call('getrawtransaction', txid, 1)
            if tx is not False:
                for vout in tx['vout']:
                    valout_accumulator += vout['value']
        blocks.append(
            [bnum, bhash, bdiff, bblock.get('flags', 'proof-of-work'), bblock['time'],
             btime, 0, numtx + 1, valout_accumulator])

    blocks = calendarise(request, blocks)
    request.tmpl_context.blocks = blocks
    request.tmpl_context.difflag = difflag(blocks)
    return request.tmpl_context.__dict__


@view_config(route_name='blocks', renderer='acme:templates/blocks.mako')
def blocks(request):
    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.timestamp = datetime.now()
    bblock = request.tmpl_context.acmerpc.call(
        'getblock', request.tmpl_context.acmerpc.call(
            'getblockhash', binfo['blocks']))
    val = request.query_string
    if request.tmpl_context.coin.get('blockdateformat', 'formatted') == 'seconds':
        btime = datetime.fromtimestamp(bblock['time'])
    else:
        btime = datetime.strptime(bblock['time'], request.tmpl_context.coin.get('strftimeformat'))
    request.tmpl_context.now = datetime.utcnow()
    # request.tmpl_context.coin['sincelastblock'] = (datetime.now() - request.tmpl_context.coin['lastblocktime']).seconds
    request.tmpl_context.neffectiveburncoins = '{}'.format(
        bblock.get('Formatted nEffectiveBurnCoins', -1))
    diff = request.tmpl_context.acmerpc.call('getdifficulty')
    request.tmpl_context.curpowdiff = '{:.6f}'.format(diff['proof-of-work'] if isinstance(diff, dict) else diff) if 'proof-of-work' in request.tmpl_context.scheme else 0
    request.tmpl_context.curposdiff = '{:.6f}'.format(diff['proof-of-stake']) if 'proof-of-stake' in request.tmpl_context.scheme else 0
    request.tmpl_context.curhashrate = request.tmpl_context.acmerpc.call(request.tmpl_context.coin.get('nethashcmd'))

    blocks = []
    toffset = int(val) if val is not None and val != '' else binfo['blocks']
    for bnum in range(toffset, toffset - int(request.tmpl_context.nbpp), -1):
        bhash = request.tmpl_context.acmerpc.call('getblockhash', bnum)
        bblock = request.tmpl_context.acmerpc.call('getblock', bhash)
        bdiff = bblock.get('difficulty', -1)
        try:
            btime = datetime.strptime(bblock['time'], '%Y-%m-%d %H:%M:%S %Z')
        except:
            btime = datetime.fromtimestamp(
                bblock['time']).strftime('%H:%M:%S %d-%m-%Y')
        valout_accumulator = 0
        for numtx, txid in enumerate(bblock['tx']):
            tx = request.tmpl_context.acmerpc.call('getrawtransaction', txid, 1)
            if tx is not False:
                for vout in tx['vout']:
                    valout_accumulator += vout['value']
        blocks.append(
            [bnum, bhash, bdiff, bblock.get('flags', 'proof-of-work'), bblock['time'],
             btime, 0, numtx + 1, valout_accumulator])
    blocks = calendarise(request, blocks)
    pag = '''<div class="item">'''
    if toffset != -1:
        pag += '''<a class="item" {}">'''.format('href="/?{}"'.format(toffset - int(request.tmpl_context.nbpp)))
        pag += '''<button class="ui right floated mini primary button" style="margin-right:12em">Older</button></a>'''
    else:
        pag += '''<a class="item"">'''
        pag += '''<button class="ui right floated disabled mini primary button" style="margin-right:12em">Older</button></a>'''
    if toffset < binfo['blocks']:
        pag += '''<a class="item" {}>'''.format('href="/?{}"'.format(toffset + int(request.tmpl_context.nbpp)))
        pag += '''<button class="ui left floated mini primary button" style="margin-left:12em">Newer</button></a>'''
    else:
        pag += '''<a class="item">'''
        pag += '''<button class="ui left floated disabled mini primary button" style="margin-left:12em">Newer</button></a>'''
    pag += '</div>'
    request.tmpl_context.blocks = blocks
    request.tmpl_context.pag = pag
    return request.tmpl_context.__dict__


@view_config(route_name='blocklist', renderer='acme:templates/blocks.mako')
def blocklist(request):
    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.nbpp = 25
    val = int(request.matchdict.get('arg', binfo['blocks']))
    # binfo['blocks'] = int(val)
    request.tmpl_context.coin['binfo'] = binfo
    request.tmpl_context.timestamp = datetime.now()
    blocks = []
    toffset = val  # binfo['blocks']
    offsetcnt = int(request.tmpl_context.nbpp)
    toffset = offsetcnt if toffset < offsetcnt else toffset
    for bnum in range(toffset, toffset - int(request.tmpl_context.nbpp), -1):
        bhash = request.tmpl_context.acmerpc.call('getblockhash', bnum)
        bblock = request.tmpl_context.acmerpc.call('getblock', bhash)
        bdiff = bblock.get('difficulty', -1)
        if request.tmpl_context.coin.get('blockdateformat', 'formatted') == 'seconds':
            btime = datetime.fromtimestamp(bblock['time'])
        else:
            btime = datetime.strptime(bblock['time'], request.tmpl_context.coin.get('strftimeformat'))
        valout_accumulator = 0
        for numtx, txid in enumerate(bblock['tx']):
            if txid == genesistxhash:
                pass                
            else:
                tx = request.tmpl_context.acmerpc.call('getrawtransaction', txid, 1)
                if tx is not False:
                    for vout in tx['vout']:
                        valout_accumulator += vout['value']
        blocks.append(
            [bnum, bhash, bdiff, bblock.get('flags', 'proof-of-work'), bblock['time'],
             btime, 0, numtx + 1, valout_accumulator])
    blocks = calendarise(request, blocks)
    pag = '''<div class="item">'''
    if toffset != -1:
        pag += '''<a class="item" {}">'''.format('href="{}"'.format(request.route_url('blocklist', net=request.tmpl_context.net, arg=toffset - int(request.tmpl_context.nbpp))))
        pag += '''<button class="ui right floated mini primary button" style="margin-right:12em">Older</button></a>'''
    else:
        pag += '''<a class="item"">'''
        pag += '''<button class="ui right floated disabled mini primary button" style="margin-right:12em">Older</button></a>'''
    if toffset < binfo['blocks']:
        pag += '''<a class="item"{}>'''.format(' href="{}"'.format(request.route_url('blocklist', net=request.tmpl_context.net, arg=toffset + int(request.tmpl_context.nbpp))))
        pag += '''<button class="ui left floated mini primary button" style="margin-left:12em">Newer</button></a>'''
    else:
        pag += '''<a class="item">'''
        pag += '''<button class="ui left floated disabled mini primary button" style="margin-left:12em">Newer</button></a>'''
    pag += '</div>'
    request.tmpl_context.blocks = blocks
    request.tmpl_context.pag = pag
    return request.tmpl_context.__dict__


@view_config(route_name='block', renderer='acme:templates/block.mako')
def blk(request):
    binfo = request.tmpl_context.coin['binfo']
    val = request.matchdict.get('arg', genesisblockhash)
    nblock = request.tmpl_context.acmerpc.call('getblock', val)
    request.tmpl_context.dump = '''<pre>{}</pre>'''.format(
        json.dumps(nblock, sort_keys=True, indent=2, separators=(',', ': ')))
    cnt = ''
    oitems = {}
    for k in blockfields:
        v = nblock.get(k)
        if k == 'tx':
            oitems['txids'] = []
            # print("Transactions: {}".format(v))
            for tx in v:  # list of txs
                # print("TX: {}".format(tx))
                if 'base' in tx[0]:
                    txid = tx[0].strip().split(' ')[0]
                    oitems['txids'].append(txid)
                    cnt += """<span>{}: <a href="/tx/{}"><span>{}</span></a></span><br />""".format(
                        k, txid, txid)
                    rtx = request.tmpl_context.acmerpc.call('getrawtransaction', txid, 1)
                    if not rtx:
                        pass
                else:
                    txid = tx
                    oitems['txids'].append(txid)
                    cnt += """<span>{k}: <a href="{r}"><span>{i}</span></a></span><br />""".format(
                        k=k, r=request.route_url('transaction', net=net, arg=txid), i=txid)
                    if txid == genesistxhash:
                        pass
                    else:
                        rtx = request.tmpl_context.acmerpc.call('getrawtransaction', txid, 1)
                        if not rtx:
                            raise Exception("rawtransaction returned no details for tx id {}".format(txid))
        else:  # block fields
            oitems[k] = v
            if k in ['previousblockhash', 'nextblockhash']:
                cnt += '''<div>{k}: <a href="{r}"><span>{v}</span></a></div/>'''.format(k=k, r=request.route_url('block', net=net, arg=v), v=v)
            elif k == 'time':
                if isinstance(v, int):
                    ktime = datetime.fromtimestamp(v).isoformat()
                else:
                    ktime = datetime.strptime(v, '%Y-%m-%d %H:%M:%S %Z').isoformat()
                cnt += '''<div>{}: <span>{}</span></span> <span class="glit">{}</div>'''.format(k, v, ktime)
                oitems[k] = ktime
            else:
                cnt += '''<div>{}: <span>{}</span></div>'''.format(k, v)
    request.tmpl_context.content = cnt
    request.tmpl_context.rdfasjson = json.dumps(oitems)
    request.tmpl_context.oitems = oitems
    return request.tmpl_context.__dict__


@view_config(route_name='transactions', renderer='acme:templates/transactions.mako')
def txs(request):
    scnt = ""
    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.txfilter = ''
    txs = []
    toffset = binfo['blocks']
    for bnum in range(toffset, toffset - 20, -1):
        bhash = request.tmpl_context.acmerpc.call('getblockhash', bnum)
        bblock = request.tmpl_context.acmerpc.call('getblock', bhash)
        txs.append([[
            request.tmpl_context.acmerpc.call('getrawtransaction', txid, 1) for txid in bblock['tx']],
            bblock['height'],
            datetime.strptime(bblock['time'], request.tmpl_context.coin.get('txdateformat')).isoformat()
        ])
    request.tmpl_context.txs = txs
    request.tmpl_context.dump = '''<pre>{}</pre>'''.format(json.dumps(txs, sort_keys=True, indent=2, separators=(',', ': ')))
    return request.tmpl_context.__dict__


@view_config(route_name='transaction', renderer='acme:templates/transaction.mako')
def tx(request):
    scnt = ""
    binfo = request.tmpl_context.coin['binfo']
    val = request.matchdict.get('arg', genesistxhash)
    if val == genesistxhash:
        tx = genesistx
    else:
        tx = request.tmpl_context.acmerpc.call('getrawtransaction', val, 1)
    assert tx is not False
    request.tmpl_context.dump = '''<pre>{}</pre>'''.format(
        json.dumps(tx, sort_keys=True, indent=2, separators=(',', ': ')))
    if tx.get('hex', '') != []:
        tx['hex'] = textwrap.wrap(tx.get('hex', ' '), width=40)
    else:
        tx['hex'] = ''
    txattrs = {
        'date': datetime.fromtimestamp(tx.get('time')),
        'height': request.tmpl_context.acmerpc.call('getblock', tx.get('blockhash')).get('height')
    }
    for attr in ['confirmations', 'blockhash', 'txid', 'IsBurnTx']:
        attrval = tx.get(attr)
        if attrval is not None:
            txattrs[attr.lower()] = attrval
    request.tmpl_context.inputs = []
    for v in tx['vin']:
        if v.get('txid') is not None:
            ptx = request.tmpl_context.acmerpc.call('getrawtransaction', v.get('txid'), 1)
            v['confirmations'] = ptx['confirmations']
            if ptx['vin'][0].get('coinbase') is not None:
                v['amount'] = ptx['vout'][0]['value']
        if v.get('scriptSig') is not None:
            vasm = textwrap.wrap(v.get('scriptSig').get('asm', ''), width=30)
            vhex = textwrap.wrap(v.get('scriptSig').get('hex', ''), width=30)
            v['scriptSignice'] = dict(asm=vasm, hex=vhex)
        request.tmpl_context.inputs.append(v)
    request.tmpl_context.outputs = []
    for i, v in enumerate(tx['vout']):
        if v.get('scriptPubKey') is not None and v.get('scriptPubKey').get('type') != 'nonstandard':
            try:
                v['address'] = v['scriptPubKey']['addresses'][0]
            except:
                v['address'] = tx['vout'][i - 1]['scriptPubKey']['addresses'][0]
            buff = io.BytesIO()
            url = pyqrcode.create(v.get('address'))
            url.svg(buff, scale=2, module_color='#cacaca', xmldecl=True, svgns=True, title="{}".format(v.get('address')), svgclass='pyqrcode', lineclass='pyqrline', omithw=False, debug=False)
            v['qrcode'] = 'data:image/svg+xml;base64,' + base64.b64encode(buff.getvalue()).decode('utf-8')
            vasm = textwrap.wrap(v.get('scriptPubKey').get('asm', ''), width=30)
            vhex = textwrap.wrap(v.get('scriptPubKey').get('hex', ''), width=30)
            v['scriptPubKeynice'] = dict(asm=vasm, hex=vhex)
            request.tmpl_context.outputs.append(v)

    request.tmpl_context.txattrs = txattrs
    return request.tmpl_context.__dict__


@view_config(route_name='nodes', renderer='acme:templates/nodes.mako')
def nodes(request):
    nodes = request.tmpl_context.acmerpc.call('getpeerinfo')
    known = request.registry.settings.get('nodes')
    hits = dict()
    versions = {}
    for i, node in enumerate(nodes):
        for attr in ["conntime", "lastrecv", "lastsend"]:
            v = nodes[i][attr]
            if isinstance(v, int):
                v += 0.0000
                nodes[i][attr] = datetime.fromtimestamp(v).strftime("%c")
            else:
                pass
        if nodes[i]['addr'] not in known:
            res = json.loads(requests.get("http://freegeoip.net/json/{}".format(node['addr'].rsplit(':')[0])).content.decode('utf-8'))
            nodes[i]['geoloc'] = res
        else:
            nodes[i]['geoloc'] = known[nodes[i]['geolod']]

        try:
            hits[iso22iso3[node['geoloc']['country_code']]] += 1
        except:
            try:
                hits[iso22iso3[node['geoloc']['country_code']]] = 1
            except:
                nodes[i]['geoloc']['country_name'] = "Great Britain"
                nodes[i]['geoloc']['country_code'] = "GB"
                hits[iso22iso3[node['geoloc']['country_code']]] = 1

        data = list(filter(lambda x: x > '', node['subver'].split('/')))
        if len(data) > 1:
            _, version = data
            mainv, _ = version.split('(')
        else:
            mainv = 'SLIMCoin:0.3.2'
        v = mainv.split(':')[1]
        versions[v] = versions.get(v, 0) + 1

    request.tmpl_context.freqcnt = defaultdict(int)
    for node in nodes:
        request.tmpl_context.freqcnt[node.get('geoloc').get('country_code')] += 1
    request.registry.settings['nodes'] = known
    dump = json.dumps(nodes, sort_keys=True, indent=2, separators=(',', ': '))
    request.tmpl_context.nodes = nodes
    request.tmpl_context.versions = [dict(label=k, value=v) for k, v in versions.items()]
    request.tmpl_context.cchosts = json.dumps([[k, v] for k, v in hits.items()])
    request.tmpl_context.dump = dump
    return request.tmpl_context.__dict__


@view_config(route_name='node', renderer='acme:templates/node.mako')
def node(request):
    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.nodes = \
        request.tmpl_context.acmerpc.call('getpeerinfo')
    dump = json.dumps(
        request.tmpl_context.nodes,
        sort_keys=True, indent=2, separators=(',', ': '))
    request.tmpl_context.dump = dump
    return request.tmpl_context.__dict__


@view_config(route_name='address', renderer='acme:templates/address.mako')
def addr(request):
    """Dicstring."""
    import binascii

    def processinput(r, k):
        if k in ['address', 'transaction']:
            return request.route_url(
                k, net=request.tmpl_context.net,
                arg=r[k]['value'].replace('http://purl.org/net/bel-epa/ccy#', '')[
                    1 if k == 'transaction' else 0:])
        elif k in ['datetime', 'value']:
            return datetime.fromtimestamp(
                int(r[k]['value'])).isoformat() if k == 'datetime' \
                    else eval(r[k]['value'])
            # return eval(r[k]['value'])
        else:
            return r[k]['value']

    def processoutput(r, k):
        if k in ['address', 'transaction']:
            return request.route_url(
                k, net=request.tmpl_context.net,
                arg=r[k]['value'].replace('http://purl.org/net/bel-epa/ccy#', '')[
                    1 if k == 'transaction' else 0:])
        elif k in ['datetime', 'value']:
            return datetime.fromtimestamp(
                int(r[k]['value'])).isoformat() if k == 'datetime' \
                    else eval(r[k]['value'])
            # return eval(r[k]['value'])
        else:
            return r[k]['value']

    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.coin['binfo'] = binfo
    val = request.matchdict.get(
        'arg', '4b8b6856954392a8484c9520a2f3ec55ac0ecb93dcb466da27fb25eba0f785ff')
    request.tmpl_context.adattrs = {}
    request.tmpl_context.adattrs['addr'] = val
    request.tmpl_context.adattrs['pubkeyhash'] = binascii.hexlify(base58.decode(val)).decode('utf-8')

    """
    # SPARQL query returning outputs for an address

    PREFIX ccy: <http://purl.org/net/bel-epa/ccy#>
    SELECT DISTINCT ?txo ?datetime ?value ?stype WHERE {
      ?txo ccy:address ccy:${adattrs.get('addr')} .
      ?tx ccy:output ?txo . ?tx ccy:time ?datetime .
      ?txo ccy:value ?value . ?txo ccy:type ?stype
    } ORDER BY DESC(?datetime)"
    
    # SPARQL query returning inputs for an address

    PREFIX ccy: <http://purl.org/net/bel-epa/ccy#>
    SELECT DISTINCT ?tx ?datetime ?addr ?value WHERE {
      ccy:${adattrs.get('address', 'ShooqRfkshDajLTvYMEKRKxXW7ooZLBZsm')} ccy:tx ?tx .
      ?tx ccy:input ?txi .
      ?tx ccy:output ?txo .
      ?tx ccy:time ?datetime .
      ?txo ccy:value ?value .
      ?txo ccy:address ?addr
    } ORDER BY DESC(?datetime)"
    """

    outputqstr = \
        "/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet" \
        "%2Fbel-epa%2Fccy%23%3E+SELECT+DISTINCT(%3Ftxo+AS+%3Ftransa" \
        "ction) %3Fdatetime+%3Fvalue+%3Fstype+WHERE+%7B+%3Ftxo+ccy%" \
        "3Aaddress+ccy%3A{addr}+.+%3Ftx+ccy%3Aoutput+%3Ftxo+.+%3Ftx+" \
        "ccy%3Atime+%3Fdatetime+.+%3Ftxo+ccy%3Avalue+%3Fvalue+.+%3F" \
        "txo+ccy%3Atype+%3Fstype+%7D+ORDER+BY+DESC(%3Fdatetime)"

    inputqstr = \
        "/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet" \
        "%2Fbel-epa%2Fccy%23%3E+SELECT+DISTINCT(%3Ftx+AS+%3Ftransac" \
        "tion)+%3Fdatetime+%3Faddress+%3Fvalue+WHERE+%7B+ccy%3A{addr" \
        "}+ccy%3Atx+%3Ftx+.+%3Ftx+ccy%3Ainput+%3Ftxi+.+%3Ftx+ccy%3A" \
        "output+%3Ftxo+.+%3Ftx+ccy%3Atime+%3Fdatetime+.+%3Ftxo+ccy%" \
        "3Avalue+%3Fvalue+.+%3Ftxo+ccy%3Aaddress+%3Faddress+%7D+ORD" \
        "ER+BY+DESC(%3Fdatetime)%0A"

    addr = request.tmpl_context.adattrs.get('addr')
    output_query = request.tmpl_context.endpoint + '/' + request.tmpl_context.dataset + outputqstr  # "/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E+SELECT+DISTINCT(%3Ftxo+AS+%3Ftransaction) %3Fdatetime+%3Fvalue+%3Fstype+WHERE+%7B+%3Ftxo+ccy%3Aaddress+ccy%3A{addr}+.+%3Ftx+ccy%3Aoutput+%3Ftxo+.+%3Ftx+ccy%3Atime+%3Fdatetime+.+%3Ftxo+ccy%3Avalue+%3Fvalue+.+%3Ftxo+ccy%3Atype+%3Fstype+%7D+ORDER+BY+DESC(%3Fdatetime)"
    input_query = request.tmpl_context.endpoint + '/' + request.tmpl_context.dataset + inputqstr  # "/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E+SELECT+DISTINCT(%3Ftx+AS+%3Ftransaction)+%3Fdatetime+%3Faddress+%3Fvalue+WHERE+%7B+ccy%3A{addr}+ccy%3Atx+%3Ftx+.+%3Ftx+ccy%3Ainput+%3Ftxi+.+%3Ftx+ccy%3Aoutput+%3Ftxo+.+%3Ftx+ccy%3Atime+%3Fdatetime+.+%3Ftxo+ccy%3Avalue+%3Fvalue+.+%3Ftxo+ccy%3Aaddress+%3Faddress+%7D+ORDER+BY+DESC(%3Fdatetime)%0A"

    inputresults = requests.get(input_query.format(addr=addr)).json()
    outputresults = requests.get(output_query.format(addr=addr)).json()
    request.tmpl_context.inputs = [
        dict([(k, processinput(r, k)) for k in r.keys()])
        for r in inputresults['results']['bindings']]
    request.tmpl_context.outputs = [
        dict([(k, processoutput(r, k)) for k in r.keys()])
        for r in outputresults['results']['bindings']]
    request.tmpl_context.outputkeys = ["tx", "datetime", "value", "stype"]
    request.tmpl_context.inputkeys = ["tx", "datetime", "value", "addr"]

    request.tmpl_context.inputsdump = json.dumps(
        inputresults, sort_keys=True, indent=2, separators=(',', ': '))
    request.tmpl_context.outputsdump = json.dumps(
        outputresults, sort_keys=True, indent=2, separators=(',', ': '))
    # request.tmpl_context.dump = dump
    request.tmpl_context.content = ""
    return request.tmpl_context.__dict__


@view_config(route_name='publications', renderer='acme:templates/publications.mako')
def pbs(request):
    binfo = request.tmpl_context.coin['binfo']
    dumpq = textwrap.dedent("""\
        # SPARQL query:

        PREFIX ccy: &lt;http://purl.org/net/bel-epa/ccy#&gt;
        SELECT ?tx ?bh ?txo ?dt ?asm
        WHERE {
          ?tx ccy:output ?txo .
          ?txo ccy:pkasm ?asm .
          ?tx ccy:blockhash ?bh .
          ?tx ccy:time ?dt .
          FILTER regex(?asm, "OP_RETURN")
        } ORDER BY DESC(?dt)

        # Results:

        """)
    query = request.tmpl_context.endpoint + "/" + \
        request.tmpl_context.dataset + "/sparql" + \
        "?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy" \
        "%23%3E%0ASELECT+%3Ftx+%3Fbh+%3Ftxo+%3Fdt+%3Fasm%0AWHERE+%7B%0A++%3F" \
        "tx+ccy%3Aoutput+%3Ftxo+.%0A++%3Ftxo+ccy%3Apkasm+%3Fasm+.%0A++%3Ftx+" \
        "ccy%3Ablockhash+%3Fbh+.%0A++%3Ftx+ccy%3Atime+%3Fdt+.%0A++FILTER+reg" \
        "ex(%3Fasm%2C+%22OP_RETURN%22)%0A%7D+ORDER+BY+DESC(%3Fdt)%0A"
    res = json.loads(requests.get(query).content.decode('utf-8'))
    request.tmpl_context.dump = dumpq + json.dumps(
        res, sort_keys=True, indent=2, separators=(',', ': '))
    pubs = []
    seen = {}
    for r in res["results"]["bindings"]:
        blkhash = r["bh"]["value"]
        if blkhash.startswith('http'):
            blkhash = blkhash.split('ccy#C')[-1]
        tx = r["tx"]['value']
        if tx.startswith('http'):
            tx = tx.split('ccy#C')[-1]
        dt = r["dt"]['value']
        block = request.tmpl_context.acmerpc.call('getblock', blkhash)
        inscription = unhexlify(
            r["asm"]["value"].split(' ')[1][8:]).decode('utf-8')
        if seen.get(blkhash) != tx:
            # if inscription.startswith('magnet'):
            #     inscriptionref = '<a href="{i}">{i}</a>'.format(i=inscription)
            # else:
            #     inscriptionref = '{}'.format(inscription)
            seen[blkhash] = tx
            pubs.append([inscription, blkhash, block, tx])
    request.tmpl_context.pubs = pubs
    return request.tmpl_context.__dict__


@view_config(route_name='network', renderer='acme:templates/network.mako')
def net(request):
    """
    The network hash rate can be statistically inferred from the difficulty
    and the rate at which blocks are found. It's just a more complex version
    of the fact that if you know that someone is flipping coins and heads
    comes up 800 times an hour, they're flipping about 1,600 coins an hour.

    The hashrate can be calculated from the expected rate of finding a block
    (144 a day for Bitcoin), the actual rate of finding a block and the
    current difficulty.

    So let's calculate the average Bitcoin hash_rate for a single day:

    expected_blocks = 144
    difficulty = 11187257.461361 # this is on May 22nd 2013
    blocks_found = 155 # Also May 22nd 2013
    hash_rate = (blocks_found/expected_blocks*difficulty * 2**32 / 600)

    The reason we use a day to average out the hash_rate is that taken block
    by block the variance would be really high and we would not get anything
    meaningful.

    """
    import itertools
    merged = sorted(
        [[m[1], m[0]] for m in list(
            itertools.chain.from_iterable(
                [m for m in [d for y, d in request.tmpl_context.histoire]]))],
        key=lambda x: x[0])
    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.dump = json.dumps(merged)
    data = []
    for i, [d, b] in enumerate(merged):
        dt = datetime.fromtimestamp(d).strftime('%Y-%m-%dT%H:%M:%S')
        if i < 2:
            pass
        else:
            data.append(
                (dt, int((d - merged[i - 1][0]) / (b - merged[i - 1][1]))))

    def svgdatashape(data):
        sd.svgbegin(width=1000, height=300)

        sd.setline(color='#777')   # set gray line color
        sd.settext(color='#555')   # set gray text color

        # indicate our datetime notation...
        sdt.dateformat('%Y-%m-%dT%H:%M:%S')

        # find min max range of the datetimes and set up X space
        # xrange = sdt.daterange(
        #    column=0, datarows=data, nearest='day', inc='6hour',
        #    stubformat='%l%P', inc2='day', stub2format='%b %d',
        #    stub2place='replace')
        xrange = sdt.daterange(
            column=0, datarows=data, nearest='month', inc='month',
            stubformat='%b', inc2='year', stub2format=' %Y',
            stub2place='replace')
        sd.xspace(svgrange=(50, 950), datarange=xrange)

        # find Y min max numeric range and set up Y space...
        for dp in data:
            sd.findrange(testval=dp[1])  
        yrange = sd.findrange(finish=True)
        sd.yspace(svgrange=(60, 280), datarange=yrange)

        # render axesd...
        sd.settext(color='#555', ptsize=11)
        sd.xaxis(stublist=xrange.stublist, tics=8, grid=True)
        sd.yaxis(tics=8)
        sd.plotdeco(title='Date time data', outline=True)

        # render red bars
        for dp in data:
            sd.bar(x=sdt.toint(dp[0]), y=dp[1], color='#4f4', width=5, opacity=0.6)
        # return the svg.  The caller could then add it in to the rendered HTML.
        return sd.svgresult()

    request.tmpl_context.chart = svgdatashape(data)

    request.tmpl_context.dump = json.dumps(data)
    return request.tmpl_context.__dict__


@view_config(route_name='search', renderer='json')  # renderer='acme:templates/search.mako'
def search(request):
    from collections import OrderedDict
    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.query = request.matchdict.get('arg')
    request.tmpl_context.dump = ""
    # return request.tmpl_context.__dict__
    return dict(results=list(
        OrderedDict(
            title="Block: {}".format(request.tmpl_context.query),
            url=request.route_url(
                'block',
                net=request.tmpl_context.net,
                arg=request.tmpl_context.query))))


@view_config(route_name='publication', renderer='acme:templates/publication.mako')
def pb(request):
    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.dump = ""
    return request.tmpl_context.__dict__


# @view_config(route_name='exchange', renderer='acme:templates/exchange.mako')
# def ex(request):
#     binfo = request.tmpl_context.coin['binfo']
#     request.tmpl_context.dump = ""
#     return request.tmpl_context.__dict__


@view_config(route_name='sparql', renderer='acme:templates/sparqlquery.mako')
def sparql(request):
    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.dump = ""
    return request.tmpl_context.__dict__


@view_config(route_name='blockbrowser', renderer='acme:templates/blockbrowser.mako')
def blockbrowser(request):
    binfo = request.tmpl_context.coin['binfo']
    request.tmpl_context.dump = ""
    return request.tmpl_context.__dict__


@view_config(route_name='test', renderer='acme:templates/test.mako')
def test(request):
    sym = request.tmpl_context.coin['symbol'].lower()
    binfo = request.tmpl_context.coin['binfo']
    sparqlquery = \
        "http://localhost:3030/{sym}chain/sparql?query=SELECT+*+WHERE" \
        "+%7B%3Fs+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23height%3E+" \
        "1000+.+%3Fs+%3Fp+%3Fo+.+%7D".format(sym)
    request.tmpl_context.sparqljson = \
        requests.get(sparqlquery).content.decode('utf-8')
    request.tmpl_context.query = request.matchdict.get('arg')
    request.tmpl_context.dump = ""
    return request.tmpl_context.__dict__
