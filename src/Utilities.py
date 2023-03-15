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
# Utilities.py
#
# This file contains various utility functions.
#

"""
:doctest:

>>> from Utilities import *

"""

from types import TracebackType
from typing import Sequence, cast


DEFAULT_ESCAPES = {
    "\n": "n",
    "\r": "r",
    "\t": "t",
    '"': '"',
    "'": "'",
}

BS = "\\"


def check_ssl_is_available() -> bool:
    from PyQt6 import QtNetwork

    return QtNetwork.QSslSocket.supportsSsl()


def quote(string: str, esc: str = BS) -> str:
    r"""
    Escapes typical control characters in the given string.

    >>> STR = '''Carriage
    ... return.'''
    >>> print( quote( STR ) )
    Carriage\nreturn.

    """

    # Escape the escape character itself:
    string = string.replace(esc, esc + esc)

    # Then escape the rest:
    for from_, to in DEFAULT_ESCAPES.items():
        string = string.replace(from_, esc + to)

    return string


def unquote(string: str, esc: str = BS) -> str:
    r"""
    Unquote a string. Reverse operation to quote().

    >>> print( unquote( r'It\'s okay.\nYes.' ) )
    It's okay.
    Yes.

    >>> STR = r'''This \\ 'is'
    ... a "test".\n'''
    >>> unquote( quote( STR ) ) == STR
    True

    """

    result: list[str] = []
    in_escape = False
    escapes = dict((v, k) for (k, v) in DEFAULT_ESCAPES.items())

    for c in string:
        if in_escape:
            result.append(escapes.get(c, c))
            in_escape = False
            continue

        if c == esc:
            in_escape = True
            continue

        result.append(c)

    return "".join(result)


def make_unicode_translation_table() -> dict[int, str]:
    from unicodedata import normalize, category

    d: dict[int, str] = {}

    def is_latin_letter(letter: str) -> bool:
        return category(letter)[0] == "L"

    for i in range(0x1FFF):
        try:
            c = chr(i)

        except ValueError:
            continue

        if not is_latin_letter(c):
            continue

        # Decompose, then keep only Latin letters in the result.
        cn = normalize("NFKD", c)
        cn = "".join([letter for letter in cn if is_latin_letter(letter)])

        if cn and cn != c:
            d[i] = cn

    return d


UNICODE_TRANSLATION_TABLE = make_unicode_translation_table()


def remove_accents(
    string: str, translation_table: dict[int, str] = UNICODE_TRANSLATION_TABLE
) -> str:
    """
    Filters the diacritics off Latin characters in the given Unicode string.

    >>> print( remove_accents( "Touché!" ) )
    Touche!

    """

    return string.translate(translation_table)


def normalize_text(string: str) -> str:
    return remove_accents(string).lower()


def ensure_valid_filename(filename: str) -> str:
    """
    Make the given string safe(r) to use as a filename.

    Some platforms refuse certain characters in filenames. This function filters
    those characters out of the given string and replaces them with an
    underscore.

    The resulting string is not guaranteed to be valid, because ultimately it's
    the filesystem's call and we can't second-guess it. This function only makes
    a best-effort attempt which should hopefully suffice in most cases.

    Note: the filename must be given as Unicode.

    >>> print( ensure_valid_filename( "(127.0.0.1:*).log" ) )
    (127.0.0.1__).log

    """

    invalid_char_codes = [ord(c) for c in '<>:"/\\|?*']
    invalid_char_codes.extend(range(32))

    translation_table = dict((c, "_") for c in invalid_char_codes)

    return filename.translate(translation_table)


CRASH_MSG = """
<qt>A critical error has occurred. You did nothing wrong! This is most likely a
bug in Spyrit, and we are terribly sorry. The error is:<br/>
<center><b><i>%(error)s</i></b></center><br/>
It occured on <b>line %(line)d</b> of file <b>%(filename)s</b>.<br/>
<br/>
We would be grateful if you would kindly send us the exact error message above
to <a href="https://github.com/pvaret/spyrit/issues">our issue tracker</a>,
so we can look into it.<br/>
<br/>
Spyrit will now close.</qt>
""".strip()


def handle_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType,
):
    import sys
    import os.path
    import traceback

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWidgets import QMessageBox
    from PyQt6.QtWidgets import QWidget

    app = cast(QApplication, QApplication.instance())

    # KeyboardInterrupt is a special case.
    # We don't raise the error dialog when it occurs.
    if issubclass(exc_type, KeyboardInterrupt):
        if app:
            app.quit()

        return

    filename, line, _, _ = traceback.extract_tb(exc_traceback).pop()
    filename = os.path.basename(filename)
    error = "%s: %s" % (exc_type.__name__, exc_value)

    if app:
        window = app.activeWindow()
    else:
        window = None

    args = dict(filename=filename, line=line, error=error)

    QMessageBox.critical(
        cast(QWidget, window),
        "Oh dear...",
        CRASH_MSG % args,
        buttons=QMessageBox.StandardButton.Close,
    )

    if app:
        # TODO: Maybe make finalization handling safer with a context handler or
        # something?
        app.aboutToQuit.emit()  # type: ignore

    print("Spyrit has closed due to an error. This is the full error report:")
    print("")

    sys.__excepthook__(exc_type, exc_value, exc_traceback)

    if app:
        app.exit(1)


def format_as_table(
    columns: Sequence[Sequence[str]], headers: Sequence[str]
) -> str:
    """
    Format a set of columns and headers as a table.

    >>> print( format_as_table( columns=( [ "item 1" ], [ "item 2" ] ),
    ...                         headers=[ "Header A", "Header B" ] ) )
    Header A    Header B
    --------    --------
    item 1      item 2

    """

    newcolumns = list(list(column[:]) for column in columns)
    if len(headers) < len(columns):
        headers = list(headers) + [""] * (len(columns) - len(headers))

    for column, header in zip(newcolumns, headers):
        column.insert(0, header)
        column.insert(1, "-" * len(header))

        justify_to = max(len(item) for item in column)

        for i, item in enumerate(column):
            column[i] = item.ljust(justify_to + 4)

    return "\n".join("".join(line).rstrip() for line in zip(*newcolumns))
