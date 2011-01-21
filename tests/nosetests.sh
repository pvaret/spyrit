#!/bin/bash
THIS_DIR=$(dirname $0)
nosetests --with-doctest --doctest-extension=.rst -v -w $THIS_DIR/..
