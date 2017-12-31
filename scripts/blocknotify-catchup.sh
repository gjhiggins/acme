#!/bin/bash
pushd /opt/acme/gapcoin-acme/acme/scripts
/opt/acme/gapcoin-acme/bin/python3 blocknotify-catchup.py
popd
