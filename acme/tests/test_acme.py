"""Tests of blockchain serialisation to RDF."""
import unittest
import json
import os
import requests
import time
import textwrap
from io import StringIO
from collections import OrderedDict
import datetime
from pyramid import testing
from pyramid.paster import get_appsettings
from pyramid.settings import asbool
from lxml import etree
# from jsonschema import validate
# from json_schema_generator.recorder import Recorder
from acme.lib.helpers import RPCHost


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
            result_list.append("{}<{}>".format(
                line_padding, tag_name.replace(' ', '_')))
            result_list.append(
                json2xml(sub_obj, "\t" + line_padding))
            result_list.append(
                "{}</{}>".format(
                    line_padding, tag_name.replace(' ', '_')))

        return "\n".join(result_list)

    return "{}{}".format(line_padding, json_obj)


class AcmeTests(unittest.TestCase):
    """Test Acme responses."""

    def setUp(self):
        """Setup."""
        self.config = testing.setUp()
        settings = {}
        settings['coins'] = {}
        for k, val in get_appsettings(
                '../../test.ini', name='main').items():
            if k.startswith('coins.'):
                d, c, v = k.split('.')
                try:
                    settings['coins'][c][v] = asbool(
                        val) if val in ['false', 'true'] else val
                except KeyError:
                    settings['coins'][c] = {}
                    settings['coins'][c][v] = asbool(
                        val) if val in ['false', 'true'] else val
        self.coin = settings['coins']['coin']
        self.rpcconn = RPCHost(
            'http://{rpcuser}:{rpcpass}@localhost:{rpcport}/'.format(
                rpcuser=self.coin.get('rpcuser', ''),
                rpcpass=self.coin.get('rpcpass', ''),
                rpcport=int(self.coin.get('testnetrpcport', '9999'))))

    def tearDown(self):
        """Teardown."""
        testing.tearDown()

    @unittest.skip("Passed, skipping")
    def test_populate_menu_selection(self):
        sparql = textwrap.dedent(
            "SELECT ?height ?dt"
            "WHERE {" 
            "  ?block <http://purl.org/net/bel-epa/ccy#height> ?height ."
            "  ?block <http://purl.org/net/bel-epa/ccy#time> ?dt .")
        sparqlfltr = "FILTER (?dt < {})"
        sparqlordr = "} ORDER BY DESC(?dt) LIMIT 1"
        for ym in [
              ["2017", ["01", "02", "03", "04", "05", "06", "07", "08"]],
              ["2016", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]],
              ["2015", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]],
              ["2014", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]],
              ["2013", ["10", "11", "12"]]]:
            y = ym[0]
            for m in ym[1]:
                tgt = int(datetime.datetime.strptime(
                    '{}-{}-01T00:00:00.000Z'.format(y, m),
                    '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
                print(sparql + sparqlfltr.format(tgt) + sparqlordr)

    # @unittest.skip("Passed, skipping")
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
                self.input = mmap.mmap(
                    file.fileno(), 0, access=mmap.ACCESS_READ)
                self.read_cursor = start

            def seek_file(self, position):
                self.read_cursor = position

            def close_file(self):
                self.input.close()

            def read_string(self):
                # Strings are encoded depending on length:
                # 0 to 252 :  1-byte-length followed by bytes (if any)
                # 253 to 65,535 : byte'253' 2-byte-length followed by bytes
                # 65,536 to 4,294,967,295 : byte '254' 4-byte-length followed
                # by bytes ... and the Bitcoin client is coded to understand:
                # greater than 4,294,967,295 : byte '255' 8-byte-length
                # followed by bytes of string ... but I don't think it
                # actually handles any strings that big.
                if self.input is None:
                    raise SerializationError(
                        "call write(bytes) before trying to deserialize")

                try:
                    length = self.read_compact_size()
                except IndexError:
                    raise SerializationError(
                        "attempt to read past end of buffer")

                return self.read_bytes(length)

            def write_string(self, string):
                # Length-encoded as with read-string
                self.write_compact_size(len(string))
                self.write(string)

            def read_bytes(self, length):
                try:
                    result = self.input[
                        self.read_cursor:self.read_cursor + length]
                    self.read_cursor += length
                    return result
                except IndexError:
                    raise SerializationError(
                        "attempt to read past end of buffer")

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
                    raise SerializationError(
                        "attempt to write size < 0")
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
                (i,) = struct.unpack_from(
                    format, self.input, self.read_cursor)
                self.read_cursor += struct.calcsize(format)
                return i

            def _write_num(self, format, num):
                s = struct.pack(format, num)
                self.write(s)

        def import_blkdat():
                pass

        ds = BCDataStream()
        fn = "/opt/acme/datacoin/.datadir/blocks/blk00000.dat"
        with open(fn, "rb") as file:
            ds.map_file(file, 0)

            # Read file
            # https://bitcoin.org/en/developer-reference#block-headers
            # https://en.bitcoin.it/wiki/Protocol_specification#block
            magic = ds.read_bytes(4).hex()
            block_size = int(struct.pack(
                '>l', *struct.unpack('<l', ds.read_bytes(4))).hex(), 16)
            version = struct.pack(
                '>l', *struct.unpack('<l', ds.read_bytes(4))).hex()
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

            print('magic: {} (da, dc, dd, ed)'.format(magic))
            print('block_size: {}'.format(block_size))
            print('version: {}'.format(version))
            print('prevhash: {}'.format(prev_header_hash))
            print('merkle_root: {}'.format(merkle_root_hash))
            print('timestamp: {} ({})'.format(
                int(timestamp, 16), datetime.datetime.fromtimestamp(
                    int(timestamp, 16)).isoformat()))
            print('nBits: {}'.format(nBits))
            print('nonce: {}'.format(int(nonce, 16)))

            print('----------------- Transaction Details: -----------------')
            print('num_of_transaction: {}'.format(int(num_of_transaction, 16)))
            print('tx_version: {}'.format(tx_version))
            print('tx_ntime: {} ({})'.format(
                int(tx_ntime, 16), datetime.datetime.fromtimestamp(
                    int(tx_ntime, 16)).isoformat()))
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
            print('lock_time: {} ({})'.format(
                int(timestamp, 16), datetime.datetime.fromtimestamp(
                    int(lock_time, 16)).isoformat()))

        ds.close_file()

    @unittest.skip("Passed, skipping")
    def test_sparqlemission(self):
        sym = self.coin.symbol.lower()
        testnet = False
        mainnetquery = \
            "http://localhost.com:3030/{}chain/sparql?query=PREFIX+ccy%3" + \
            "A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0ASE" + \
            "LECT+%3Fheight+%3Fdt%0AWHERE+%7B%0A++%3Fblock+ccy%3Aheight+" + \
            "%3Fheight+.%0A++%3Fblock+ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fd" + \
            "t+%3C+{timestamp})%0A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1""".format(sym)
        testnetquery = \
            "http://localhost:3030/{}tchain/sparql?query=PREFIX+ccy%3A+%3" + \
            "Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0ASELECT+" + \
            "%3Fheight+%3Fdt%0AWHERE+%7B%0A++%3Fblock+ccy%3Aheight+%3Fhei" + \
            "ght+.%0A++%3Fblock+ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{" + \
            "timestamp})%0A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1""".format(sym)
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
            # print('{}-{}-{}T00:00:00.000Z'.format(
            #     ptr.year, ptr.month, ptr.day))
            ts = int(datetime.datetime.strptime(
                '{}-{}-{}T00:00:00.000Z'.format(
                    ptr.year, ptr.month, ptr.day),
                '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
            # print(query.format(timestamp=ts))
            res = requests.get(
                query.format(timestamp=ts)).content.decode('utf-8')
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

        # template SPARQL query returning the block height of the next minted
        # block after {timestamp}
        querytmpl = \
            '''?query=PREFIX+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2F''' \
            '''bel-epa%2Fccy%23%3E%0ASELECT+%3Fheight+%3Fdt%0AWHERE+%''' \
            '''7B%0A++%3Fblock+ccy%3Aheight+%3Fheight+.%0A++%3Fblock+''' \
            '''ccy%3Atime+%3Fdt.+%0A++FILTER(%3Fdt+%3C+{timestamp})%0''' \
            '''A%7D%0AORDER+BY+DESC(%3Fdt)+LIMIT+1'''

        url = '''http://localhost:3030/{}/sparql'''.format(
            'slmtchain' if testnet else 'slmchain')

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
        testnet = True
        url = 'http://localhost:3030/slmtchain/sparql' if testnet \
            else 'http://localhost:3030/slmchain/sparql'
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
        with open('{}-daystats.csv'.format(
                'testnet' if testnet else 'mainnet'), 'w') as fp:
            for day in range(0, (datetime.date.today() - psz).days):
                # if day > 1:
                #     break
                fromdate = int(
                    datetime.datetime.strptime(
                        '{}-{}-{}T00:00:00.000Z'.format(
                            ptr.year, ptr.month, ptr.day),
                        '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
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
                    print("Day {}-{}, {}".format(
                        datetime.datetime.fromtimestamp(fromdate),
                        datetime.datetime.fromtimestamp(todate), e))
                    raise Exception(e)
            fp.close()
            # print(datum)


if __name__ == "__main__":
    unittest.main()
