##
## localqt.py
##
## Imports the PyQt4 functions and namespaces that will be used throughout
## the whole application, for convenience.
##

import sip

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtNetwork

connect    = QtCore.QObject.connect
disconnect = QtCore.QObject.disconnect
emit       = QtCore.QObject.emit
SIGNAL     = QtCore.SIGNAL
SLOT       = QtCore.SLOT

Qt = QtCore.Qt
