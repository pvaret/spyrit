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
## Singletons.py
##
## Contains the Singletons class, which manages on-demand loading of
## application-wide singletons.
##
## This file also defines an instance of Singletons called 'singletons', which
## can be used right away to register classes and return singletons.
##


class Singletons:

  def __init__( s, *items ):

    s._classes   = {}
    s._instances = {}

    for name, klass in items:
      s.addClass( name, klass )


  def addClass( s, name, klass ):

    assert klass not in s._classes.values()

    s._classes[ name ] = klass


  def __getattr__( s, name ):

    if name not in s._classes.keys():
      raise AttributeError( name )

    if name not in s._instances.keys():
      s._instances[ name ] = s._classes[ name ] ()

    return s._instances[ name ]


singletons = Singletons()
