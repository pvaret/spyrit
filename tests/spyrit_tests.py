#!/usr/bin/python
## -*- coding: utf-8 -*-

import os
import sys
import unittest

THIS_DIR   = os.path.dirname( __file__ )
SPYRIT_DIR = os.path.join( THIS_DIR, os.path.pardir )

sys.path.append( SPYRIT_DIR )

from Pipeline import Pipeline

from BaseFilter        import BaseFilter

from AnsiFilter        import AnsiFilter
from TelnetFilter      import TelnetFilter
from FlowControlFilter import FlowControlFilter
from UnicodeTextFilter import UnicodeTextFilter
from TriggersFilter    import TriggersFilter

from PipelineChunks import ChunkTypes
from PipelineChunks import ByteChunk


class testSimplePipeline( unittest.TestCase ):

  def setUp( s ):

    s.pipe = Pipeline()

    ## Require at least one filter for chunk feeding to work.
    s.pipe.addFilter( BaseFilter )

    s.output = []
    s.pipe.addSink( s.sink )


  def sink( s, data ):

    for item in data:
      s.output.append( item )


  def test_feed( s ):

    DATA = "abc"

    s.pipe.feedBytes( DATA )

    s.assertTrue( len( s.output ) == 2 )

    c = s.output[0]
    s.assertTrue( c.chunktype == ChunkTypes.BYTES )
    s.assertTrue( c.data == DATA )

    c = s.output[1]
    s.assertTrue( c.chunktype == ChunkTypes.ENDOFPACKET )

  def test_format_for_sending( s ):

    DATA = "abc"

    s.assertTrue( s.pipe.formatForSending( DATA ) == DATA )


  def test_notifications( s ):

    NOTIFICATION = "test_notification"
    DATA = "abc"

    bucket = []

    def callback( data ):
      bucket.append( data )

    s.pipe.bindNotificationListener( NOTIFICATION, callback )


    ## Notification is all set up. Now trigger it.

    s.pipe.notify( NOTIFICATION, DATA )

    s.assertTrue( len( bucket ) == 1 and bucket[0] == DATA )



class testFullPipeLine( unittest.TestCase ):

  def setUp( s ):

    s.pipe = Pipeline()

    s.pipe.addFilter( TelnetFilter )
    s.pipe.addFilter( AnsiFilter )
    s.pipe.addFilter( FlowControlFilter )
    s.pipe.addFilter( UnicodeTextFilter, encoding="utf-8" )
    s.pipe.addFilter( TriggersFilter, manager=None )


  def test_telnet( s ):

    DATA = chr( 255 ) + chr( 255 ) ## IAC + IAC

    bucket = []

    def callback( data ):
      for item in data: bucket.append( item )

    s.pipe.addSink( callback )

    s.pipe.feedChunk( ByteChunk( DATA ) )

    s.assertTrue( len( bucket ) == 1 )

    c = bucket[0]
    s.assertTrue( c.chunktype == ChunkTypes.TEXT )
    s.assertTrue( c.data == u'\ufffd' )


if __name__ == "__main__":
  unittest.main()
