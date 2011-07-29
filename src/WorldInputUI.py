# -*- coding: utf-8 -*-

## Copyright (c) 2007-2011 Pascal Varet <p.varet@gmail.com>
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


from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui  import QTextEdit
from PyQt4.QtGui  import QFontMetrics
from PyQt4.QtGui  import QKeySequence


from ActionSet        import ActionSet
from InputHistory     import InputHistory



class WorldInputUI( QTextEdit ):

  returnPressed = pyqtSignal()
  focusChanged  = pyqtSignal( 'QWidget' )

  def __init__( self, parent, world, shouldsavehistory=True ):

    QTextEdit.__init__( self, parent )

    self.setTabChangesFocus( True )
    self.setAcceptRichText( False )

    self.world    = world
    self.settings = world.settings
    self.history  = InputHistory( self, shouldsavehistory )

    self.actionset = ActionSet( self )

    self.actionset.bindAction( "historyup",    self.historyUp )
    self.actionset.bindAction( "historydown",  self.historyDown )
    self.actionset.bindAction( "autocomplete", self.autocomplete )

    ## Apply configuration:

    self.refresh()

    ## And bind it to key changes:

    for key in [ "font.color", "font.name", "font.size", "background.color" ]:
      self.settings._ui._input.onChange( key, self.refresh )

    self.returnPressed.connect( self.clearAndSend )


  def refresh( self ):

    ## Unlike the output UI, which is very specific to the problem domain --
    ## i.e. MU*s, the input box should be whatever's convenient to the
    ## user, and already configured in their system. This is why we use
    ## system default values when nothing specific is configured.

    style_elements = []

    input_settings = self.settings._ui._input
    if input_settings._font._color:

      style_elements.append( u"color: %s" \
                             % input_settings._font._color )

    if input_settings._font._name:

      style_elements.append( u"font-family: %s" \
                             % input_settings._font._name )

    if input_settings._font._size:

      style_elements.append( u"font-size: %dpt" \
                             % input_settings._font._size )

    if input_settings._background._color:

      style_elements.append( u"background-color: %s" \
                             % input_settings._background._color )

    if style_elements:
      self.setStyleSheet( u"QTextEdit { %s }" % " ; ".join( style_elements ) )

    font_height = QFontMetrics( self.font() ).height()
    self.setMinimumHeight( font_height*3 )


  def keyPressEvent( self, e ):

    ## Custom key sequence handler: since all our shortcuts are configurable,
    ## and are allowed to override the default QTextEdit shortcuts, we have to
    ## override the key event handler to preempt the use of those shortcuts.
    ## Note: This still doesn't work for Tab & Shift+Tab, which are handled
    ## straight in QWidget.event() by Qt.

    key = QKeySequence( int( e.modifiers() ) + e.key() )

    for a in self.actions() + self.parentWidget().actions():
      for shortcut in a.shortcuts():

        if key.matches( shortcut ) == QKeySequence.ExactMatch:

          a.trigger()
          e.accept()
          return

    ## Special case: disallow overriding of Return/Enter.

    alt_ctrl_shift = e.modifiers() & \
                   ( Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier )

    if e.key() in ( Qt.Key_Return, Qt.Key_Enter ) \
      and alt_ctrl_shift == Qt.NoModifier:

      self.returnPressed.emit()
      e.accept()

    else:
      QTextEdit.keyPressEvent( self, e )


  @pyqtSlot()
  def clearAndSend( self ):

    text = unicode( self.toPlainText() )

    self.clear()

    if text:
      self.history.update( text )

    self.world.processInput( text )


  def historyUp( self ):

    self.history.historyUp()


  def historyDown( self ):

    self.history.historyDown()


  def autocomplete( self ):

    self.world.worldui.autocompleter.complete( self )


  def focusInEvent( self, e ):

    QTextEdit.focusInEvent( self, e )

    ## Notify other possible interested parties that this widget now has the
    ## focus.

    self.focusChanged.emit( self )


  def __del__( self ):

    self.world     = None
    self.settings  = None
    self.history   = None
    self.commands  = None
    self.actionset = None
