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

from PyQt4.QtGui import QPixmap, QWidget, QFormLayout
from PyQt4.QtGui import QLineEdit, QSpinBox, QCheckBox

from Utilities            import check_ssl_is_available
from PrettyPanelHeader    import PrettyPanelHeader
from PrettyOptionDialog   import PrettyOptionDialog
from SettingsWidgetMapper import SettingsWidgetMapper


class Panel( QWidget ):

  def __init__( self, mapper ):

    QWidget.__init__( self )
    self.setLayout( QFormLayout() )

    self.mapper = mapper


  def addBoundRow( self, node_path, widget, label=None ):

    self.layout().addRow( label, widget )
    return self.mapper.bind( node_path, widget )


def NewWorldDialog( settings, parent=None ):

    header = PrettyPanelHeader( u"New world", QPixmap( ":/icon/new_world" ) )

    mapper = SettingsWidgetMapper( settings )
    panel  = Panel( mapper )

    panel.addBoundRow( '/name', QLineEdit(), u"World name:" )
    panel.addBoundRow( '/net/host', QLineEdit(), u"Server:" )

    port = QSpinBox()
    port.setRange( 1, 65535 )
    panel.addBoundRow( '/net/port', port, u"Port:" )


    if check_ssl_is_available():
      panel.addBoundRow( '/net/ssl', QCheckBox( u"Use SSL &encryption" ) )

    dialog = PrettyOptionDialog( mapper,
                                 panel,
                                 parent  = parent,
                                 header  = header,
                                 oklabel = u"Connect",
                                 title   = u"New world" )

    return dialog

