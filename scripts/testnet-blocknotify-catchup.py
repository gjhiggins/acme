#! /usr/bin/env python3
import unittest
import subprocess
import os
from rdflib import URIRef, RDF 
import blocknotifybase

global blockhash
debug = False
test = False
maxblocks = 999999999

sym = blocknotifybase.testnet.get('symbol').lower()

class TestCatchUp(blocknotifybase.TestNotifyCase):

    # @unittest.skip("Passed, skipping")
    def test_catchup(self):
        self.setConn(blocknotifybase.testnet)
        self.blockchain = URIRef(blocknotifybase.ccy_urif.format(self.ecoin.get('genesis')[2:]))
        self.g.add((self.blockchain, RDF.type, blocknotifybase.CCY.BlockChain))
        self.g.add((self.blockchain, blocknotifybase.CCY.cryptocurrency, self.doacc))
        self.binfof, self.binfo = self.dobinfo()

        for i in range(1, min(maxblocks, self.binfo.get('blocks') + 1)):
            if i % 500 == 0:
                print(i)
            blockhash = self.getblockhash(i)
            self.readblock(blockhash)

        if test:
            print(self.g.serialize(format="n3").decode('utf-8'))
        else:
            with open('/tmp/{s}t.nt'.format(s=sym), 'w') as fp:
                fp.write(self.g.serialize(format="nt").decode('utf-8'))
            fp.close()
            subprocess.getstatusoutput(
                "/opt/acme/fuseki/bin/s-post http://localhost:3030/{s}tchain/data default /tmp/{s}t.nt".format(s=sym))
            os.unlink("/tmp/{s}t.nt".format(s=sym))

if __name__ == "__main__":
    unittest.main()
