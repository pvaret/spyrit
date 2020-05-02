.. :doctest:

REGRESSION: When an ANSI line is split by the prompt sweeper, if it happens
in the middle of an ANSI sequence, then that sequence isn't parsed properly.

Let's thus test that an ANSI sequence is continued correctly after a prompt
sweep.

Setup the Pipeline:

>>> from pipeline.Pipeline import Pipeline
>>> from pipeline.AnsiFilter import AnsiFilter
>>> p = Pipeline()
>>> p.addFilter( AnsiFilter )

Silence Qt warnings:

>>> def silent( *args ):
...   pass
>>> from PyQt5 import QtCore
>>> QtCore.qInstallMessageHandler( silent )

Setup a sink for the Pipeline:

>>> buffer = []
>>> def sink( chunk ):
...   buffer.append( chunk )
>>> p.addSink( sink )

And test the behavior.

>>> ansi_seq = bytearray([27]) + b"[4m"  ## underline
>>> p.feedBytes( ansi_seq[0:1] )
>>> p.sweepPrompt()
>>> p.feedBytes( ansi_seq[1:] )

Ensure the buffer now contains a proper ANSI chunk:
>>> from pipeline.ChunkData import chunk_repr
>>> print( [ chunk_repr( chunk ) for chunk in buffer ] )  #doctest: +ELLIPSIS
[...<Chunk: ANSI...]
