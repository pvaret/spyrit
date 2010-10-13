# -*- coding: utf-8 -*-

## Copyright (c) 2007-2010 Pascal Varet <p.varet@gmail.com>
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
## WorldInputUI.py
##
## This files holds the WorldInputUI class, which is the input box in which
## you type stuff to be sent to the world.
##


from localqt import *

from Singletons       import singletons
from ActionSet        import ActionSet
from InputHistory     import InputHistory
from ConfigObserver   import ConfigObserver
from Globals          import CMDCHAR



class WorldInputUI( QtGui.QTextEdit ):

  def __init__( s, parent, world, shouldsavehistory=True ):

    QtGui.QTextEdit.__init__( s, parent )

    s.setAcceptRichText( False )

    s.world    = world
    s.conf     = world.conf
    s.history  = InputHistory( s, shouldsavehistory )

    s.actionset = ActionSet( s )

    s.actionset.bindAction( "historyup",    s.historyUp )
    s.actionset.bindAction( "historydown",  s.historyDown )
    s.actionset.bindAction( "autocomplete", s.autocomplete )

    ## Apply configuration:

    s.refresh()

    ## And bind it to key changes:

    s.observer = ConfigObserver( s.conf )
    s.observer.addCallback(
                            [
                              "input_font_color",
                              "input_font_name",
                              "input_font_size",
                              "input_background_color" 
                            ],
                            s.refresh
                          )

    connect( s, SIGNAL( "returnPressed()" ), s.clearAndSend )


  def refresh( s ):

    ## Unlike the output UI, which is very specific to the problem domain --
    ## i.e. MU*s, the input box should be whatever's convenient to the
    ## user, and already configured in their system. This is why we use
    ## system default values when nothing specific is configured.

    style_elements = []

    if s.conf._input_font_color:

      style_elements.append( u"color: %s" \
                             % s.conf._input_font_color )

    if s.conf._input_font_name:

      style_elements.append( u"font-family: %s" \
                             % s.conf._input_font_name )

    if s.conf._input_font_size:

      style_elements.append( u"font-size: %dpt" \
                             % s.conf._input_font_size )

    if s.conf._input_background_color:

      style_elements.append( u"background-color: %s" \
                             % s.conf._input_background_color )

    if style_elements:
      s.setStyleSheet( u"QTextEdit { %s }" % " ; ".join( style_elements ) )

    font_height = QtGui.QFontMetrics( s.font() ).height()
    s.setMinimumHeight( font_height*3 )


  def keyPressEvent( s, e ):

    ## Custom key sequence handler: since all our shortcuts are configurable,
    ## and are allowed to override the default QTextEdit shortcuts, we have to
    ## override the key event handler to preempt the use of those shortcuts.
    ## Note: This still doesn't work for Tab & Shift+Tab, which are handled
    ## straight in QWidget.event() by Qt.

    key = QtGui.QKeySequence( int( e.modifiers() ) + e.key() )

    for a in s.actions() + s.parentWidget().actions():
      for shortcut in a.shortcuts():

        if key.matches( shortcut ) == QtGui.QKeySequence.ExactMatch:

          a.trigger()
          e.accept()
          return

    ## Special case: disallow overriding of Return/Enter.

    alt_ctrl_shift = e.modifiers() & \
                   ( Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier )

    if e.key() in ( Qt.Key_Return, Qt.Key_Enter ) \
      and alt_ctrl_shift == Qt.NoModifier:

      emit( s, SIGNAL( "returnPressed()" ) )
      e.accept()

    else:
      QtGui.QTextEdit.keyPressEvent( s, e )


  def clearAndSend( s ):

    text = unicode( s.toPlainText() ).rstrip( u"\r\n" )

    s.clear()

    ## Ensure the input is cleared right away even if processing takes a little
    ## time:
    s.repaint()
    qApp().processEvents()

    if text:
      s.history.update( text )

    if text.startswith( CMDCHAR ):
      singletons.commands.runCmdLine( s.world, text[ len( CMDCHAR ): ] )

    else:
      s.world.socketpipeline.send( text + u"\r\n" )
      emit( s, SIGNAL( "textSent( str )" ), text )


  def historyUp( s ):

    s.history.historyUp()


  def historyDown( s ):

    s.history.historyDown()


  def autocomplete( s ):

    s.world.worldui.autocompleter.complete( s )


  def focusInEvent( s, e ):

    QtGui.QTextEdit.focusInEvent( s, e )

    ## Notify other possible interested parties that this widget now has the
    ## focus.

    emit( s, SIGNAL( "focusChanged( QWidget )" ), s )


  def __del__( s ):

    s.world     = None
    s.conf      = None
    s.history   = None
    s.commands  = None
    s.observer  = None
    s.actionset = None
