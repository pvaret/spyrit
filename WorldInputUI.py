# -*- coding: utf-8 -*-

## Copyright (c) 2007-2009 Pascal Varet <p.varet@gmail.com>
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

from Commands         import Commands
from ActionSet        import ActionSet
from InputHistory     import InputHistory
from ConfigObserver   import ConfigObserver



class WorldInputUI( QtGui.QTextEdit ):

  def __init__( s, parent, world, shouldsavehistory=True ):

    QtGui.QTextEdit.__init__( s, parent )

    s.setAcceptRichText( False )

    s.world    = world
    s.conf     = world.conf
    s.history  = InputHistory( s, shouldsavehistory )
    s.commands = Commands( world )

    s.actionset = ActionSet( s )

    s.actionset.bindAction( "historyup",   s.historyUp )
    s.actionset.bindAction( "historydown", s.historyDown )

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
    connect( s, SIGNAL( "tabPressed()" ),    s.autocomplete )


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


  def keyPressEvent( s, e ):

    alt_ctrl_shift = e.modifiers() & \
                   ( Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier )

    if e.key() in [ Qt.Key_Return, Qt.Key_Enter ] \
      and alt_ctrl_shift == Qt.NoModifier:

      emit( s, SIGNAL( "returnPressed()" ) )
      e.accept()

    elif e.key() == Qt.Key_Tab and e.modifiers() == Qt.NoModifier:
      emit( s, SIGNAL( "tabPressed()" ) )
      e.accept()

    else:

      QtGui.QTextEdit.keyPressEvent( s, e )


  def clearAndSend( s ):

    text = unicode( s.toPlainText() ).rstrip( u"\r\n" )

    s.clear()

    if text:
      s.history.update( text )

    if text.startswith( s.conf._input_command_char ):
      s.commands.execute( text[ len( s.conf._input_command_char ): ] )

    else:
      s.world.socketpipeline.send( text + u"\r\n" )


  def historyUp( s ):

    s.history.historyUp()


  def historyDown( s ):

    s.history.historyDown()


  def autocomplete( s ):

    s.world.worldui.autocompleter.complete( s )


  def __del__( s ):

    s.world     = None
    s.conf      = None
    s.history   = None
    s.commands  = None
    s.observer  = None
    s.actionset = None