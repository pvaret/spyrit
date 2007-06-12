##
## QuickConnectDialog.py
##
## This class holds the Quick Connect dialog. Y'know.
##

from localqt import *

from PrettyOptionPanel  import ConfigMapper
from PrettyPanelHeader  import PrettyPanelHeader
from PrettyOptionDialog import PrettyOptionDialog


class QuickConnectDialog:

  def __init__( s, conf, parent=None ):

    s.conf = conf
    
    s.header = PrettyPanelHeader( "Quick connect",
                                  QtGui.QPixmap( ":/icon/connect" ) )

    s.mapper = ConfigMapper( conf )
    s.mapper.addGroup( "Connection parameters", [
                         s.mapper.lineedit( "host", "&Server:" ),
                         s.mapper.spinbox( "port", "&Port:" ),
                       ] )

    s.dialog = PrettyOptionDialog( s.mapper,
                                   parent  = parent,
                                   header  = s.header,
                                   oklabel = "Connect",
                                   title   = "Quick connect" )


  def exec_( s ):

    return s.dialog.exec_()
