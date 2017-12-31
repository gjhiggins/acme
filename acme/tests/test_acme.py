"""Tests of blockchain serialisation to RDF."""
import unittest
import json
import os
import requests
import time
from io import StringIO
from collections import OrderedDict
import datetime
from pyramid import testing
from pyramid.paster import get_appsettings
from pyramid.settings import asbool
from lxml import etree
# from jsonschema import validate, exceptions
# from json_schema_generator.recorder import Recorder
from acme.lib.helpers import RPCHost
import psycopg2
import requests
import time
import blocknotifybase

global blockhash
debug = False
test = False

MAX_BLOCK_HEIGHT = None # The block number marking the end of the public ledger, -1 for “latest block”
# MAX_BLOCK_HEIGHT = 1000

blockattrs = [
  "adder",
  "chainwork",
  # "confirmations",
  "difficulty",
  "gapend",
  "gaplen",
  "gapstart",
  "hash",
  "height",
  "merit",
  "merkleroot",
  "nextblockhash",
  "nonce",
  "previousblockhash",
  "shift",
  "size",
  "time",
  # "version"
]


def json2xml(json_obj, line_padding=""):
    result_list = list()

    json_obj_type = type(json_obj)

    if json_obj_type is list:
        for sub_elem in json_obj:
            result_list.append(json2xml(sub_elem, line_padding))

        return "\n".join(result_list)

    if json_obj_type is dict:
        for tag_name in json_obj:
            sub_obj = json_obj[tag_name]
            result_list.append("{}<{}>".format(line_padding, tag_name.replace(' ', '_')))
            result_list.append(json2xml(sub_obj, "\t" + line_padding))
            result_list.append("{}</{}>".format(line_padding, tag_name.replace(' ', '_')))

        return "\n".join(result_list)

    return "{}{}".format(line_padding, json_obj)


