##
## WorldUI.py
##
## Contains the WorldUI class, which manages a world's widget for reading and
## writing.
##


from localqt import *

from PipelineChunks import chunktypes


class WorldUI( QtGui.QTextEdit ):

  def __init__( s, parent, world ):
    
    QtGui.QTextEdit.__init__( s, parent )

    s.parent = parent
    s.world  = world

    s.setCurrentFont( QtGui.QFont("Courier") )
    world.socketpipeline.addSink( s.sink, [chunktypes.TEXT, chunktypes.ENDOFLINE] )
    world.connectToWorld()


  def sink( s, chunks ):

    for chunk in chunks:
      if chunk.chunktype == chunktypes.TEXT:
        s.insertPlainText( chunk.data )
      elif chunk.chunktype == chunktypes.ENDOFLINE:
        s.insertPlainText( "\n" )
