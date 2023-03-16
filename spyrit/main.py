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


"""
Check dependencies, bootstrap the program.
"""


import sys

from typing import NoReturn

from spyrit import dependency_checker


def show_deps_and_exit(
    checker: dependency_checker.DependencyChecker,
) -> NoReturn:
    for msg in checker.messages():
        print(msg)

    sys.exit(0 if checker.dependenciesMet() else 1)


def main(args: list[str]) -> int:
    checker = dependency_checker.DependencyChecker()

    if not checker.dependenciesMet():
        show_deps_and_exit(checker)

    if dependency_checker.CHECK_DEPENDENCIES_ARG in args:
        show_deps_and_exit(checker)

    # Note that we don't pull in any dependencies until now.

    from spyrit.bootstrap import bootstrap

    return bootstrap(args)


def run() -> NoReturn:
    sys.exit(main(sys.argv))
