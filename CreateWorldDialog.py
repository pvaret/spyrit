##
## CreateWorldDialog.py
##
## This class holds the dialog that lets the user create a new world.
##

from localqt import *

from PrettyOptionPanel  import ConfigMapper
from PrettyPanelHeader  import PrettyPanelHeader
from PrettyOptionDialog import PrettyOptionDialog


def CreateWorldDialog( conf, parent=None ):

    header = PrettyPanelHeader( "Create world",
                                 QtGui.QPixmap( ":/icon/new_world" ) )

    mapper = ConfigMapper( conf )
    mapper.addGroup( "World name", [
                       mapper.lineedit( "name" )
                     ] )
    mapper.addGroup( "Connection parameters", [
                       mapper.lineedit( "host", "&Server:" ),
                       mapper.spinbox(  "port", "&Port:" ),
                     ] )

    dialog = PrettyOptionDialog( mapper,
                                 parent  = parent,
                                 header  = header,
                                 oklabel = "Connect",
                                 title   = "Create world" )

    return dialog

