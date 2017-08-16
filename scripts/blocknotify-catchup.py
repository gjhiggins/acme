#! /usr/bin/env python3
import unittest
from rdflib import RDF, URIRef
import blocknotifybase

global blockhash
debug = False
test = True
maxblocks = 10

sym = blocknotifybase.mainnet.get('symbol').lower()


class TestCatchUp(blocknotifybase.TestNotifyCase):
    # @unittest.skip("Passed, skipping")
    def test_catchup(self):
        self.setConn(blocknotifybase.mainnet)
        self.blockchain = URIRef(blocknotifybase.ccy_urif.format(self.ecoin.get('genesis')[2:]))
        self.g.add((self.blockchain, RDF.type, blocknotifybase.CCY.BlockChain))
        self.g.add((self.blockchain, blocknotifybase.CCY.cryptocurrency, self.doacc))
        self.binfof, self.binfo = self.dobinfo()
        offset = 0
        for i in range(offset, min(maxblocks, self.binfo.get('blocks') + 1)):
            if i % 500 == 0:
                print(i)
            blockhash = self.getblockhash(i)
            self.readblock(blockhash)

        if test:
            print(self.g.serialize(format="n3").decode('utf-8'))
        else:
            with open('/tmp/{s}.nt'.format(s=sym), 'w') as fp:
                fp.write(self.g.serialize(format="nt").decode('utf-8'))
            subprocess.getstatusoutput(
                "/opt/acme/fuseki/bin/s-post http://localhost:3030/{s}chain/data default /tmp/{s}.nt".format(s=sym))
            os.unlink("/tmp/{s}.nt".format(s=sym))


if __name__ == "__main__":
    unittest.main()
