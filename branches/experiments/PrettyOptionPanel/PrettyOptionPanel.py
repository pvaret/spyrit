##
## PrettyOptionPanel.py
##
## This file, essentially, the PrettyOptionPanel class, that automatically
## creates a pretty option panel where all configuration widgets are cleanly
## aligned along a grid, based on a list of mappers between configuration keys
## and widgets.
## The file also contains all the classes for the mappers in question.
##


from localqt import *

from Separator import Separator


class ConfigMapperWidget:

  ## This here is the base widget mapper class; it is not used as such, but
  ## implements the boilerplate code that will be common to all its subclasses,
  ##  i.e. the actual widget mappers.

  def __init__( s, mapper, option ):

    s.mapper = mapper
    s.conf   = mapper.conf  ## for convenience.
    s.option = option

    mapper.widgets.append( s )


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



class LineEditMapper( ConfigMapperWidget, QtGui.QLineEdit ):

  MINIMUM_WIDTH = 150

  def __init__( s, mapper, option ):

    ConfigMapperWidget.__init__( s, mapper, option )
    QtGui.QLineEdit.__init__( s )

    s.setMinimumWidth( s.MINIMUM_WIDTH )

    connect( s, SIGNAL( "textEdited( const QString & )" ),
                s.updateConfFromWidget )

    s.updateWidgetFromConf()


  def obtainValueFromWidget( s ):

    return unicode( s.text() )


  def applyValueToWidget( s, value ):

    s.setText( value )



class SpinBoxMapper( ConfigMapperWidget, QtGui.QSpinBox ):

  def __init__( s, mapper, option ):

    ConfigMapperWidget.__init__( s, mapper, option )
    QtGui.QSpinBox.__init__( s )

    s.setRange( 1, 65535 )
    s.setAlignment( QtCore.Qt.AlignRight )

    connect( s, SIGNAL( "valueChanged( int )" ),
                s.updateConfFromWidget )

    s.updateWidgetFromConf()


  def obtainValueFromWidget( s ):

    return s.value()


  def applyValueToWidget( s, value ):

    s.setValue( value )





class ConfigMapper( QtCore.QObject ):

  ## This class aggregates all the mapper widgets, so that the actual option
  ## panel widget only has to know about this.
  ## It also provides convenience method to create the most typically used
  ## configuration mapper widgets and automatically bind them to this mapper
  ## instance.

  def __init__( s, conf ):

    QtCore.QObject.__init__( s )

    s.conf     = conf
    s.contents = []
    s.widgets  = []


  def addGroup( s, group, items ):

    s.contents.append( ( group, items ) )


  def refreshState( s ):

    if s.conf.isEmpty():
      emit( s, SIGNAL( "hasChanges( bool )" ), False )

    else:
      emit( s, SIGNAL( "hasChanges( bool )" ), True )

    d = s.conf.getOwnDict()

    for w in s.widgets:

      if not w.isValid():
        emit( s, SIGNAL( "isValid( bool )" ), False )
        break

    else:
      emit( s, SIGNAL( "isValid( bool )" ), True )


  def lineedit( s, option ):

    return LineEditMapper( s, option )


  def spinbox( s, option ):

    return SpinBoxMapper( s, option )


  def updateWidgetsFromConf( s ):

    for w in s.widgets:
      w.updateWidgetFromConf()



class PrettyOptionPanel( QtGui.QWidget ):
  
  MIN_LEFT_MARGIN = 25
  MAX_LABEL_WIDTH_UNTIL_WORDWRAP = 100

  def __init__( s, mapper, parent=None ):

    QtGui.QWidget.__init__( s, parent )
    
    s.mapper = mapper

    s.relayout()

    
  def relayout( s ):
    
    layout = s.layout()
    
    if layout:
      import sip
      sip.delete( layout )

    s.setLayout( QtGui.QGridLayout( s ) )
    s.layout().setColumnMinimumWidth( 0, s.MIN_LEFT_MARGIN )
    s.layout().setColumnStretch( 0, 0 )
    s.layout().setColumnStretch( 1, 0 )
    s.layout().setColumnStretch( 2, 1 )
   
    currentrow = 0

    for group, items in s.mapper.contents:

      s.addGroup( group, currentrow )
      currentrow += 1

      for item, itemlabel in items:
        s.addItem( item, currentrow, itemlabel )
        currentrow += 1
    


  def addGroup( s, name, currentrow ):
    
    label = QtGui.QLabel("<b>" + name + "</b>", s)
    label.setAlignment( QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom )

    s.layout().addWidget( label, currentrow, 0, 1, -1 )

    if currentrow > 0:
      s.layout().setRowMinimumHeight( currentrow,
                                      label.sizeHint().height() * 1.5 )
    

  def addItem( s, widget, currentrow, label=None ):
    
    if label:

      l = QtGui.QLabel( label, s )
      l.setAlignment( QtCore.Qt.AlignRight )
      l.setBuddy( widget )

      if l.sizeHint().width() >= s.MAX_LABEL_WIDTH_UNTIL_WORDWRAP:
        l.setWordWrap( True )

      s.layout().addWidget( l, currentrow, 1 )
    
    s.layout().addWidget( widget, currentrow, 2 )


  def defaults( s ):
   
    s.mapper.conf.reset()
    s.mapper.updateWidgetsFromConf()


  def apply( s ):

    s.mapper.conf.commit()
    s.mapper.updateWidgetsFromConf()



class PrettyOptionDialog( QtGui.QDialog ):

  def __init__( s, mapper, header=None, oklabel=None, parent=None ):

    QtGui.QDialog.__init__( s, parent )

    s.header    = header
    s.panel     = PrettyOptionPanel( mapper )
    s.buttonbox = QtGui.QDialogButtonBox( QtGui.QDialogButtonBox.Ok
                                        | QtGui.QDialogButtonBox.Cancel )

    s.okbutton = s.buttonbox.button( QtGui.QDialogButtonBox.Ok )

    if oklabel:
      s.okbutton.setText( oklabel )

    connect( mapper,     SIGNAL( "isValid( bool )" ),
             s.okbutton, SLOT( "setEnabled( bool )" ) )

    connect( s.buttonbox, SIGNAL( "accepted()" ), s, SLOT( "accept()" ) );
    connect( s.buttonbox, SIGNAL( "rejected()" ), s, SLOT( "reject()" ) );

    mapper.refreshState()

    s.relayout()


  def relayout( s ):

    if s.layout(): 
      import sip
      sip.delete( s.layout() )

    s.setLayout( QtGui.QVBoxLayout( s ) )

    if s.header:
      s.layout().addWidget( s.header )

    s.layout().addWidget( s.panel )
    s.layout().addWidget( Separator( s ) )
    s.layout().addWidget( s.buttonbox )
