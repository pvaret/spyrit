#!/usr/bin/python
# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
##
## This file is part of Spyrit.
##
## Spyrit is free software; you can redistribute it and/or modify it under the
## terms of the GNU General Public License version 2 as published by the Free
## Software Foundation.
##
## You should have received a copy of the GNU General Public License along with
## Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
## Fifth Floor, Boston, MA  02110-1301  USA
##


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
