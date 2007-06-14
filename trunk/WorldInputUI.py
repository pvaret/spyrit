##
## WorldInputUI.py
##
## This files holds the WorldInputUI class, which is the input box in which
## you type stuff to be sent to the world.
##


from localqt import *

class WorldInputUI( QtGui.QTextEdit ):

  def __init__( s, parent, world ):

    QtGui.QTextEdit.__init__( s, parent )

    s.world = world

    connect( s, SIGNAL( "returnPressed()" ), s.clearAndSend )


  def keyPressEvent( s, e ):

    if e.key() in [ Qt.Key_Return, Qt.Key_Enter ]:

      emit( s, SIGNAL( "returnPressed()" ) )
      e.accept()

    else:

      QtGui.QTextEdit.keyPressEvent( s, e )


  def clearAndSend( s ):

    text = unicode( s.toPlainText() ).rstrip( "\n" )
    s.world.socketpipeline.write( text + "\n" )
    s.clear()
