# -*- coding: utf-8 -*-

## Copyright (c) 2007-2020 Pascal Varet <p.varet@gmail.com>
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
## MacosSpecific.py
##
## Contains the class that implements Mac OS X-specific elements.
##


from PosixSpecific import PosixSpecific


class MacosSpecific(PosixSpecific):

    should_repaint_on_scroll = True
    default_font = "Monaco"

    def get_sound_backends(self):

        return ["qsound"]
