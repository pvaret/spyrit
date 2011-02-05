#!/usr/bin/python

import os
import subprocess

this_dir = os.path.dirname( __file__ )


PYRCC    = os.path.join( this_dir, "spyrcc.py" )
RESOURCE = os.path.join( this_dir, "resources.qrc" )
OUTPUT   = os.path.join( this_dir, "../resources.py" )

cmdline = "%s -o %s %s" % ( PYRCC, OUTPUT, RESOURCE )

subprocess.Popen( cmdline, shell=True )
