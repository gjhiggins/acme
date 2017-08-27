#! /usr/bin/env python3
import unittest
import os
import json
import subprocess
from rdflib import (URIRef, RDF) 
import blocknotifybase

global blockhash
debug = False
test = True
maxblocks = 10

sym = blocknotify.mainnet.get('symbol').lower()


class TestMainnetBlockNotify(blocknotifybase.TestNotifyCase):

    # @unittest.skip("Passed, skipping")
    def test_doreadblock(self):
        self.setConn(blocknotifybase.mainnet)
        self.blockchain = URIRef(blocknotifybase.ccy_urif.format(self.ecoin.get('genesis')[2:]))
        self.g.add((self.blockchain, RDF.type, blocknotifybase.CCY.BlockChain))
        self.g.add((self.blockchain, blocknotifybase.CCY.cryptocurrency, self.doacc))
        binfof, self.binfo = self.dobinfo()
        blockhash = os.environ.get('BLOCKHASH')
        if blockhash is not None:
            self.readblock(blockhash)
            if test:
                print(self.g.serialize(format="n3").decode('utf-8'))
            else:
                with open('/tmp/{s}.nt'.format(s=sym), 'w') as fp:
                    fp.write(self.g.serialize(format="nt").decode('utf-8'))
                subprocess.getstatusoutput(
                    "/opt/acme/fuseki2/bin/s-post http://localhost:3030/{s}chain/data default /tmp/{s}.nt".format(
                    s=sym))
                os.unlink("/tmp/{s}.nt".format(s=sym))


if __name__ == "__main__":
    unittest.main()
