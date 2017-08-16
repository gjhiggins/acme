#! /usr/bin/env python3
import unittest
from datetime import datetime, timedelta, tzinfo
import json
import re
import requests
import time
from rdflib import (
    Namespace,
    URIRef,
    Graph,
    Literal,
)
from rdflib.namespace import RDF, XSD, SKOS
import configparser

config = configparser.ConfigParser()
config.read('coin.ini')
mainnet = dict((key, config['mainnet'][key]) for key in config['mainnet'])
testnet = dict((key, config['testnet'][key]) for key in config['testnet'])

global blockhash
debug = False
test = False


class RPCHost(object):
    def __init__(self, url):
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}

    def call(self, rpcMethod, *params):
        payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
        tries = 10
        hadConnectionFailures = False
        while True:
            # print("{url} {headers} {data}".format(url=self._url, headers=self._headers, data=payload))
            try:
                response = self._session.get(self._url, headers=self._headers, data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception('Failed to connect for remote procedure call.')
                hadConnectionFailures = True
                print("Couldn't connect for remote procedure call, will sleep for ten seconds and then try again ({} more tries)".format(tries))
                time.sleep(10)
            else:
                if hadConnectionFailures:
                    print('Connected for remote procedure call after retry.')
                break
        if response.status_code not in (200, 500):
            raise Exception('RPC connection failure: ' + str(response.status_code) + ' ' + response.reason)
        responseJSON = response.json()
        if 'error' in responseJSON and responseJSON['error'] is not None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        return responseJSON['result']


class GMT1(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=1) + self.dst(dt)

    def dst(self, dt):
        # DST starts last Sunday in March
        d = datetime(dt.year, 4, 1)   # ends last Sunday in October
        self.dston = d - timedelta(days=d.weekday() + 1)
        d = datetime(dt.year, 11, 1)
        self.dstoff = d - timedelta(days=d.weekday() + 1)
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return timedelta(hours=1)
        else:
            return timedelta(0)

    def tzname(self, dt):
        return "GMT +1"

blockfields = [
    'size',
    'height',
    'version',
    'headerhash',
    'merkleroot',
    'time',
    'difficulty',
    'transition',
    'primechain',
    'primeorigin',
    'previousblockhash',
    'nextblockhash',
]


doacc_rubric_n3 = """
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix doacc: <http://purl.org/net/bel-epa/doacc#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

doacc:D6b7dd05f-19f2-4b36-833d-f4bda4be58f5 a doacc:Cryptocurrency ;
    dc:description "Slimcoin burn mining is truly ASIC-proof."@en ;
    doacc:block-reward "50"^^xsd:string ;
    doacc:block-time 90 ;
    doacc:date-founded "2014-05-28"^^xsd:date ;
    doacc:distribution-scheme doacc:Dc10c93fb-f7ec-40cd-a06e-7890686f6ef8 ;
    doacc:image "datacoin_dat.png"^^xsd:string ;
    doacc:incept "2014-05"^^xsd:string ;
    doacc:pow doacc:D28483031-b854-4853-9a35-e1daf97e4c59 ;
    doacc:protection-scheme doacc:D493eab2e-eeba-496d-afca-c9372c6efe9a ;
    doacc:protocol doacc:Dede0f611-3a23-4794-b768-0740933a5ff6 ;
    doacc:retarget-time "continuous"^^xsd:string ;
    doacc:reward-modifier "var/diff"^^xsd:string ;
    doacc:symbol "SLM"@en ;
    doacc:total-coins "250000000"^^xsd:string ;
    skos:prefLabel "Slimcoin"@en .

doacc:Dc10c93fb-f7ec-40cd-a06e-7890686f6ef8 a doacc:DistributionScheme ;
    dc:description "Dissemination via proof of work"@en ;
    rdfs:isDefinedBy <http://purl.org/net/bel-epa/doacc> ;
    skos:prefLabel "pow"@en .

doacc:D28483031-b854-4853-9a35-e1daf97e4c59 a doacc:PoWscheme ;
    dc:description "SHA256 made difficult to parallelise via using leapfrog hashing"@en ;
    rdfs:isDefinedBy <http://purl.org/net/bel-epa/doacc> ;
    skos:prefLabel "dcrypt"@en .

doacc:D493eab2e-eeba-496d-afca-c9372c6efe9a a doacc:ProtectionScheme ;
    dc:description "Proof-of-Work plus Proof-of-Stake augmented by Proof-of-Burn"@en ;
    rdfs:isDefinedBy <http://purl.org/net/bel-epa/doacc> ;
    skos:prefLabel "pob"@en .

doacc:Dede0f611-3a23-4794-b768-0740933a5ff6 a doacc:Protocol ;
    dc:description "Bitcoin"@en ;
    rdfs:isDefinedBy <http://purl.org/net/bel-epa/doacc> ;
    skos:prefLabel "bitcoin"@en .
"""

blockprops = dict(
    bits="http://purl.org/net/bel-epa/ccy#bits",
    confirmations="http://purl.org/net/bel-epa/ccy#confirmations",
    difficulty="http://purl.org/net/bel-epa/ccy#difficulty",
    hash="http://purl.org/net/bel-epa/ccy#hash",
    headerhash="http://purl.org/net/bel-epa/ccy#headerhash",
    height="http://purl.org/net/bel-epa/ccy#height",
    merkleroot="http://purl.org/net/bel-epa/ccy#merkleroot",
    nextblockhash="http://purl.org/net/bel-epa/ccy#nextblockhash",
    nonce="http://purl.org/net/bel-epa/ccy#nonce",
    previousblockhash="http://purl.org/net/bel-epa/ccy#previousblockhash",
    size="http://purl.org/net/bel-epa/ccy#size",
    time="http://purl.org/net/bel-epa/ccy#time",
    version="http://purl.org/net/bel-epa/ccy#version",
    primechain="http://purl.org/net/bel-epa/ccy#primechain",
    primeorigin="http://purl.org/net/bel-epa/ccy#primeorigin",
    transition="http://purl.org/net/bel-epa/ccy#transition",
)


blockpropdata = dict(
    bits=XSD.hexBinary,
    confirmations=XSD.integer,
    difficulty=XSD.decimal,
    primechain=XSD.string,
    primeorigin=XSD.integer,
    hash=XSD.hexBinary,
    headerhash=XSD.hexBinary,
    height=XSD.integer,
    merkleroot=XSD.hexBinary,
    transition=XSD.decimal,
    nextblockhash=XSD.hexBinary,
    nonce=XSD.integer,
    previousblockhash=XSD.hexBinary,
    size=XSD.integer,
    time=XSD.integer,
    version=XSD.integer,
)

ccy_urif = "http://purl.org/net/bel-epa/ccy#C{}"
doacc_urif = "http://purl.org/net/bel-epa/doacc#D{}"
hexaPattern = re.compile(r'^([0-9a-fA-F]+)$')
CCY = Namespace("http://purl.org/net/bel-epa/ccy#")
DOACC = Namespace("http://purl.org/net/bel-epa/doacc#")


class TestNotifyCase(unittest.TestCase):
    def setUp(self):
        self.g = Graph()
        self.g.bind("", "http://purl.org/net/bel-epa/ccy#")
        self.g.bind("doacc", "http://purl.org/net/bel-epa/doacc#")
        self.g.bind("skos", "http://www.w3.org/2004/02/skos/core#")

    def setConn(self, network=None):
        self.ecoin = mainnet if network is None else network
        self.doacc = URIRef("http://purl.org/net/bel-epa/doacc#Dc74ed816-06ae-4b2a-b51a-3ac190810b1e")
        self.serverurl = 'http://{}:{}@localhost:{}/'.format(
            self.ecoin.get('rpcuser'), self.ecoin.get('rpcpass'), self.ecoin.get('rpcport'))
        self.amerpc = RPCHost(self.serverurl)

    def tearDown(self):
        pass

    # // ppcoin: the coin stake transaction is marked with the first output empty

    def dotxvi(self, txid, tx, txvi, txnode, s):
        txinnode = URIRef(ccy_urif.format(txid + '-I-' + str(s)))
        if debug:
            print("....")
            print(json.dumps(txvi, sort_keys=True, indent=2, separators=(',', ': ')))
            print("....")
        self.g.add((txinnode, RDF.type, CCY.TransactionInput))
        self.g.add((txnode, CCY.input, txinnode))
        if txvi.get('sequence') != 4294967295:
            self.g.add((txinnode, CCY.sequence, Literal(txvi.get('sequence'), datatype=XSD.integer)))
        if 'coinbase' in txvi:
            self.g.add((txinnode, CCY.coinbase, Literal(txvi.get('coinbase'), datatype=XSD.hexBinary)))
            # Link to address
            # g.add((anode, CCY.tx, tnode))
            # g.add((anode, CCY.txinput, txinnode))
        else:
            self.g.add((txinnode, CCY.txid, URIRef('C' + txvi.get('txid'))))
            self.g.add((txinnode, CCY.nvout, Literal(txvi.get('vout'), datatype=XSD.integer)))
            self.g.add((txinnode, CCY.ssasm, Literal(txvi.get('scriptSig').get('asm'), datatype=XSD.string)))
            # self.g.add((txinnode, CCY.sshex, Literal(txvi.get('scriptSig').get('hex'), datatype=XSD.hexBinary)))

    def dotxvo(self, txid, tx, txvo, txnode, s):
        txoutnode = URIRef(ccy_urif.format(txid + '-O-' + str(s)))
        self.g.add((txoutnode, RDF.type, CCY.TransactionOutput))
        self.g.add((txnode, CCY.output, txoutnode))
        self.g.add((txoutnode, CCY.n, Literal(txvo.get('n'), datatype=XSD.integer)))
        self.g.add((txoutnode, CCY.value, Literal(txvo.get('value'), datatype=XSD.decimal)))
        self.g.add((txoutnode, CCY.pkasm, Literal(txvo.get('scriptPubKey').get('asm'), datatype=XSD.string)))
        # self.g.add((txoutnode, CCY.pkhex, Literal(txvo.get('scriptPubKey').get('hex'), datatype=XSD.hexBinary)))
        if txvo.get('scriptPubKey').get('reqSigs', 1) != 1:
            self.g.add((txoutnode, CCY.reqSigs, Literal(txvo.get('scriptPubKey').get('reqSigs'), datatype=XSD.integer)))
        txvoseq = txvo.get('n')
        txvotype = txvo.get('scriptPubKey').get('type')
        self.g.add((txoutnode, CCY.type, Literal(txvotype, datatype=XSD.string)))
        if debug:
            print("----")
            print(json.dumps(txvo, sort_keys=True, indent=2, separators=(',', ': ')))
            print("----")
        if txvotype == "nulldata" and txvo.get('scriptPubKey').get('asm')[:9] == "OP_RETURN":
            msg = binascii.unhexlify(txvo.get('scriptPubKey').get('asm')[18:])
            if debug:
                print("----")
                print("Message: {}".format(msg))
                print(json.dumps(txvo, sort_keys=True, indent=2, separators=(',', ': ')))
            self.g.add((txoutnode, CCY.inscription, Literal(msg, datatype=XSD.string)))
        if txvotype not in ['nonstandard', 'nulldata']:
            for addr in txvo.get('scriptPubKey').get('addresses'):
                anode = URIRef(CCY[addr])
                self.g.add((anode, RDF.type, CCY.Address))
                self.g.add((txoutnode, CCY.address, anode))
                self.g.add((anode, CCY.tx, txnode))
                # self.g.add((anode, CCY.txoutput, txoutnode))

    def dogetrawtransaction(self, txid, nheight):
        txkeys = dict(
            hex=XSD.hexBinary,
            version=XSD.integer,
            time=XSD.integer,
            locktime=XSD.integer,
            confirmations=False,
            blocktime=XSD.dateTimeStamp)

        tx = self.amerpc.call('getrawtransaction', txid, 1)
        if debug:
            print(json.dumps(tx, sort_keys=True, indent=2, separators=(',', ': ')))
        txnode = URIRef(ccy_urif.format(txid))
        self.g.add((txnode, RDF.type, CCY.Transaction))

        for txk, dt in txkeys.items():
            if txk in ['blockhash']:
                self.g.add((txnode, CCY[txk], URIRef(ccy_urif.format(tx.get(txk)))))
            elif txk in ['confirmations', 'locktime', 'version', 'hex', 'blocktime']:
                pass
            # elif txk == 'IsBurnTx' and not tx.get(txk, False):
            #     pass
            elif txk == 'time':
                datestamp = int(datetime.fromtimestamp(tx.get(txk)).timestamp())
                self.g.add((txnode, CCY[txk], Literal(datestamp, datatype=dt)))
            else:
                self.g.add((txnode, CCY[txk.lower()], Literal(tx.get(txk), datatype=dt)))
        for txvi in tx.pop('vin', []):
            if txvi.get('sequence', 4294967295) == 4294967295:
                self.dotxvi(txid, tx, txvi, txnode, txvi.get('n', '0'))
            else:
                s = str(txvi.get('sequence', '0'))
                self.dotxvi(txid, tx, txvi, txnode, s)
        for s, txvo in enumerate(tx.pop('vout', [])):
            self.dotxvo(txid, tx, txvo, txnode, txvo.get('n'))

    def dobinfo(self):
        debug = False
        try:
            binfo = self.amerpc.call('getinfo')
            if debug:
                print(json.dumps(binfo, sort_keys=True, indent=2, separators=(',', ': ')))
        except Exception as e:
            raise Exception("{} getinfo failed for {}".format(e, self.ecoin))
        binfof = [
            "balance",
            "blocks",
            "connections",
            "difficulty",
            "errors",
            "ip",
            "keypoololdest",
            "keypoolsize",
            "moneysupply",
            "newmint",
            "paytxfee",
            "protocolversion",
            "proxy",
            "stake",
            "testnet",
            "version",
            "walletversion"
        ]
        return binfof, binfo

    def dobtime(self, bk):
        # Split off into separate method?
        try:
            btime = datetime.strptime(
                bk['time'], '%Y-%m-%d %H:%M:%S %Z')
        except:
            btime = datetime.fromtimestamp(bk['time'])
        return int(btime.timestamp())

    def getblockhash(self, nheight):
        debug = False
        try:
            bhash = self.amerpc.call('getblockhash', nheight)
            if debug:
                print(json.dumps(bhash, sort_keys=True, indent=2, separators=(',', ': ')))
            return bhash
        except Exception as e:
            raise Exception("{} getblockhash failed for {}".format(e, self.ecoin))

    def readblock(self, blockhash):
        block = URIRef(ccy_urif.format(str(blockhash)))
        self.g.add((block, RDF.type, CCY.Block))
        bk = self.amerpc.call('getblock', blockhash)
        if debug:
            print(json.dumps(bk, sort_keys=True, indent=2, separators=(',', ': ')))
        txs = bk.pop('tx', [])
        nheight = bk.get('height', 0)
        if nheight == 0:
            txs = txs[:2]

        for ks in blockfields:

            k = ks.lower()
            val = bk.get(ks)

            # Genesis block has no prevhash
            if val is None and k == 'previousblockhash':
                continue

            if val is None and k == 'nextblockhash':
                if self.binfo.get('blocks') == nheight:
                    continue
                else:
                    assert val is not None

            dt = blockpropdata.get(k)

            if k == 'height':
                self.g.add(
                    (block, URIRef(blockprops.get(k)),
                        Literal(nheight, datatype=dt)))
            elif k == 'time':
                self.g.add(
                    (block, URIRef(blockprops.get(k)),
                        Literal(self.dobtime(bk), datatype=dt)))
            elif k == 'difficulty':
                self.g.add(
                    (block, URIRef(blockprops.get(k)),
                        Literal(round(val, 8), datatype=dt)))
            elif k == 'previousblockhash':
                self.g.add(
                    (block, URIRef(blockprops.get(k)),
                        URIRef(CCY['C' + val])))
            elif k == 'nextblockhash' and val is not None:
                self.g.add(
                    (block, URIRef(blockprops.get(k)),
                        URIRef(CCY['C' + val])))
            elif k == 'version' and val == 1:
                pass
            else:
                try:
                    self.g.add(
                        (block, URIRef(blockprops.get(k)),
                            Literal(val, datatype=dt)))
                except Exception as e:
                    print("Ooops {} {}".format(e, k))
                    raise Exception(e)
        if nheight == 0:
            rawtx = "010000009d508653010000000000000000000000000000000000000000000000000000000000000000ffffffff0e049e5086530101062f503253482fffffffff01c07a8102000000002321038a52f85595a8d8e7c1d8c256baeee2c9ea7ad0bf7fe534575be4eb47cdbf18f6ac00000000"
        else:
            for txcnt, txid in enumerate(txs):
                self.dogetrawtransaction(txid, nheight)
