#! /usr/bin/env python3
import unittest
import os
import json
import requests
import subprocess
from rdflib import (URIRef, RDF) 
import blocknotifybase

global blockhash
debug = False
test = True
maxblocks = 10

sym = blocknotifybase.testnet.get('symbol').lower()


class TestCatchUp(blocknotifybase.TestNotifyCase):

    # @unittest.skip("Passed, skipping")
    def test_catchup(self):

        qs = "/sparql?query=PREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F" + \
             "02%2F22-rdf-syntax-ns%23%3E%0ASELECT+%3Fsubject+%3Fheight+WHERE+%" + \
             "7B+%3Fsubject+rdf%3Atype+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fbel-epa" + \
             "%2Fccy%23Block%3E+.+%3Fsubject+%3Chttp%3A%2F%2Fpurl.org%2Fnet%2Fb" + \
             "el-epa%2Fccy%23height%3E+%3Fheight+%7D+ORDER+BY+DESC(%3Fheight)+LIMIT+1"
        query = blocknotifybase.testnet.get('endpoint') + '/' + blocknotifybase.testnet.get('dataset') + qs
        gblocks = int(
            json.loads(
                requests.get(query).content.decode('utf-8'))[
                    'results']['bindings'][0]['height']['value'])

        self.setConn(blocknotifybase.testnet)
        self.blockchain = URIRef(blocknotifybase.ccy_urif.format(self.ecoin.get('genesis')[2:]))
        self.g.add((self.blockchain, RDF.type, blocknotifybase.CCY.BlockChain))
        self.g.add((self.blockchain, blocknotifybase.CCY.cryptocurrency, self.doacc))
        self.binfof, self.binfo = self.dobinfo()

        for i in range(gblocks, self.binfo.get('blocks') + 1):
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
                "/opt/acme/fuseki2/bin/s-post http://localhost:3030/{s}tchain/data default /tmp/{s}t.nt".format(s=sym))
            os.unlink("/tmp/{s}t.nt".format(s=sym))

if __name__ == "__main__":
    unittest.main()
