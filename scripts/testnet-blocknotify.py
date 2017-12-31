#! /usr/bin/env python3
import unittest
import subprocess
import os
from rdflib import URIRef, RDF 
import blocknotifybase

global blockhash
debug = False
test = True

sym = blocknotifybase.testnet.get('symbol').lower()


class Test_TestnetBlockNotify(blocknotifybase.TestNotifyCase):

    # @unittest.skip("Passed, skipping")
    def test_doreadblock(self):
        self.setConn(blocknotifybase.testnet)
        self.blockchain = URIRef(blocknotifybase.ccy_urif.format(self.ecoin.get('genesis')[2:]))
        self.g.add((self.blockchain, RDF.type, blocknotifybase.CCY.BlockChain))
        self.g.add((self.blockchain, blocknotifybase.CCY.cryptocurrency, self.doacc))
        binfof, binfo = self.dobinfo()
        blockhash = os.environ.get(
            'BLOCKHASH',
            'cee5f695d016eda5137a820588ea1891eb107bb94daccff819849507e5bb17cc')
        # Process either a specific block or all blocks
        if blockhash is not None:
            self.readblock(blockhash)
        else:
            for i in range(1, binfo.get('blocks') + 1):
                blockhash = self.getblockhash(i)
                self.readblock(blockhash)

        if test:
            print(self.g.serialize(format="n3").decode('utf-8'))
        else:
            with open('/tmp/{s}t{h}.nt'.format(s=sym, h=blockhash), 'w') as fp:
                fp.write(self.g.serialize(format="nt").decode('utf-8'))
            subprocess.getstatusoutput(
                "/opt/acme/fuseki/bin/s-post http://localhost:3030/{s}tchain/data default /tmp/{s}t{h}.n3".format(
                    s=sym, h=blockhash))
            os.unlink('/tmp/{s}t{h}.nt'.format(s=sym, h=blockhash))

if __name__ == "__main__":
    unittest.main()
