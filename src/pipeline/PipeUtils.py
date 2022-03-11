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
# PipeUtils.py
#
# This file contains pipeline-related utilities.
#


from .ChunkData import ChunkType


def insert_chunks_in_chunk_buffer(chunkbuffer, new_chunks):

    pos = 0
    target_pos = 0
    new_chunk = None

    for i, chunk in enumerate(chunkbuffer):

        if not new_chunk:  # Pop the next chunk to insert...

            if not new_chunks:  # ... Assuming there is one, of course.
                return

            target_pos, new_chunk = new_chunks.pop(0)

        chunk_type, payload = chunk

        if chunk_type != ChunkType.TEXT:
            continue

        if pos == target_pos:

            chunkbuffer.insert(i, new_chunk)
            new_chunk = None
            continue

        elif target_pos - pos < len(payload):

            split_pos = target_pos - pos

            chunkbuffer.pop(i)
            chunkbuffer.insert(i, (ChunkType.TEXT, payload[:split_pos]))
            chunkbuffer.insert(i + 1, new_chunk)
            chunkbuffer.insert(i + 2, (ChunkType.TEXT, payload[split_pos:]))

            pos += split_pos
            new_chunk = None
            continue

        else:
            pos += len(payload)

    if target_pos == pos:
        chunkbuffer.append(new_chunk)
