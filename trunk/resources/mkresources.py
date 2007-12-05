#!/usr/bin/python

import os

PYRCC    = "pyrcc4"
RESOURCE = "resources.qrc"
OUTPUT   = "../resources.py"

os.execlp( PYRCC, PYRCC, "-o", OUTPUT, RESOURCE )
