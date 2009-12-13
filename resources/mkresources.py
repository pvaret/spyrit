#!/usr/bin/python

import os

this_dir = os.path.dirname( __file__ )


#PYRCC    = os.path.join( this_dir, "spyrcc.py" )
PYRCC    = "pyrcc4"
RESOURCE = os.path.join( this_dir, "resources.qrc" )
OUTPUT   = os.path.join( this_dir, "../resources.py" )



os.execlp( PYRCC, PYRCC, "-o", OUTPUT, RESOURCE )
