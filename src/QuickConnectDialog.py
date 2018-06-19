# -*- coding: utf-8 -*-

## Copyright (c) 2007-2018 Pascal Varet <p.varet@gmail.com>
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
## QuickConnectDialog.py
##
## This file holds the Quick Connect dialog. Y'know.
##


from __future__ import absolute_import

from PyQt5.QtGui     import QPixmap
from PyQt5.QtWidgets import QLineEdit, QSpinBox, QCheckBox

from Utilities            import check_ssl_is_available
from SettingsPanel        import SettingsPanel
from SettingsWidgetMapper import SettingsWidgetMapper, qlineedit_not_empty
from PrettyPanelHeader    import PrettyPanelHeader
from PrettyOptionDialog   import PrettyOptionDialog


def QuickConnectDialog( settings, parent=None ):

    header = PrettyPanelHeader( u"Quick connect", QPixmap( ":/icon/connect" ) )

    mapper = SettingsWidgetMapper( settings )
    panel  = SettingsPanel( mapper )

    host_mapper = panel.addBoundRow( 'net.host', QLineEdit(), u"Server:" )

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
                                 title   = u"Quick connect" )

    return dialog

