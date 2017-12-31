#! /usr/bin/env python3
import unittest
from rdflib import RDF, URIRef, Graph
import copy
import blocknotifybase
import subprocess

global blockhash
debug = False
test = False
maxblocks = 99999999



class Test_BlockNotifyCatchUp(blocknotifybase.TestNotifyCase):
    # @unittest.skip("Passed, skipping")
    def test_catchup(self):
        sym = blocknotifybase.mainnet.get('symbol').lower()
        coin = blocknotifybase.mainnet.get('coin').lower()
        self.setConn(blocknotifybase.mainnet)
        self.binfof, self.binfo = self.dobinfo()
        self.blockchain = URIRef(blocknotifybase.ccy_urif.format(self.ecoin.get('genesis')[2:]))
        nblocks = self.binfo.get('blocks')
        for i in range(0, nblocks, 100000):
            self.g = Graph()
            self.g.bind("", "http://purl.org/net/bel-epa/ccy#")
            self.g.bind("doacc", "http://purl.org/net/bel-epa/doacc#")
            self.g.bind("skos", "http://www.w3.org/2004/02/skos/core#")
            if i == 0:
                self.g.add((self.blockchain, RDF.type, blocknotifybase.CCY.BlockChain))
                self.g.add((self.blockchain, blocknotifybase.CCY.cryptocurrency, self.doacc))
            for j in range(i, min(i + (nblocks - i), i + 100000)):
                if j % 10000 == 0:
                    print(j)
                blockhash = self.getblockhash(j)
                self.readblock(blockhash)

            if test:
                print(self.g.serialize(format="n3").decode('utf-8'))
            else:
                with open('/opt/acme/{coin}-acme/acme/data/{sym}-{i}.nt'.format(**locals()), 'w') as fp:
                    fp.write(self.g.serialize(format="nt").decode('utf-8'))
                subprocess.getstatusoutput(
                    "/opt/acme/fuseki/bin/s-post http://localhost:3030/{sym}chain/data default /tmp/{sym}-{i}.nt".format(**locals()))


if __name__ == "__main__":
    unittest.main()
