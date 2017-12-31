#!/bin/bash
LOG=/opt/acme/log/gap-blocknotify-catchup.log
pushd /opt/acme/gapcoin-acme/acme/scripts
/opt/acme/gapcoin-acme/bin/python3 testnet-blocknotify-catchup.py  > ${LOG} 2>&1
popd
