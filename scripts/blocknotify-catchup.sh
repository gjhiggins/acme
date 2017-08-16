#!/bin/bash
pushd /opt/acme/datacoin-acme/acme/scripts
/opt/acme/datacoin-acme/bin/python3 blocknotify-catchup.py
popd
