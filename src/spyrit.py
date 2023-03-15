#!/usr/bin/env python

# Copyright (c) 2007-2022 Pascal Varet <p.varet@gmail.com>
#
# This file is part of Spyrit.
#
# Spyrit is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 2 as published by the Free
# Software Foundation.
#
# You should have received a copy of the GNU General Public License along with
# Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
# Fifth Floor, Boston, MA  02110-1301  USA
#


#
# spyrit.py
#
# Bootstraps the program.
# This file is kept purposefully short, so that the code will run off imported
# bytecode as early as possible.
#


import sys

from Messages import messages


def main(args):
    from CheckVersions import check_python_version
    from CheckVersions import check_pyqt6_installed
    from CheckVersions import check_qt_version

    for check in (
        check_python_version,
        check_pyqt6_installed,
        check_qt_version,
    ):
        ok, msg = check()

        if not ok:
            messages.error(msg)
            sys.exit(1)  # Fail!

        if "--check-dependencies-only" in args:
            messages.info(msg)

    if "--check-dependencies-only" in args:
        sys.exit(0)  # Success.

    from Application import Application

    Application(args).doExec()


if __name__ == "__main__":
    main(sys.argv)
