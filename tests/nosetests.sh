#!/bin/bash
THIS_DIR=$(dirname $0)
nosetests --with-doctest --doctest-extension=.rst -v $THIS_DIR/../src $THIS_DIR/
