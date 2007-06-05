##
## spyrit.py
##
## Bootstraps the program.
## This file is kept purposefully short, so that the code will run off imported
## bytecode as early as possible.
##



from Utilities import test_python_version, test_pyqt4, test_qt_version


if not test_python_version() or not test_pyqt4() or not test_qt_version() :

  import sys
  from Logger import logger
  logger.error( "This program requires " + \
                "Python 2.4, PyQt 4 and Qt 4.2 or later." )
  sys.exit( 1 )


import sys
from Application import Application

Application().exec_()
