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
## PrettyOptionPanel.py
##
## This file, essentially, holds the PrettyOptionPanel class, that
## automatically creates a pretty option panel where all configuration widgets
## are cleanly aligned along a grid, based on a list of mappers between
## configuration keys and widgets.
## The file also contains all the classes for the mappers in question.
##

import sip

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui  import QLabel
from PyQt4.QtGui  import QWidget
from PyQt4.QtGui  import QSpinBox
from PyQt4.QtGui  import QLineEdit
from PyQt4.QtGui  import QCheckBox
from PyQt4.QtGui  import QGridLayout


class ConfigMapperWidget:

  ## This here is the base widget mapper class; it is not used as such, but
  ## implements the boilerplate code that will be common to all its subclasses,
  ## i.e. the actual widget mappers.

  def __init__( self, mapper, option, label=None ):

    self.mapper   = mapper
    self.settings = mapper.settings  ## For convenience.
    self.option   = option
    self.label    = label

    mapper.widgets.append( self )


  #@pyqtSlot()  ## Not a QObject, can't make it an official slot.
  def updateConfFromWidget( self ):

    ## This is the slot that updates the configuration object based on the
    ## widget contents. Since all subclasses map different widgets with
    ## different data access methods, the data retrieval is delegated to
    ## the method obtainValueFromWidget(), which every mapper must overload.

    value = self.obtainValueFromWidget()

    if value != self.settings[ self.option ]:

      self.settings[ self.option ] = value
      self.mapper.refreshState()


  def obtainValueFromWidget( self ):

    raise NotImplemented( "The obtainValueFromWidget method must be " \
                        + "reimplemented in children widgets!" )


  def updateWidgetFromConf( self ):

    ## This is the slot that updates the widget based on the configuration
    ## object's contents. Since all subclasses map different widgets with
    ## different data access methods, the data retrieval is delegated to
    ## the method applyValueToWidget(), which every mapper must overload.

    value = self.obtainValueFromWidget()

    if value != self.settings[ self.option ]:
      self.applyValueToWidget( self.settings[ self.option ] )


  def applyValueToWidget( self, value ):

    raise NotImplemented( "The applyValueToWidget method must be " \
                        + "reimplemented in children widgets!" )


  def isValid( self ):

    ## Indicates whether the widget mapper's contents is a suitable
    ## configuration value. This is typically used to disable the 'Ok' button
    ## of the dialog if it isn't.
    ## This method should be reimplemented by widget mappers that need to.

    if self.settings[ self.option ]:
      return True

    else:
      return False



class LineEditMapper( ConfigMapperWidget, QLineEdit ):

  MINIMUM_WIDTH = 250

  def __init__( self, mapper, option, label=None ):

    ConfigMapperWidget.__init__( self, mapper, option, label )
    QLineEdit.__init__( self )

    self.setMinimumWidth( self.MINIMUM_WIDTH )

    self.textEdited.connect( self.updateConfFromWidget )

    self.updateWidgetFromConf()


  def obtainValueFromWidget( self ):

    return unicode( self.text() )


  def applyValueToWidget( self, value ):

    self.setText( value )



class SpinBoxMapper( ConfigMapperWidget, QSpinBox ):

  def __init__( self, mapper, option, label=None ):

    ConfigMapperWidget.__init__( self, mapper, option, label )
    QSpinBox.__init__( self )

    self.setRange( 1, 65535 )
    self.setAlignment( Qt.AlignRight )

    self.valueChanged.connect( self.updateConfFromWidget )

    self.updateWidgetFromConf()


  def obtainValueFromWidget( self ):

    return self.value()


  def applyValueToWidget( self, value ):

    self.setValue( value )





