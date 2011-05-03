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
## SettingsNodeContainer.py
##
## Implements a specific Settings node that serves as a container for other
## nodes.
##

u"""
:doctest:

>>> from SettingsNodeContainer import *

"""


from SettingsNode import SettingsNode


class SettingsNodeContainer( SettingsNode ):
  """
  A specific SettingsNode that does nothing on its own and just contains other
  nodes.

  Attempts to set keys on a SettingsNodeContainer raise a TypeError.

  """

  def __init__( self, parent=None ):

    SettingsNode.__init__( self, parent )

    self.new_sections_inherit_from = None


  def __getitem__( self, key ):

    return self.section( key )


  def __setitem__( self, key, value ):

    if self.SEP in key:
      section, key = key.split( self.SEP, 1 )
      self.section( section )[ key ] = value
      return

    raise TypeError( "Container nodes can't hold keys!" )


  def __delitem__( self, key ):

    if self.SEP in key:
      section, key = key.split( self.SEP, 1 )
      del self.section( section )[ key ]
      return

    raise KeyError( key )


  def __contains__( self, key ):

    if self.SEP in key:
      section, key = key.split( self.SEP, 1 )
      return key in self.section( section )

    raise KeyError( key )


  def section( self, name ):

    if name in self.sections:
      return self.sections[ name ]

    if self.new_sections_inherit_from:
        parent = self.new_sections_inherit_from

    elif self.parent:
      parent = self.parent.section( name )  ## may raise KeyError

    else:
      raise KeyError( u"No such section", name )

    ## New subsections in containers are SettingsNode. Compare with
    ## SettingsNode.section(), where new subsections are created with the
    ## node's specific class, which may be different (SettingsSchema for
    ## instance). Not yet sure this is a good idea.

    subsection = self.sections[ name ] = SettingsNode()

    if self.label:
      subsection.label = self.label

    subsection.setParent( parent )

    return subsection
