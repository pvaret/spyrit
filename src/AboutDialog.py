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
## AboutDialog.py
##
## This is our pretty about dialog! Well, not so pretty yet, but we'll improve
## it later.
##

from PyQt4.QtCore import Qt
from PyQt4.QtGui  import QLabel
from PyQt4.QtGui  import QPixmap
from PyQt4.QtGui  import QDialog
from PyQt4.QtGui  import QPushButton
from PyQt4.QtGui  import QTabWidget
from PyQt4.QtGui  import QVBoxLayout

from PrettyPanelHeader import PrettyPanelHeader


ABOUT = u"""\
<center><font size="+2">
  <b>%(app_name)s %(app_version)s</b></font><br/>
<br/>
"Endorsed by scientists!"</center>
<br/>
<br/>
%(app_name)s is a client for textual roleplaying games such as MUDs, MUSHes,
  MUCKs, MOOs and other M-acronyms.<br/>
<br/>
Though it is still in development and far from complete, it tries really hard
  to be polished and pleasant to use. Thank you for trying it out! Feedback and
  bug reports can be sent to
  <a href="mailto:spyrit-devel@lists.sourceforge.net">
  spyrit-devel@lists.sourceforge.net</a>.<br/>
<br/>
Technically minded users can follow the development on <a
  href="https://www.ohloh.net/p/spyrit">Ohloh</a> and get the latest source
  code from <a href="http://bitbucket.org/balinares/spyrit">BitBucket</a>.<br/>
<br/>
This software uses the <i><a
  href="http://code.activestate.com/recipes/473846/">winpath</a></i> module by
  Chris Arndt, and a modified version of Raymond Hettinger's <i><a
  href="http://pypi.python.org/pypi/ordereddict">OrderedDict</a></i>. Special
  characters imported from the <a href="http://dejavu.sourceforge.net/">DejaVu
  Sans Mono</a> font. Additional icons imported from the <a
  href="http://www.oxygen-icons.org/">Oxygen</a> set.<br/>
<br/>
%(app_name)s is &#169;2007-2011 P. Varet, and licensed under the
  <a href="http://www.gnu.org/licenses/old-licenses/gpl-2.0.html">GNU
  General Public License</a>.<br/>
"""


AUTHORS = u"""\
<b><font size="+2">Authors</font></b><br/>
<br/>
<b>Pascal Varet</b>: Project lead, code design, community management, Web site
  maintenance, pony wrangling.<br/>
<b>Clément Mairet</b>: Additional programming, spyrcc maintenance.<br/>
<br/>
<br/>
<b><font size="+2">Contributors</font></b><br/>
<br/>
<b>Matthew Groat</b>: Idea and initial patch for ANSI colors in logs and sound
  play on pattern match.<br/>
<b>Walter Vermeij</b>: Horse logo design.<br/>
<b>Griatch</b>: Review, server-side feedback.<br/>
"""


class AboutDialog( QDialog ):

  def __init__( self, config, parent=None ):

    QDialog.__init__( self, parent )

    self.setLayout( QVBoxLayout( self ) )

    min_size = config._mainwindow_min_size
    if len( min_size ) >= 2:
      self.setMinimumSize( min_size[0], min_size[1] )

    title = u"About %s" % config._app_name

    self.setWindowTitle( title )

    header = PrettyPanelHeader( title, QPixmap( ":/app/icon" ) )
    self.layout().addWidget( header )

    about = QLabel( ABOUT % config )
    about.setContentsMargins( 20, 20, 20, 20 )
    about.setWordWrap( True )
    about.setOpenExternalLinks( True )

    authors = QLabel( AUTHORS % config )
    authors.setContentsMargins( 20, 20, 20, 20 )
    authors.setWordWrap( True )
    authors.setOpenExternalLinks( True )

    tabwidget = QTabWidget()
    tabwidget.addTab( about, u"About" )
    tabwidget.addTab( authors, u"Credits" )
    self.layout().addWidget( tabwidget )

    button = QPushButton( u"Ok" )
    self.layout().addWidget( button )
    self.layout().setAlignment( button, Qt.AlignHCenter )

    button.clicked.connect( self.accept )
