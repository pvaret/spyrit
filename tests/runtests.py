#!/usr/bin/python
## -*- coding: utf-8 -*-

import os
import sys
import doctest

THIS_DIR   = os.path.dirname( __file__ )
SPYRIT_DIR = os.path.join( THIS_DIR, os.path.pardir )

sys.path.append( SPYRIT_DIR )

OPTIONS = doctest.NORMALIZE_WHITESPACE \
        | doctest.ELLIPSIS \
        | doctest.REPORT_NDIFF




def is_probably_test( fname ):

  data = file( fname ).read( 1024 )

  for line in data.split( "\n" ):
    if line.strip() == ":doctest:":
      return True

  return False


def find_all_tests():

  for current, dirs, files in os.walk( THIS_DIR ):

    for f in files:

      fname = os.path.join( current, f )

      if is_probably_test( fname ):
        yield fname




if __name__ == "__main__":

  for f in find_all_tests():

    print "--", f
    failed, run = doctest.testfile( f, report=True, optionflags=OPTIONS )
    print "Ran %d tests, %d failed." % ( run, failed )
    print
