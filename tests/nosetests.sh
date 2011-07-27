#!/bin/bash
THIS_DIR=$(dirname $0)
ARGS=$@
if [[ -z $ARGS ]] ; then
    ARGS="$THIS_DIR/../src $THIS_DIR/"
fi

nosetests --with-doctest --doctest-extension=.rst -v $ARGS
