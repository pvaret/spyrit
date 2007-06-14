import sys
sys.path.append( "../../../trunk" )

from PrettyOptionPanel  import *
from PrettyOptionDialog import *
from PrettyPanelHeader  import *

app=QtGui.QApplication( sys.argv )


from Config import config

worldconf = config.getDomain( "Worlds" ).createAnonymousDomain()
worldconf._host = ""
worldconf._port = 8000
worldconf._ssl  = False

c = ConfigMapper( worldconf )

c.addGroup( "Connection parameters", [
    ( c.lineedit( "host", "&Server:" ) ),
    ( c.spinbox( "port", "&Port:" ) ),
  ] )

c.addGroup( "Encryption", [
  ( c.checkbox( "ssl", "Use &SSL:" ) )
] )

i = QtGui.QPixmap( "/usr/share/icons/hicolor/32x32/apps/konqueror.png" )
h = PrettyPanelHeader( None, "Quick connect", i )


p = PrettyOptionDialog( c, oklabel="Connect", header=h )

r = p.exec_()
if r == QtGui.QDialog.Accepted: print worldconf.dumpAsDict()

#app.exec_()