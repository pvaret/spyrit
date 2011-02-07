#!/usr/bin/python

import os
import subprocess

THIS_DIR = os.path.dirname( __file__ ) or os.path.curdir

PYRCC    = os.path.join( THIS_DIR, "spyrcc.py" )
RESOURCE = os.path.join( THIS_DIR, "resources.qrc" )
OUTPUT   = os.path.join( THIS_DIR, os.pardir, "resources.py" )

CMDLINE = "%s -o %s %s" % ( PYRCC, OUTPUT, RESOURCE )

subprocess.Popen( CMDLINE, shell=True ).wait()
