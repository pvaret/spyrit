#!/usr/bin/env python

import os
import sys
THIS_DIR   = os.path.dirname( __file__ ) or '.'
SPYRIT_DIR = os.path.join( THIS_DIR, os.path.pardir )

CMDLINE = "%s/testrunner " \
          "--doctest-modules --doctest-glob=*.rst --exitfirst %s" \
          % ( THIS_DIR, SPYRIT_DIR )

import shlex
import subprocess

p = subprocess.Popen( shlex.split( CMDLINE ) + sys.argv[ 1: ] )
p.communicate()
