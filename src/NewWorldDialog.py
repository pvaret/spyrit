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
## NewWorldDialog.py
##
## This class holds the dialog that lets the user create a new world.
##

from PyQt4.QtGui import QPixmap, QLineEdit, QSpinBox, QCheckBox

from Utilities            import check_ssl_is_available
from SettingsPanel        import SettingsPanel
from PrettyPanelHeader    import PrettyPanelHeader
from PrettyOptionDialog   import PrettyOptionDialog
from SettingsWidgetMapper import SettingsWidgetMapper, qlineedit_not_empty


def NewWorldDialog( settings, parent=None ):

    header = PrettyPanelHeader( u"New world", QPixmap( ":/icon/new_world" ) )

    mapper = SettingsWidgetMapper( settings )
    panel  = SettingsPanel( mapper )

    name_mapper = panel.addBoundRow( 'name', QLineEdit(), u"World name:" )
    host_mapper = panel.addBoundRow( 'net.host', QLineEdit(), u"Server:" )

    name_mapper.setValidator( qlineedit_not_empty )
    host_mapper.setValidator( qlineedit_not_empty )

    port = QSpinBox()
    port.setRange( 1, 65535 )
    panel.addBoundRow( 'net.port', port, u"Port:" )

    if check_ssl_is_available():
      panel.addBoundRow( 'net.ssl', QCheckBox( u"Use SSL &encryption" ) )

    dialog = PrettyOptionDialog( mapper,
                                 panel,
                                 parent  = parent,
                                 header  = header,
                                 oklabel = u"Connect",
                                 title   = u"New world" )

    return dialog

