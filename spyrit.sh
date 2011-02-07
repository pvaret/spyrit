#!/bin/bash

_THIS_DIR=$(dirname $0)
_OLD_DIR=$(pwd)

cd $_THIS_DIR/src/resources/
python mkresources.py
cd $_OLD_DIR
cd $_THIS_DIR/src
python spyrit.py
cd $_OLD_DIR
