#!/bin/bash
THIS_DIR=$(dirname $0)
ARGS=$@
if [[ -z $ARGS ]] ; then
    ARGS="$THIS_DIR/../src $THIS_DIR/"
fi

nosetests --with-doctest --doctest-extension=.rst --doctest-options=+NORMALIZE_WHITESPACE,+ELLIPSIS,+DONT_ACCEPT_TRUE_FOR_1,+IGNORE_EXCEPTION_DETAIL,+REPORT_NDIFF,+REPORT_ONLY_FIRST_FAILURE -v $ARGS
