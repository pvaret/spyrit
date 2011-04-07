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
## SettingsSchema.py
##
## Implements schemas that defines the layout of a settings object.
##

from fnmatch      import fnmatchcase
from SettingsNode import SettingsNode


class SettingsSchema( SettingsNode ):

  def __init__( self, definition=None ):

    SettingsNode.__init__( self )
    self.serializers = {}

    if definition:
      self.loadDefinition( definition )


  def loadDefinition( self, definition ):

    for path, serializer in definition.get( 'keys', () ):

      path = path.rstrip( '/' )

      node, key_pattern = self.getNodeKeyByPath( path, create_if_missing=True )

      ## Direct access to node.keys instead of going through __setitem__, so we
      ## can use special characters in the pattern.
      node.keys[ key_pattern ] = serializer.default
      node.serializers[ key_pattern ] = serializer

    for path, sub_definition in definition.get( 'sections', () ):

      sub_node = self.getNodeByPath( path, create_if_missing=True )

      inherit = sub_definition.get( 'inherit' )

      if inherit:
        inherit_node = self.getNodeByPath( inherit )
        sub_node.setParent( inherit_node )

      sub_node.loadDefinition( sub_definition )


  def __getitem__( self, key ):

    ## Attempt to match the key to a pattern:
    for pattern, value in self.keys.iteritems():
      if fnmatchcase( key, pattern ):
        return value

    ## Otherwise, fall back on default behavior.
    return SettingsNode.__getitem__( self, key )


  def getSerializer( self, key ):

    for pattern, value in self.serializers.iteritems():
      if fnmatchcase( key, pattern ):
        return value

    return None
