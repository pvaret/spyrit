# -*- coding: utf-8 -*-

## Copyright (c) 2002-2007 Pascal Varet <p.varet@gmail.com>
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
from Singletons        import singletons
from PrettyPanelHeader import PrettyPanelHeader


config = singletons.config


ABOUT = """
  <center><br/>
  <font size="+2"><b>%(NAME)s v%(VERSION)s</b></font><br/>
  <br/>
  "The light at the end of the tunnel may be an oncoming dragon. YAY!"<br/>
  <br/>
  This software is a beta version and as of yet incomplete, although it is
  already usable and, we hope, fast, stable and pleasant to use.<br/>
  <br/>
  Please stay tuned for further developments! We aim to release version 1.0
  within a few months, after adding the important features that are currently
  missing, namely logs, matches and highlights, and configuration dialogs for
  everything.<br/>
  <br/>
  %(NAME)s is &#169;2007 P. Varet, and licensed under the 
  <a href="http://www.gnu.org/licenses/old-licenses/gpl-2.0.html">GNU
  General Public License</a>.<br/>
  </center>
""" % dict( NAME=config._app_name, VERSION=config._app_version )


class AboutDialog( QtGui.QDialog ):

  def __init__( s, parent=None ):

    QtGui.QDialog.__init__( s, parent )

    s.setLayout( QtGui.QVBoxLayout( s ) )

    title = "About %s" % config._app_name

    s.setWindowTitle( title )

    header = PrettyPanelHeader( title, QtGui.QPixmap( ":/app/icon" ) )
    s.layout().addWidget( header )

    label = QtGui.QLabel( ABOUT )
    label.setWordWrap( True )
    label.setOpenExternalLinks( True )

    s.layout().addWidget( label )

    button = QtGui.QPushButton( "Ok" )
    s.layout().addWidget( button )
    s.layout().setAlignment( button, Qt.AlignHCenter )

    connect( button, SIGNAL( "clicked()" ), s, SLOT( "accept()" ) )


  @staticmethod
  def showDialog( parent=None ):

    return AboutDialog( parent ).exec_()