class CheckBoxMapper( ConfigMapperWidget, QCheckBox ):

  def __init__( self, mapper, option, label=None ):

    ConfigMapperWidget.__init__( self, mapper, option, label )
    QCheckBox.__init__( self )

    text = self.label.rstrip( u":" )
    self.label = None
    self.setText( text )

    self.stateChanged.connect( self.updateConfFromWidget )

    self.updateWidgetFromConf()


  def obtainValueFromWidget( self ):

    return ( self.checkState() == Qt.Checked ) and True or False


  def applyValueToWidget( self, value ):

    if value:
      self.setCheckState( Qt.Checked )

    else:
      self.setCheckState( Qt.Unchecked )


  def isValid( self ):
    return True  ## A checkbox is always valid.






class ConfigMapper( QObject ):

  ## This class aggregates all the mapper widgets, so that the actual option
  ## panel widget only has to know about this.
  ## It also provides convenience methods to create the most typically used
  ## configuration mapper widgets and automatically bind them to this mapper
  ## instance.

  isValid    = pyqtSignal( bool )
  hasChanges = pyqtSignal( bool )

  def __init__( self, settings ):

    QObject.__init__( self )

    self.settings = settings
    self.widgets  = []
    self.contents = []


  def addGroup( self, group, items ):

    self.contents.append( ( group, items ) )


  def refreshState( self ):

    valid = all( w.isValid() for w in self.widgets )

    self.hasChanges.emit( not self.settings.isEmpty() )
    self.isValid.emit( valid )


  def lineedit( self, option, label=None ):

    return LineEditMapper( self, option, label )


  def spinbox( self, option, label=None ):

    return SpinBoxMapper( self, option, label )


  def checkbox( self, option, label=None ):

    return CheckBoxMapper( self, option, label )


  def updateWidgetsFromConf( self ):

    for w in self.widgets:
      w.updateWidgetFromConf()



class PrettyOptionPanel( QWidget ):

  MIN_LEFT_MARGIN                = 20
  MAX_LABEL_WIDTH_UNTIL_WORDWRAP = 100

  def __init__( self, mapper, parent=None ):

    QWidget.__init__( self, parent )

    self.mapper = mapper

    self.relayout()


  def relayout( self ):

    layout = self.layout()

    if layout:
      sip.delete( layout )

    self.setLayout( QGridLayout( self ) )
    self.layout().setColumnMinimumWidth( 0, self.MIN_LEFT_MARGIN )
    self.layout().setColumnStretch( 0, 0 )
    self.layout().setColumnStretch( 1, 0 )
    self.layout().setColumnStretch( 2, 1 )

    self.currentrow = 0

    for group, items in self.mapper.contents:

      self.addGroupRow( group )

      for item in items:
        self.addItemRow( item )

      self.addStretchRow()


  def addGroupRow( self, name ):

    label = QLabel( u"<b>" + name + u"</b>", self )
    label.setAlignment( Qt.AlignLeft | Qt.AlignBottom )

    self.layout().addWidget( label, self.currentrow, 0, 1, -1 )

    if self.currentrow > 0:
      self.layout().setRowMinimumHeight( self.currentrow,
                                         label.sizeHint().height() * 1.5 )

    self.currentrow += 1


  def addItemRow( self, widget ):

    label = widget.label

    if label:

      l = QLabel( label, self )
      l.setAlignment( Qt.AlignRight | Qt.AlignVCenter )
      l.setBuddy( widget )

      if l.sizeHint().width() >= self.MAX_LABEL_WIDTH_UNTIL_WORDWRAP:
        l.setWordWrap( True )

      self.layout().addWidget( l, self.currentrow, 1 )

    self.layout().addWidget( widget, self.currentrow, 2 )

    self.currentrow += 1


  def addStretchRow( self ):

    self.layout().setRowStretch( self.currentrow, 1 )
    self.currentrow += 1


  def defaults( self ):

    self.mapper.settings.reset()
    self.mapper.updateWidgetsFromConf()


  def apply( self ):

    self.mapper.settings.apply()
    self.mapper.updateWidgetsFromConf()


