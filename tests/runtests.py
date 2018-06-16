#!/usr/bin/python
## -*- coding: utf-8 -*-

import os
import sys
import doctest

THIS_DIR   = os.path.abspath( os.path.dirname( __file__ ) or os.curdir )
SPYRIT_DIR = os.path.normpath( os.path.join( THIS_DIR, os.path.pardir, 'src' ) )

sys.path.insert( 0, SPYRIT_DIR )

OPTIONS = ( doctest.NORMALIZE_WHITESPACE
          | doctest.ELLIPSIS
          | doctest.DONT_ACCEPT_TRUE_FOR_1
          | doctest.IGNORE_EXCEPTION_DETAIL

          | doctest.REPORT_NDIFF
          | doctest.REPORT_ONLY_FIRST_FAILURE )




def is_rst_doctest( fname ):

  if not fname.lower().endswith( ".rst" ):
    return False

  data = file( fname ).read( 4096 )

  for line in data.split( "\n" ):
    if line.lstrip( "." ).strip() == ":doctest:":
      return True

  return False


def is_python_module_doctest( fname ):

  if not fname.lower().endswith( ".py" ):
    return False

  data = file( fname ).read( 4096 )

  for line in data.split( "\n" ):
    if line.lstrip( "." ).strip() == ":doctest:":
      return True

  return False


def find_all_tests():

  for DIR in ( SPYRIT_DIR, THIS_DIR ):

    for current, dirs, files in os.walk( DIR ):

      for f in files:

        fname = os.path.join( current, f )

        if is_rst_doctest( fname ):
          yield os.path.relpath( fname, THIS_DIR )

        elif is_python_module_doctest( fname ):
          yield os.path.relpath( fname, THIS_DIR )




if __name__ == "__main__":

  include_list = sys.argv[ 1: ]

  for f in find_all_tests():

    if include_list and not any( pattern in f for pattern in include_list ):
      continue

    failed, run = doctest.testfile(
      f, report=True, optionflags=OPTIONS, encoding="utf-8" )

    if run > 0:
      print "--", f
      print "Ran %d tests, %d failed." % ( run, failed )
      print
