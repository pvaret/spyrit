.. :doctest:

REGRESSION: When an ANSI line is split by the prompt sweeper, if it happens
in the middle of an ANSI sequence, then that sequence isn't parsed properly.

Let's thus test that an ANSI sequence is continued correctly after a prompt
sweep.

Setup the Pipeline:

>>> from Pipeline import Pipeline
>>> from AnsiFilter import AnsiFilter
>>> p = Pipeline()
>>> p.addFilter( AnsiFilter )

Setup a sink for the Pipeline:

>>> buffer = []
>>> def sink( chunks ):
...   buffer.extend( chunks )
>>> p.addSink( sink )

And test the behavior.

>>> ansi_seq = chr(27) + "[4m"  ## underline
>>> p.feedBytes( ansi_seq[0:1] )
>>> p.sweepPrompt()
>>> p.feedBytes( ansi_seq[1:] )
>>> print buffer
[... <Chunk Type: ANSI...]
