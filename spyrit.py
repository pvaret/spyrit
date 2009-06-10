#!/usr/bin/python
## -*- coding: utf-8 -*-

##
## spyrit.py
##
## Bootstraps the program.
## This file is kept purposefully short, so that the code will run off imported
## bytecode as early as possible.
##



from Utilities import test_python_version, \
                      test_sip_version, \
                      test_pyqt4, \
                      test_qt_version


for test in ( test_python_version,
              test_sip_version,
              test_pyqt4,
              test_qt_version ):

  result, msg = test()

  if not result:

    import sys
    from Logger import logger
    logger.error( msg )

    sys.exit( 1 )


def main():

  from Application import Application
  Application().exec_()


if __name__ == "__main__":
  main()
