##
## localqt.py
##
## Imports the PyQt4 functions and namespaces that will be used throughout
## the whole application, for convenience.
##

from PyQt4 import QtCore
from PyQt4 import QtGui

connect = QtCore.QObject.connect
emit    = QtCore.QObject.emit
SIGNAL  = QtCore.SIGNAL
SLOT    = QtCore.SLOT
