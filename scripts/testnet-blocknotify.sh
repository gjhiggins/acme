#!/bin/bash
BLOCKHASH="$@" /opt/acme/datacoin-acme/bin/python3 /opt/acme/datacoin-acme/acme/scripts/testnet-blocknotify.py  > /opt/acme/log/dtct-blocknotify.log 2>&1
echo "${@}" >> /opt/acme/log/dtct-blocknotify.log

