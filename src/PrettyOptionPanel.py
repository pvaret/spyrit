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


from PyQt4.QtCore import Qt
from PyQt4.QtCore import QObject
#from PyQt4.QtCore import pyqtSlot
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

  def __init__( s, mapper, option, label=None ):

    s.mapper = mapper
    s.conf   = mapper.conf  ## For convenience.
    s.option = option
    s.label  = label

    mapper.widgets.append( s )


  #@pyqtSlot()
  def updateConfFromWidget( s ):

    ## This is the slot that updates the configuration object based on the
    ## widget contents. Since all subclasses map different widgets with
    ## different data access methods, the data retrieval is delegated to
    ## the method obtainValueFromWidget(), which every mapper must overload.

    value = s.obtainValueFromWidget()

    if value != s.conf[ s.option ]:

      s.conf[ s.option ] = value
      s.mapper.refreshState()


  def obtainValueFromWidget( s ):

    raise NotImplemented( "The obtainValueFromWidget method must be " \
                        + "reimplemented in children widgets!" )


  def updateWidgetFromConf( s ):

    ## This is the slot that updates the widget based on the configuration
    ## object's contents. Since all subclasses map different widgets with
    ## different data access methods, the data retrieval is delegated to
    ## the method applyValueToWidget(), which every mapper must overload.

    value = s.obtainValueFromWidget()

    if value != s.conf[ s.option ]:
      s.applyValueToWidget( s.conf[ s.option ] )


  def applyValueToWidget( s, value ):

    raise NotImplemented( "The applyValueToWidget method must be " \
                        + "reimplemented in children widgets!" )


  def isValid( s ):

    ## Indicates whether the widget mapper's contents is a suitable
    ## configuration value. This is typically used to disable the 'Ok' button
    ## of the dialog if it isn't.
    ## This method should be reimplemented by widget mappers that need to.

    if s.conf[ s.option ]:
      return True

    else:
      return False



class LineEditMapper( ConfigMapperWidget, QLineEdit ):

  MINIMUM_WIDTH = 250

  def __init__( s, mapper, option, label=None ):

    ConfigMapperWidget.__init__( s, mapper, option, label )
    QLineEdit.__init__( s )

    s.setMinimumWidth( s.MINIMUM_WIDTH )

    s.textEdited.connect( s.updateConfFromWidget )

    s.updateWidgetFromConf()


  def obtainValueFromWidget( s ):

    return unicode( s.text() )


  def applyValueToWidget( s, value ):

    s.setText( value )



class SpinBoxMapper( ConfigMapperWidget, QSpinBox ):

  def __init__( s, mapper, option, label=None ):

    ConfigMapperWidget.__init__( s, mapper, option, label )
    QSpinBox.__init__( s )

    s.setRange( 1, 65535 )
    s.setAlignment( Qt.AlignRight )

    s.valueChanged.connect( s.updateConfFromWidget )

    s.updateWidgetFromConf()


  def obtainValueFromWidget( s ):

    return s.value()


  def applyValueToWidget( s, value ):

    s.setValue( value )





class CheckBoxMapper( ConfigMapperWidget, QCheckBox ):

  def __init__( s, mapper, option, label=None ):

    ConfigMapperWidget.__init__( s, mapper, option, label )
    QCheckBox.__init__( s )

    text    = s.label.rstrip( u":" )
    s.label = None
    s.setText( text )

    s.stateChanged.connect( s.updateConfFromWidget )

    s.updateWidgetFromConf()


  def obtainValueFromWidget( s ):

    return ( s.checkState() == Qt.Checked ) and True or False


  def applyValueToWidget( s, value ):

    if value:
      s.setCheckState( Qt.Checked )

    else:
      s.setCheckState( Qt.Unchecked )


  def isValid( s ):
    return True  ## A checkbox is always valid.






class ConfigMapper( QObject ):

  ## This class aggregates all the mapper widgets, so that the actual option
  ## panel widget only has to know about this.
  ## It also provides convenience methods to create the most typically used
  ## configuration mapper widgets and automatically bind them to this mapper
  ## instance.

  isValid    = pyqtSignal( bool )
  hasChanges = pyqtSignal( bool )

  def __init__( s, conf ):

    QObject.__init__( s )

    s.conf     = conf
    s.widgets  = []
    s.contents = []


  def addGroup( s, group, items ):

    s.contents.append( ( group, items ) )


  def refreshState( s ):

    valid = all( w.isValid() for w in s.widgets )

    s.hasChanges.emit( not s.conf.isEmpty() )
    s.isValid.emit( valid )


  def lineedit( s, option, label=None ):

    return LineEditMapper( s, option, label )


  def spinbox( s, option, label=None ):

    return SpinBoxMapper( s, option, label )


  def checkbox( s, option, label=None ):

    return CheckBoxMapper( s, option, label )


  def updateWidgetsFromConf( s ):

    for w in s.widgets:
      w.updateWidgetFromConf()



class PrettyOptionPanel( QWidget ):

  MIN_LEFT_MARGIN                = 20
  MAX_LABEL_WIDTH_UNTIL_WORDWRAP = 100

  def __init__( s, mapper, parent=None ):

    QWidget.__init__( s, parent )

    s.mapper = mapper

    s.relayout()


  def relayout( s ):

    layout = s.layout()

    if layout:
      sip.delete( layout )

    s.setLayout( QGridLayout( s ) )
    s.layout().setColumnMinimumWidth( 0, s.MIN_LEFT_MARGIN )
    s.layout().setColumnStretch( 0, 0 )
    s.layout().setColumnStretch( 1, 0 )
    s.layout().setColumnStretch( 2, 1 )

    s.currentrow = 0

    for group, items in s.mapper.contents:

      s.addGroupRow( group )

      for item in items:
        s.addItemRow( item )

      s.addStretchRow()


  def addGroupRow( s, name ):

    label = QLabel( u"<b>" + name + u"</b>", s )
    label.setAlignment( Qt.AlignLeft | Qt.AlignBottom )

    s.layout().addWidget( label, s.currentrow, 0, 1, -1 )

    if s.currentrow > 0:
      s.layout().setRowMinimumHeight( s.currentrow,
                                      label.sizeHint().height() * 1.5 )

    s.currentrow += 1


  def addItemRow( s, widget ):

    label = widget.label

    if label:

      l = QLabel( label, s )
      l.setAlignment( Qt.AlignRight | Qt.AlignVCenter )
      l.setBuddy( widget )

      if l.sizeHint().width() >= s.MAX_LABEL_WIDTH_UNTIL_WORDWRAP:
        l.setWordWrap( True )

      s.layout().addWidget( l, s.currentrow, 1 )

    s.layout().addWidget( widget, s.currentrow, 2 )

    s.currentrow += 1


  def addStretchRow( s ):

    s.layout().setRowStretch( s.currentrow, 1 )
    s.currentrow += 1


  def defaults( s ):

    s.mapper.conf.reset()
    s.mapper.updateWidgetsFromConf()


  def apply( s ):

    s.mapper.conf.commit()
    s.mapper.updateWidgetsFromConf()


