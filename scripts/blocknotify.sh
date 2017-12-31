#!/bin/bash
LOG=/opt/acme/log/gap-blocknotify.log
BLOCKHASH="$@" /opt/acme/gapcoin-acme/bin/python3 /opt/acme/gapcoin-acme/acme/scripts/blocknotify.py  >> ${LOG} 2>&1
echo "${@}" >> ${LOG}