class AcmeTests(unittest.TestCase):
    """Test Acme responses."""

    def setUp(self):
        """Setup."""
        self.config = testing.setUp()
        settings = {}
        settings['coins'] = {}
        for k, val in get_appsettings('../../test.ini', name='main').items():
            if k.startswith('coins.'):
                d, c, v = k.split('.')
                try:
                    settings['coins'][c][v] = asbool(val) if val in ['false', 'true'] else val
                except KeyError:
                    settings['coins'][c] = {}
                    settings['coins'][c][v] = asbool(val) if val in ['false', 'true'] else val
        self.coin = settings['coins'].get('coin')
        self.rpcconn = RPCHost(
            'http://{rpcuser}:{rpcpass}@localhost:{rpcport}/'.format(**locals()))

        # self.conn = psycopg2.connect(
        #     "dbname={} user={} password={}".format(
        #         self.ecoin.get('dbname')
        #         self.ecoin.get('dbuser')
        #         self.ecoin.get('dbpass')))

        # # Open a cursor to perform database operations
        # self.cursor = self.conn.cursor()

        # self.cursor.execute('''CREATE TABLE  IF NOT EXISTS blocks (
        #     adder integer,
        #     chainwork integer,
        #     difficulty number,
        #     gapend text,
        #     gaplen integer,
        #     gapstart text,
        #     height integer,
        #     merit number,
        #     shift integer,
        #     "time" integer
        #     )''')
        # self.cursor.execute('''CREATE INDEX IF NOT EXISTS merit_index ON blocks USING HASH (merit);''')
        # self.cursor.execute('''CREATE INDEX IF NOT EXISTS gaplen_index ON blocks USING HASH (gaplen);''')

    def tearDown(self):
        # self.cursor.execute('''DROP TABLE IF EXISTS blocks;''')
        # self.conn.commit()
        # self.conn.close()
        # os.unlink('gapcoin.db')
        testing.tearDown()

    @unittest.skip("Passed, skipping")
    def test_readblock(self):
        binfo = self.rpcconn.call('getinfo')
        last_block_in_db = self.cursor.execute('''select max(height) from blocks''').fetchone()[0] or 0
        blocknum = binfo['blocks'] if MAX_BLOCK_HEIGHT is None else MAX_BLOCK_HEIGHT
        if last_block_in_db < blocknum:
            print("Catching up from {} to {}".format(last_block_in_db, blocknum))
        for i in range(last_block_in_db + (1 if last_block_in_db > 0 else 0), blocknum):
            block = self.rpcconn.call('getblock', self.rpcconn.call('getblockhash', i))
            query = """insert into blocks (adder, chainwork, difficulty, gapend, gaplen, gapstart, height, merit, shift, time) VALUES ({adder}, {chainwork}, {difficulty}, '{gapend}', {gaplen}, '{gapstart}', {height}, {merit}, {shift}, {time})""".format(
                **block)
            self.cursor.execute(query)
            if i % 10000 == 0:
                print(i)
                self.conn.commit()
        self.conn.commit()

    @unittest.skip("Passed, skipping")
    def test_doreadblock(self):
        binfo = self.rpcconn.call('getinfo')
        last_block_in_db = self.cursor.execute('''select max(height) from blocks''').fetchone()[0] or 0
        blocknum = binfo['blocks'] if MAX_BLOCK_HEIGHT is None else MAX_BLOCK_HEIGHT
        if last_block_in_db < blocknum:
            print("Catching up from {} to {}".format(last_block_in_db, blocknum))
        for i in range(last_block_in_db + (1 if last_block_in_db > 0 else 0), blocknum):
            block = self.rpcconn.call('getblock', self.rpcconn.call('getblockhash', i))
            query = """insert into blocks (adder, chainwork, difficulty, gapend, gaplen, gapstart, height, merit, shift, time) VALUES ({adder}, {chainwork}, {difficulty}, '{gapend}', {gaplen}, '{gapstart}', {height}, {merit}, {shift}, {time})""".format(
                **block)
            self.cursor.execute(query)
        #     # FOR EACH TX
        #     for txid in block.get('tx'):
        #         tx = self.amerpc.call('decoderawtransaction', self.amerpc.call('getrawtransaction', txid))
        #         # SPENT TXS, REMOVE FROM UTXO SET
        #         for txin in tx.get('vin'):
        #             if "coinbase" not in txin.keys():
        #                 query = """delete from outputs where txhsh='{}' and seq={};""".format(
        #                         txin["txid"], txin["vout"])
        #                 self.cursor.execute(query)
        #         # UNSPENT TXS, ADD TO UTXO SET
        #         for txout in tx.get('vout'):
        #             scripttype = txout["scriptPubKey"]["type"]
        #             if scripttype in ["pubkeyhash", "pubkey", "scripthash"]:
        #                 query = "insert into outputs (bnum, tx, bhsh, txhsh, seq, addr, bal) " + \
        #                         "values ({}, '{}', '{}', '{}', {}, '{}', {});".format(
        #                             i, scripttype, block["hash"], txid, txout["n"],
        #                             txout["scriptPubKey"]["addresses"][0],
        #                             txout["value"])
        #                 self.cursor.execute(query)
        #             elif scripttype in ["nonstandard", "multisig"]:
        #                 query = "insert into outputs (bnum, tx, bhsh, txhsh, seq, addr, bal) " + \
        #                         "values ({}, '{}', '{}', '{}', {}, '** {} **', {});".format(
        #                             i, scripttype, block["hash"], txid, txout["n"],
        #                             scripttype, txout["value"])
        #                 self.cursor.execute(query)
        #             else:
        #                 raise Exception(
        #                     "Don't know how to handle {} scripts in transaction {}".format(
        #                         scripttype, txid))
            if i % 10000 == 0:
                print(i)
                self.conn.commit()
        self.conn.commit()

    @unittest.skip("Passed, skipping")
    def test_basic_api(self):
        # Test blockinfo schema
        binfo = self.rpcconn.call('getrawtransaction', '007e7020acbdafcce9f044c0a6bf66b3d7e194f4fc86efb5e12be06bb28c545e', 1)
        print(json.dumps(binfo, sort_keys=True, indent=2, separators=(',', ': ')))

    @unittest.skip("Passed, skipping")
    def test_populate_menu_selection(self):
        sparql = """SELECT ?height ?dt WHERE { ?block <http://purl.org/net/bel-epa/ccy#height> ?height . ?block <http://purl.org/net/bel-epa/ccy#time> ?dt. """
        sparqlfltr = """FILTER (?dt < {})"""
        sparqlordr = """} ORDER BY DESC(?dt) LIMIT 1"""
        for ym in [
              ["2017", ["01", "02", "03", "04"]],
              ["2016", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]],
              ["2015", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]],
              ["2014", ["05", "06", "07", "08", "09", "10", "11", "12"]]]:
            y = ym[0]
            for m in ym[1]:
                tgt = int(datetime.datetime.strptime('{}-{}-01T00:00:00.000Z'.format(y, m), '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
                print(sparql + sparqlfltr.format(tgt) + sparqlordr)

    @unittest.skip("Passed, skipping")
    def test_extract_genesis_tx(self):
        import struct  # convert between Python values and C structsrepresented as Python strings
        try:
            import StringIO  # Reads and writes a string buffer
        except ImportError:
            from io import StringIO 
        import mmap  # mutable string
        from binascii import unhexlify, hexlify

        class BCDataStream(object):
            def __init__(self):
                self.input = None
                self.read_cursor = 0

            def clear(self):
                self.input = None
                self.read_cursor = 0

            def write(self, bytes):  # Initialize with string of bytes
                if self.input is None:
                    self.input = bytes
                else:
                    self.input += bytes

            def map_file(self, file, start):  # Initialize with bytes from file
                self.input = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
                self.read_cursor = start

            def seek_file(self, position):
                self.read_cursor = position

            def close_file(self):
                self.input.close()

            def read_string(self):
                # Strings are encoded depending on length:
                # 0 to 252 :  1-byte-length followed by bytes (if any)
                # 253 to 65,535 : byte'253' 2-byte-length followed by bytes
                # 65,536 to 4,294,967,295 : byte '254' 4-byte-length followed by bytes
                # ... and the Bitcoin client is coded to understand:
                # greater than 4,294,967,295 : byte '255' 8-byte-length followed by bytes of string
                # ... but I don't think it actually handles any strings that big.
                if self.input is None:
                    raise SerializationError("call write(bytes) before trying to deserialize")

                try:
                    length = self.read_compact_size()
                except IndexError:
                    raise SerializationError("attempt to read past end of buffer")

                return self.read_bytes(length)

            def write_string(self, string):
                # Length-encoded as with read-string
                self.write_compact_size(len(string))
                self.write(string)

            def read_bytes(self, length):
                try:
                    result = self.input[self.read_cursor:self.read_cursor + length]
                    self.read_cursor += length
                    return result
                except IndexError:
                    raise SerializationError("attempt to read past end of buffer")

                return ''

            def read_boolean(self):
                return self.read_bytes(1)[0] != chr(0)

            def read_int16(self):
                return self._read_num('>h')

            def read_uint16(self):
                return self._read_num('>H')

            def read_int32(self):
                return self._read_num('>i')

            def read_uint32(self):
                return self._read_num('>I')

            def read_int64(self):
                return self._read_num('>q')

            def read_uint64(self):
                return self._read_num('>Q')

            def write_boolean(self, val):
                return self.write(chr(1) if val else chr(0))

            def write_int16(self, val):
                return self._write_num('>h', val)

            def write_uint16(self, val):
                return self._write_num('>H', val)

            def write_int32(self, val):
                return self._write_num('>i', val)

            def write_uint32(self, val):
                return self._write_num('>I', val)

            def write_int64(self, val):
                return self._write_num('>q', val)

            def write_uint64(self, val):
                return self._write_num('>Q', val)

            def read_compact_size(self):
                size = ord(self.input[self.read_cursor])
                self.read_cursor += 1
                if size == 253:
                    size = self._read_num('>H')
                elif size == 254:
                    size = self._read_num('>I')
                elif size == 255:
                    size = self._read_num('>Q')
                return size

            def write_compact_size(self, size):
                if size < 0:
                    raise SerializationError("attempt to write size < 0")
                elif size < 253:
                    self.write(chr(size))
                elif size < 2**16:
                    self.write('\xfd')
                    self._write_num('>H', size)
                elif size < 2**32:
                    self.write('\xfe')
                    self._write_num('>I', size)
                elif size < 2**64:
                    self.write('\xff')
                    self._write_num('>Q', size)

            def _read_num(self, format):
                (i,) = struct.unpack_from(format, self.input, self.read_cursor)
                self.read_cursor += struct.calcsize(format)
                return i

            def _write_num(self, format, num):
                s = struct.pack(format, num)
                self.write(s)

        def import_blkdat():
                pass

        ds = BCDataStream()
        with open("/home/user/.coin/blocks/blk00000.dat", "rb") as file:
            ds.map_file(file, 0)

            # Read file
            # https://bitcoin.org/en/developer-reference#block-headers
            # https://en.bitcoin.it/wiki/Protocol_specification#block
            magic = ds.read_bytes(4).hex()
            block_size = int(struct.pack('>l', *struct.unpack('<l', ds.read_bytes(4))).hex(), 16)
            version = struct.pack('>l', *struct.unpack('<l', ds.read_bytes(4))).hex()
            prev_header_hash = ds.read_bytes(32)[::-1].hex()
            merkle_root_hash = ds.read_bytes(32)[::-1].hex()
            timestamp = ds.read_bytes(4)[::-1].hex()
            nBits = ds.read_bytes(4)[::-1].hex()
            nonce = ds.read_bytes(4)[::-1].hex()

            num_of_transaction = ds.read_bytes(1)[::-1].hex()
            tx_version = ds.read_bytes(4)[::-1].hex()
            tx_ntime = ds.read_bytes(4)[::-1].hex()
            tx_input = ds.read_bytes(1)[::-1].hex()
            tx_prev_output_hash = ds.read_bytes(32)[::-1].hex()
            tx_prev_output_num = ds.read_bytes(4)[::-1].hex()
            script_length = ds.read_bytes(1)[::-1].hex()
            scriptsig = ds.read_bytes(int((script_length), 16)).hex()
            dunno = ds.read_bytes(1)[::-1].hex()
            sequence = ds.read_bytes(4)[::-1].hex()
            tx_output = ds.read_bytes(1)[::-1].hex()
            BTC_num = ds.read_bytes(8)[::-1].hex()
            pk_script_len = ds.read_bytes(1)[::-1].hex()
            pk_script = ds.read_bytes(int(pk_script_len, 16))[::-1].hex()
            lock_time = ds.read_bytes(4)[::-1].hex()

            print('magic: {} (6e, 8b, 92, a5)'.format(magic))
            print('block_size: {}'.format(block_size))
            print('version: {}'.format(version))
            print('prevhash: {}'.format(prev_header_hash))
            print('merkle_root: {}'.format(merkle_root_hash))
            print('timestamp: {} ({})'.format(int(timestamp, 16), datetime.datetime.fromtimestamp(int(timestamp, 16)).isoformat()))
            print('nBits: {}'.format(nBits))
            print('nonce: {}'.format(int(nonce, 16)))

            print('--------------------- Transaction Details: ---------------------')
            print('num_of_transaction: {}'.format(int(num_of_transaction, 16)))
            print('tx_version: {}'.format(tx_version))
            print('tx_ntime: {} ({})'.format(int(tx_ntime, 16), datetime.datetime.fromtimestamp(int(tx_ntime, 16)).isoformat()))
            print('tx_input_num: {}'.format(int(tx_input, 16)))
            print('tx_prev_output_hash: {}'.format(tx_prev_output_hash))
            print('tx_prev_output_num: {}'.format(tx_prev_output_num))
            print('script_length: {}'.format(int(script_length, 16)))
            print('scriptsig: {}'.format(scriptsig))
            print('dunno: {}'.format(dunno))
            print('sequence: {}'.format(sequence))
            print('tx_output_num: {}'.format(tx_output))
            print('BTC_num: {}'.format(BTC_num))
            print('pk_script_len: {}'.format(pk_script_len))
            print('pk_script: {}'.format(pk_script))
            print('lock_time: {}'.format(lock_time))
            print('lock_time: {} ({})'.format(int(timestamp, 16), datetime.datetime.fromtimestamp(int(lock_time, 16)).isoformat()))

        ds.close_file()

    @unittest.skip("Passed, skipping")
    def test_schema(self):
        """Test schemas."""
        forreal = True
        newuns = 0
        schemas = {}
        txschemas = {}
        for i in ['getinfo', 'getblock', 'getrawtransaction']:
            with open(os.getcwd() + '/schemas/{}_schema.json'.format(i)) as fp:
                schemas[i] = json.loads(fp.read())
            fp.close()

        d = [x for x in os.listdir(os.getcwd() + '/schemas/getrawtransaction') if 'schema' in x]
        for j in d:
            with open(os.getcwd() + '/schemas/getrawtransaction/{}'.format(j)) as fp:
                txschemas[j] = json.loads(fp.read())
            fp.close()

        # Test blockinfo schema
        binfo = self.rpcconn.call('getinfo')
        if forreal:
            validate(binfo, schemas['getinfo'])

        for nheight in range(1, binfo.get('blocks') + 1):
            if nheight % 500 == 0:
                print(nheight)
            print(nheight)
            blockhash = self.rpcconn.call('getblockhash', nheight)
            block = self.rpcconn.call('getblock', blockhash)
            if forreal:
                try:
                    validate(block, schemas['getblock'])
                except exceptions.ValidationError as e:
                    raise Exception("{} {}".format(e, block))
            for tx in block['tx']:
                transaction = self.rpcconn.call('getrawtransaction', tx, 1)
                if forreal:
                    validated = False
                    try:
                        xmltr = StringIO(
                            '<?xml version="1.0"?>\n'
                            '<transaction>\n{}\n</transaction>\n'.format(
                                json2xml(transaction)))
                        with open(os.getcwd() + '/schemas/transaction.rng', 'r') as fp:
                            relaxng_doc = etree.parse(fp)
                        relaxng = etree.RelaxNG(relaxng_doc)
                        try:
                            doc = etree.parse(xmltr)
                        except Exception as e:
                            print(xmltr.read())
                            raise Exception(e)
                        try:
                            relaxng.assertValid(doc)
                        except Exception as e:
                            print("{} {}".format(e, xmltr.read()))
                            raise Exception(e)
                        # validate(transaction, schemas['getrawtransaction'])
                    except exceptions.ValidationError as e:
                        print(json2xml(transaction))
                        # for label, schema in txschemas.items():
                        #     try:
                        #         validate(transaction, schema)
                        #         validated = True
                        #         break
                        #     except exceptions.ValidationError as e:
                        #         pass
                        # if not validated:
                        #     with open(os.getcwd() + '/schemas/getrawtransaction/{}.json'.format(newuns), 'wb') as fp:
                        #         fp.write(json.dumps(transaction, sort_keys=True, indent=2, separators=(',', ': ')).encode('utf-8'))
                        #     fp.close()
                        #     res = Recorder.from_string(json.dumps(transaction))
                        #     res.save_json_schema(os.getcwd() + '/schemas/getrawtransaction/{}_schema.json'.format(newuns), indent=4)
                        #     # schemas['getblock']
                        #     newuns += 1

    @unittest.skip("Passed, skipping")
    def test_fixup(self):
        """Test schemas."""
        schemas = {}
        for i in ['getinfo', 'getblock', 'getrawtransaction']:
            with open(os.getcwd() + '/schemas/{}_schema.json'.format(i)) as fp:
                schemas[i] = json.loads(fp.read())
            fp.close()

        txid = "be151c377da175c2a06e8d8e103575e27440c9819258a92dc80753d144d93019"
        tx = self.rpcconn.call('getrawtransaction', txid, 1)
        # validate(block, schemas['getrawtransaction'])
        try:
            validate(tx, schemas['getrawtransaction'])
        except exceptions.ValidationError as e:
            with open(os.getcwd() + '/schemas/getrawtransaction_no_coinbase.json', 'wb') as fp:
                fp.write(json.dumps(tx, sort_keys=True, indent=2, separators=(',', ': ')).encode('utf-8'))
            fp.close()
            res = Recorder.from_string(json.dumps(tx))
            res.save_json_schema(os.getcwd() + '/schemas/getrawtransaction_no_coinbase.json', indent=4)
            # schemas['getblock']

    @unittest.skip("Passed, skipping")
    def test_sparqlemission(self):
        sym = self.coin.symbol.lower()
        testnet = False
        mainnetquery = """http://localhost.com:3030/{}chain/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1""".format(sym)
        testnetquery = """http://localhost:3030/{}tchain/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1""".format(sym)
        if testnet:
            query = testnetquery
            psz = datetime.date(year=2017, month=4, day=15)
        else:
            query = mainnetquery
            psz = datetime.date(year=2014, month=5, day=28)
        ptr = psz
        nextday = datetime.timedelta(days=1)
        for day in range(0, (datetime.date.today() - psz).days):
            # if day > 1:
            #     break
            if day % 100 == 0:
                print(day)
            ptr += nextday
            # print('{}-{}-{}T00:00:00.000Z'.format(ptr.year, ptr.month, ptr.day))
            ts = int(datetime.datetime.strptime('{}-{}-{}T00:00:00.000Z'.format(ptr.year, ptr.month, ptr.day), '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
            # print(query.format(timestamp=ts))
            res = requests.get(query.format(timestamp=ts)).content.decode('utf-8')
            # print(res)
            resd = json.loads(res)
            height = resd['results']['bindings'][0]['height']['value']
            bdate = resd['results']['bindings'][0]['dt']['value']
            datum = '''"{t}",{h},{d}\n'''.format(t=ptr, h=height, d=bdate)
            with open('emissions.csv', 'a') as fp:
                fp.write(datum)
            fp.close()
            # print(datum)

    @unittest.skip("Passed, skipping")
    def test_get_emissions(self):
        # unittests already imported
        import json
        import requests
        import datetime

        # switch endpoint
        testnet = True
        testnetflag = 't'
        endpoint = self.coin['endpoint']
        sym = self.coin['symbol'].lower()

        # template SPARQL query returning the block height of the next minted
        # block after {timestamp}
        querytmpl = \
            '''?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2F''' \
            '''bel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%''' \
            '''7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+''' \
            '''ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0''' \
            '''A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1'''

        url = '''{endpoint}/{sym}{testnetflag}chain/sparql'''.format(**locals())

        # Initialise the starting date
        ptr = psz = datetime.date(year=2017, month=4, day=15) if testnet \
            else datetime.date(year=2014, month=5, day=28)

        # Create a day incrementer
        nextday = datetime.timedelta(days=1)

        # Save results in comma-separated format
        with open('/tmp/{}-emissions.csv'.format(
                'testnet' if testnet else 'mainnet'), 'w') as fp:

            # create day range to drive iteration
            for day in range(0, (datetime.date.today() - psz).days):

                # Blurt progress
                if day % 100 == 0:
                    print(day)

                # Increment the date pointer by one day
                ptr += nextday

                # Create timestamp from date pointer
                ts = int(datetime.datetime.strptime(
                    '{}-{}-{}T00:00:00.000Z'.format(
                        ptr.year, ptr.month, ptr.day),
                    '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())

                # Execute the SPARQL query
                res = requests.get(url + querytmpl.format(
                    timestamp=ts)
                ).content.decode('utf-8')

                # Marshal and persist the results for the given day
                resd = json.loads(res)
                height = resd['results']['bindings'][0]['height']['value']
                bdate = resd['results']['bindings'][0]['dt']['value']
                datum = '''"{t}",{h},{d}\n'''.format(t=ptr, h=height, d=bdate)
                fp.write(datum)
        fp.close()

    @unittest.skip("Passed, skipping")
    def test_sparqldaystats(self):
        sym = self.coin['symbol'].lower()
        endpoint = self.coin['endpoint']
        testnet = True
        testnetflag = 't'
        sym = self.coin.symbol.lower()
        url = '{endpoint}/{sym}{testnetflag}chain/sparql'.format(**locals)
        query = \
            '?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2F' \
            'ccy%23%3E%0A%23+SELECT+%3Fblock+%3Fheight+WHERE+%7B+%3Fblock+ccy%3' \
            'Aheight+%3Fheight+%7D+ORDER+BY+DESC(%3Fheight)+LIMIT+1%0ASELECT+%3' \
            'Fheight+%3Fdt+%3Fmint+%3Fdiff+%3Fflags+WHERE+%7B%0A++++%3Fblock+cc' \
            'y%3Aheight+%3Fheight+.%0A++++%3Fblock+ccy%3Atime+%3Fdt+.%0A++++%3F' \
            'block+ccy%3Amint+%3Fmint+.%0A++++%3Fblock+ccy%3Adifficulty+%3Fdiff' \
            '+.%0A++++%3Fblock+ccy%3Aflags+%3Fflags+.%0A++FILTER+((%3Fdt+%3E+{f' \
            'romdate})+%26%26+(%3Fdt+%3C+{todate}))%0A%7D+ORDER+BY+ASC(%3Fdt)%0A'
        ptr = psz = datetime.date(year=2017, month=4, day=15) if testnet \
            else datetime.date(year=2014, month=5, day=28)
        nextday = datetime.timedelta(days=1)
        with open('{sym}{testnetflag}-daystats.csv'.format(**locals()), 'w') as fp:
            for day in range(0, (datetime.date.today() - psz).days):
                # if day > 1:
                #     break
                fromdate = int(datetime.datetime.strptime('{}-{}-{}T00:00:00.000Z'.format(
                    ptr.year, ptr.month, ptr.day), '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
                # print('{}-{}-{}T00:00:00.000Z'.format(ptr.year, ptr.month, ptr.day))
                ptr += nextday
                todate = int(datetime.datetime.strptime(
                    '{}-{}-{}T00:00:00.000Z'.format(
                        ptr.year, ptr.month, ptr.day),
                    '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
                # print(query.format(timestamp=ts))
                res = requests.get(url + query.format(
                    fromdate=fromdate, todate=todate)
                ).content.decode('utf-8')
                print(res)
                resd = json.loads(res)
                try:
                    height = resd['results']['bindings'][0]['height']['value']
                    bdate = resd['results']['bindings'][0]['dt']['value']
                    mint = resd['results']['bindings'][0]['mint']['value']
                    diff = resd['results']['bindings'][0]['diff']['value']
                    flags = resd['results']['bindings'][0]['flags']['value']
                    datum = '{b}\t{h}\t{t}\t{m}\t{d}\t{f}\n'.format(
                        b=bdate, h=height, t=ptr, m=mint, d=diff, f=flags)
                    fp.write(datum)
                except Exception as e:
                    print("Day {}-{}, {}".format(datetime.datetime.fromtimestamp(fromdate), datetime.datetime.fromtimestamp(todate), e))
                    raise Exception(e)
            fp.close()
            # print(datum)

    @unittest.skip("Passed, skipping")
    def test_cmcap(self):
        import csv
        with open('cmcap.csv', newline='') as csvfile:
            datareader = csv.reader(csvfile, delimiter=',', quotechar='"')
            data = [dict(
                date=int(datetime.datetime.strptime(row[0], "%b %d %Y").timestamp()),
                open=row[1],
                high=row[2],
                low=row[3],
                close=row[4],
                marketcap=row[5]) 
                    for row in list(datareader)[1:]]
        print(data)

    @unittest.skip("Passed, skipping")
    def test_cmcapblocks(self):
        sym = self.coin['symbol'].lower()
        endpoint = self.coin['endpoint']
        testnet = False
        testnetflag = ''
        mainnetquery = """{endpoint}/{sym}{testnetflag}chain/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1"""
        testnetquery = """{endpoint}/{sym}{testnetflag}chain/sparql?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1"""
        if testnet:
            query = testnetquery
        else:
            query = mainnetquery
        with open('cmcap.csv', 'r') as fp:
            csv = [d.split(',') for d in fp.read().split('\n')][1:]
        for dt in csv[:1]:
            ts = int(dt[0])
            res = requests.get(query.format(timestamp=ts)).content.decode('utf-8')
            # print(res)
            resd = json.loads(res)
            height = resd['results']['bindings'][0]['height']['value']
            bdate = resd['results']['bindings'][0]['dt']['value']
            datum = '''{h},{d}\n'''.format(h=height, d=bdate)
            # with open('emissions.csv', 'a') as fp:
            #     fp.write(datum)
            # fp.close()
            print(datum)

    @unittest.skip("Passed, skipping")
    def test_activitystreams(self):
        from lxml import etree
        with open('data.html', 'r') as fp:
            html = fp.read()
        fp.close()
        root = etree.HTML(html)
        examples = root.xpath('//div[@class="example"]')
        for example in examples:
            title = ''.join(example.xpath('./div[@class="example-title marker"]/span/text()'))
            content = example.xpath('string()').strip()
            titlend = content.find('\n')
            title = content[:titlend]
            content = content[titlend:].strip()
            print('{} = """{}"""\n'.format(title.lower().replace(' ', ''), content))

    @unittest.skip("Passed, skipping")
    def test_asread(self):
        from examples import examples
        from rdflib import Graph
        g = Graph()
        for label, example in examples.items():
            g1 = Graph()
            try:
                g1.parse(data=example, format="json-ld")
                g += g1
            except Exception as e:
                print(label)
            del g1
        print(g.serialize(format="n3").decode('utf-8'))

    @unittest.skip("Passed, skipping")
    def test_graph_hash(self):
        from rdflib import Namespace, Literal, URIRef, BNode
        from rdflib.graph import Graph, ConjunctiveGraph
        from rdflib.plugins.memory import IOMemory
        from rdflib.compare import to_isomorphic, _TripleCanonicalizer


        ns = Namespace("http://love.com#")

        mary = BNode()
        john = URIRef("http://love.com/lovers/john#")

        cmary = URIRef("http://love.com/lovers/mary#")
        cjohn = URIRef("http://love.com/lovers/john#")

        store = IOMemory()

        g = ConjunctiveGraph(store=store)
        g.bind("love",ns)

        gmary = Graph(store=store, identifier=cmary)

        gmary.add((mary, ns['hasName'], Literal("Mary")))
        gmary.add((mary, ns['loves'], john))

        gjohn = Graph(store=store, identifier=cjohn)
        gjohn.add((john, ns['hasName'], Literal("John")))

        print("The internal hash of an named graph is the same as the internal hash of the Conjunctive graph: " +
              str(to_isomorphic(g).internal_hash() == to_isomorphic(gmary).internal_hash()) + "\n")

        # Prints to 'True'

        print("The internal hash of an named graph is the same as the internal hash of the Conjunctive graph: " +
              str(_TripleCanonicalizer(g).to_hash() == _TripleCanonicalizer(gmary).to_hash()))

        # Prints to 'False'


        # Example how I think to proove the signature of signed graphs:
        for h in g.objects(mary_public_keys, wot.signed):
            # First verify the signature
            if gpg.verify(str(h)):
                # Second compare hash
                sigHash = gpg.decrypt(h).data.decode("utf-8").strip() # gpg.decrypt(h): bytes --> string
                
                identifier = str(g.value(h, RDFS.label))
                signedG = g.get_context(identifier)
                realHash = str(to_isomorphic(signedG).internal_hash())  # Gives the wrong hash?
                                                                        # (Whath happens with two existing equal identifiers/contexts?)
                print(sigHash)
                print(realHash)
                
                if sigHash == realHash:
                    print("Graph verified")
                
                else:
                    print("Signature verified but graph has changed")
            
            else:
                print("Signature verification failed")



if __name__ == "__main__":
    unittest.main()


"""
PREFIX ccy: <http://purl.org/net/bel-epa/ccy#>
SELECT ?tx ?bh ?txo ?dt ?asm
WHERE {
  ?tx ccy:output ?txo .
  ?txo ccy:pkasm ?asm .
    { SELECT ?bh ?dt WHERE {
        ?tx ccy:blockhash ?bh .
        ?tx ccy:time ?dt. }
    LIMIT 1 } . 
    FILTER regex(?asm, "OP_RETURN")
} ORDER BY DESC(?dt)

SELECT ?tx ?bh ?txo ?dt ?asm
WHERE {
  ?tx ccy:output ?txo .
  ?txo ccy:pkasm ?asm .
#  { SELECT DISTINCT ?bh ?dt WHERE {
#        ?tx ccy:blockhash ?bh .
#        ?tx ccy:time ?dt. }
#    LIMIT 1 } . 
  ?tx ccy:blockhash ?bh .
  ?tx ccy:time ?dt .
  FILTER regex(?asm, "OP_RETURN")
} ORDER BY DESC(?dt)
"""
