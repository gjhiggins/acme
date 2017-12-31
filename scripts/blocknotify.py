#! /usr/bin/env python3
import unittest
import os
import subprocess
from rdflib import (URIRef, RDF) 
import blocknotifybase
import json
import requests

global blockhash
debug = False
test = False
maxblocks = 10

class TestMainnetBlockNotify(blocknotifybase.TestNotifyCase):

    # @unittest.skip("Passed, skipping")
    def test_doreadblock(self):
        # http://localhost:3030/dataset.html?tab=query&ds=/gapchain#query=prefix+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0A%0ASELECT+%3Fblock+%3Fheight%0AWHERE+%7B%0A%3Fblock+ccy%3Aheight+%3Fheight%0A%7D%0AORDER+BY+DESC(%3Fheight)+LIMIT+1
        sym = blocknotifybase.mainnet.get('symbol').lower()
        qs = """/sparql?query=prefix+ccy%3A+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa%2Fccy%23%3E%0A%0ASELECT+%3Fblock+%3Fheight%0AWHERE+%7B%0A%3Fblock+ccy%3Aheight+%3Fheight%0A%7D%0AORDER+BY+DESC(%3Fheight)+LIMIT+1"""
        query = "{}/{}{}".format(
            blocknotifybase.mainnet.get('endpoint'), blocknotifybase.mainnet.get('dataset'), qs)
        # print(query)
        res = json.loads(requests.get(query).content.decode('utf-8'))['results']['bindings'][0]
        gblocks = int(res['height']['value'])
        curheight = gblocks + 1
        lblockhash = res['block']['value'][len('http://purl.org/net/bel-epa/ccy#C'):]
        # print("Prevhash of block# {curheight} should be {lblockhash}".format(**locals()))
        self.setConn(blocknotifybase.mainnet)
        self.blockchain = URIRef(blocknotifybase.ccy_urif.format(self.ecoin.get('genesis')[2:]))
        self.g.add((self.blockchain, RDF.type, blocknotifybase.CCY.BlockChain))
        self.g.add((self.blockchain, blocknotifybase.CCY.cryptocurrency, self.doacc))
        binfof, self.binfo = self.dobinfo()
        blockhash = os.environ.get('BLOCKHASH')
        if blockhash is not None:
            bk = self.readblock(blockhash, as_dict=True)
            pblockhash = bk['previousblockhash']
            if pblockhash != lblockhash:
                print("New block's ({curheight}) previoushash {pblockhash} does not match graph's latestblock ({gblocks}) hash {lblockhash}.\nRe-synch required.".format(**locals()))
            else:
                self.readblock(blockhash)
            if test:
                print(self.g.serialize(format="n3").decode('utf-8'))
            else:
                with open('/tmp/{sym}-{blockhash}.nt'.format(**locals()), 'w') as fp:
                    fp.write(self.g.serialize(format="nt").decode('utf-8'))
                    fp.close()
                subprocess.getstatusoutput(
                    "/opt/acme/fuseki/bin/s-post http://localhost:3030/{sym}chain/data default /tmp/{sym}-{blockhash}.nt".format(
                        **locals()))
                # os.unlink("/tmp/{sym}-{hashblock}.nt".format(**locals()))


if __name__ == "__main__":
    unittest.main()
