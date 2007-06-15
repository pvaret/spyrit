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
    s.conf  = world.conf

    s.refresh()

    connect( s, SIGNAL( "returnPressed()" ), s.clearAndSend )


  def refresh( s ):

    ## Unlike the output UI, which is very specific to the problem domain --
    ## i.e. MU*s, the input box should be whatever's convenient to the
    ## user, and already configured in their system. This is why we use
    ## system default values when nothing specific is configured.

    style_elements = []

    if s.conf._input_font_color:

      style_elements.append( "color: %s" \
                            % s.conf._input_font_color )


    if s.conf._input_font_name:
      
      style_elements.append( "font-family: %s" \
                            % s.conf._input_font_name )

    if s.conf._input_font_size:

      style_elements.append( "font-size: %dpt" \
                            % s.conf._input_font_size )

    if style_elements:
      s.setStyleSheet( "QTextEdit { %s }" % " ; ".join( style_elements ) )

    s.viewport().palette().setColor( QtGui.QPalette.Base,
                       QtGui.QColor( s.conf._input_background_color ) )


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


  def canInsertFromMimeData( s, mimesource ):

    return mimesource.hasText()


  def insertFromMimeData( s, mimesource ):

    s.insertPlainText( mimesource.text() )
