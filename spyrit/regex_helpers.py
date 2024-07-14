# Copyright (c) 2007-2024 Pascal Varet <p.varet@gmail.com>
#
# This file is part of Spyrit.
#
# Spyrit is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3 as published by the Free
# Software Foundation.
#
# You should have received a copy of the GNU General Public License along with
# Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
# Fifth Floor, Boston, MA  02110-1301  USA
#

"""
Functions to help construct URLs.
"""


def any_of(*elements: str) -> str:
    return r"(" + r"|".join(elements) + r")"


def blocks_with_separator(block: str, sep: str) -> str:
    return block + r"(" + sep + block + r")*"


def optional(element: str) -> str:
    return r"(" + element + r")?"
