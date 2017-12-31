#!/bin/bash
LOG=/opt/acme/log/gap-testnet-blocknotify.log
# BLOCKHASH="$@" /opt/acme/gapcoin-acme/bin/python3 /opt/acme/gapcoin-acme/acme/scripts/testnet-blocknotify.py  >> ${LOG} 2>&1
echo "${@}" >> ${LOG}
