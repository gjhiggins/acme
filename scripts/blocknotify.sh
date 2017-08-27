#!/bin/bash
BLOCKHASH="$@" /opt/acme/datacoin-acme/bin/python3 /opt/acme/datacoin-acme/acme/scripts/blocknotify.py  > /opt/acme/log/dtc-blocknotify.log 2>&1
echo "${@}" >> /opt/acme/log/dtc-blocknotify.log

