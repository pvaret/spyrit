# -*- coding: utf-8 -*-

## Copyright (c) 2007-2010 Pascal Varet <p.varet@gmail.com>
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
## AboutDialog.py
##
## This is our pretty about dialog! Well, not so pretty yet, but we'll improve
## it later.
##

from localqt           import *
from PrettyPanelHeader import PrettyPanelHeader


ABOUT = u"""
  <center><br/>
  <font size="+2"><b>%(app_name)s v%(app_version)s</b></font><br/>
  <br/>
  "Still alive!"<br/>
  <br/>
  This software is a beta version and as of yet incomplete, although it is
  already usable and, we hope, fast, stable and pleasant to use.<br/>
  <br/>
  Please stay tuned for further developments! We aim to release version 1.0
  within a few months, after adding the important features that are currently
  missing, namely matches, highlights and such, and configuration dialogs for
  everything.<br/>
  <br/>
  %(app_name)s is &#169;2007-2010 P. Varet, and licensed under the
  <a href="http://www.gnu.org/licenses/old-licenses/gpl-2.0.html">GNU
  General Public License</a>.<br/>
  <br/>
  This software uses the
  <i><a href="http://code.activestate.com/recipes/473846/">winpath</a></i>
  module by Chris Arndt.<br/>
  Dingbat symbols imported from the
  <a href="http://dejavu.sourceforge.net/">DejaVu Sans Mono</a> font.<br/>
  Horse logo contributed by
  <a href="http://waltervermeij.blogspot.com/">Walter Vermeij</a>.
  </center>
  <br/>
  <br/>
"""


class AboutDialog( QtGui.QDialog ):

  def __init__( s, config, parent=None ):

    QtGui.QDialog.__init__( s, parent )

    s.setLayout( QtGui.QVBoxLayout( s ) )

    min_size = config._mainwindow_min_size
    if len( min_size ) >= 2: s.setMinimumSize( min_size[0], min_size[1] )

    title = u"About %s" % config._app_name

    s.setWindowTitle( title )

    header = PrettyPanelHeader( title, QtGui.QPixmap( ":/app/icon" ) )
    s.layout().addWidget( header )

    label = QtGui.QLabel( ABOUT % config )
    label.setWordWrap( True )
    label.setOpenExternalLinks( True )

    s.layout().addWidget( label )

    button = QtGui.QPushButton( u"Ok" )
    s.layout().addWidget( button )
    s.layout().setAlignment( button, Qt.AlignHCenter )

    connect( button, SIGNAL( "clicked()" ), s, SLOT( "accept()" ) )
