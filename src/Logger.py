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
# Logger.py
#
# Holds the class that manages logging of a world's output to a text file.
#


import os
import time

from os.path import basename, dirname, isdir

from Globals import ESC
from Globals import FORMAT_PROPERTIES
from Globals import compute_closest_ansi_color
from FormatStack import FormatStack

from pipeline.ChunkData import ChunkType
from pipeline.ChunkData import FlowControl

from SingleShotTimer import SingleShotTimer


class PlainLogger(object):
    log_chunk_types = ChunkType.TEXT | ChunkType.FLOWCONTROL
    encoding = "utf-8"

    def __init__(self, world, logfile):
        self.world = world
        self.logfile = logfile

        self.is_logging = False
        self.buffer: list[bytes] = []

        self.flush_timer = SingleShotTimer(self.flushBuffer)
        self.flush_timer.setInterval(100)  # ms

    def logChunk(self, chunk):
        if not self.is_logging:
            return

        chunk_type, payload = chunk

        if chunk_type == ChunkType.TEXT:
            self.doLogText(payload)

        elif chunk == (ChunkType.FLOWCONTROL, FlowControl.LINEFEED):
            self.doLogText("\n")

        else:
            return

        self.flush_timer.start()

    def doLogText(self, text: str) -> None:
        self.buffer.append(text.encode(self.encoding, "replace"))

    def doLogStart(self):
        now = time.strftime("%c", time.localtime())
        self.doLogText(
            "%% Log start for %s on %s.\n" % (self.world.title(), now)
        )

    def doLogStop(self):
        now = time.strftime("%c", time.localtime())
        self.doLogText("%% Log end on %s.\n" % now)

    def flushBuffer(self):
        if self.is_logging and self.buffer:
            self.logfile.write(b"".join(self.buffer))
            self.logfile.flush()
            self.buffer[:] = []

    def start(self):
        if self.is_logging:
            return

        self.is_logging = True
        self.doLogStart()
        # TODO: move info message out of logger?
        self.world.info("Started logging to %s" % basename(self.logfile.name))

        self.flushBuffer()

    def stop(self):
        if not self.is_logging:
            return

        self.doLogStop()
        # TODO: move info message out of logger?
        self.world.info("Stopped logging.")

        self.flushBuffer()
        self.is_logging = False

    def __del__(self):
        self.stop()


class AnsiFormatter:
    def __init__(self, buffer):
        self.buffer = buffer

    def setProperty(self, property, value):
        if property == FORMAT_PROPERTIES.BOLD:
            self.buffer.append(ESC + b"[1m")

        elif property == FORMAT_PROPERTIES.ITALIC:
            self.buffer.append(ESC + b"[3m")

        elif property == FORMAT_PROPERTIES.UNDERLINE:
            self.buffer.append(ESC + b"[4m")

        elif property == FORMAT_PROPERTIES.COLOR:
            ansi_color = compute_closest_ansi_color(value)
            self.buffer.append(ESC + b"[38;5;%dm" % ansi_color)

        elif property == FORMAT_PROPERTIES.BACKGROUND:
            ansi_color = compute_closest_ansi_color(value)
            self.buffer.append(ESC + b"[48;5;%dm" % ansi_color)

    def clearProperty(self, property):
        if property == FORMAT_PROPERTIES.BOLD:
            self.buffer.append(ESC + b"[22m")

        elif property == FORMAT_PROPERTIES.ITALIC:
            self.buffer.append(ESC + b"[23m")

        elif property == FORMAT_PROPERTIES.UNDERLINE:
            self.buffer.append(ESC + b"[24m")

        elif property == FORMAT_PROPERTIES.COLOR:
            self.buffer.append(ESC + b"[39m")

        elif property == FORMAT_PROPERTIES.BACKGROUND:
            self.buffer.append(ESC + b"[49m")


class AnsiLogger(PlainLogger):
    log_chunk_types = (
        PlainLogger.log_chunk_types | ChunkType.HIGHLIGHT | ChunkType.ANSI
    )

    def __init__(self, *args):
        super().__init__(*args)

        self.format_stack = FormatStack(AnsiFormatter(self.buffer))

    def logChunk(self, chunk):
        chunk_type, _ = chunk

        if chunk_type & (ChunkType.HIGHLIGHT | ChunkType.ANSI):
            self.format_stack.processChunk(chunk)

        else:
            super().logChunk(chunk)

    def doLogStop(self):
        # TODO: decide if we want to also store the current format somewhere, in
        # case we want to re-apply it if the user re-starts the log.
        self.buffer.append(ESC + b"[m")
        super().doLogStop()


def create_logger_for_world(world, logfilename):
    dir = dirname(logfilename)

    if not isdir(dir):
        try:
            os.makedirs(dir)

        except (IOError, OSError):
            pass

    file = world.openFileOrErr(logfilename, "a+b")

    if not file:
        return None

    loggerClass = AnsiLogger if world.settings._log._ansi else PlainLogger

    logger = loggerClass(world, file)

    world.socketpipeline.addSink(logger.logChunk, logger.log_chunk_types)

    return logger
