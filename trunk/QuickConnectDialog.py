##
## QuickConnectDialog.py
##
## This class holds the Quick Connect dialog. Y'know.
##

from localqt import *

from PrettyOptionPanel  import ConfigMapper
from PrettyPanelHeader  import PrettyPanelHeader
from PrettyOptionDialog import PrettyOptionDialog


def QuickConnectDialog( conf, parent=None ):

    header = PrettyPanelHeader( "Quick connect",
                                 QtGui.QPixmap( ":/icon/connect" ) )

    mapper = ConfigMapper( conf )
    mapper.addGroup( "Connection parameters", [
                       mapper.lineedit( "host", "&Server:" ),
                       mapper.spinbox(  "port", "&Port:" ),
                     ] )

    dialog = PrettyOptionDialog( mapper,
                                 parent  = parent,
                                 header  = header,
                                 oklabel = "Connect",
                                 title   = "Quick connect" )

    return dialog

