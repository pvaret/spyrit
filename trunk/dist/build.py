#!/usr/bin/python
## -*- coding: utf-8 -*-

import sys
import imp
import bz2
import time
import struct
import marshal
import os.path


LAUNCHER_STUB = """#!/usr/bin/python
## -*- coding: utf-8 -*-

EMBEDDED_MODULES = {
%s
}


import sys
import imp
import bz2
import marshal


class embedded_module_importer:

  def find_module( s, fullname, path=None ):

    if fullname == "MAIN":
      fullname = "__main__"

    return EMBEDDED_MODULES.has_key( fullname ) and s or None


  def load_module( s, fullname ):

    if fullname == "MAIN":
      fullname = "__main__"

    filename, code = EMBEDDED_MODULES[ fullname ]
    code =  marshal.loads( bz2.decompress( code ) )

    mod = sys.modules.setdefault( fullname, imp.new_module( fullname ) )
    mod.__file__ = filename
    mod.__loader__ = s

    exec code in mod.__dict__

    return mod


sys.meta_path.append( embedded_module_importer() )

import MAIN
"""



def get_timestamp_long():
  return struct.pack( "l", long( time.time() ) )


def make_bytecode( filename ):

  m  = compile( file( filename ).read(), filename, 'exec' )
#  bc = imp.get_magic() + get_timestamp_long() + marshal.dumps( m )
  bc = bz2.compress( marshal.dumps( m ) )

  return bc


def make_module_dict( modules ):

  mods = []

  for ( modulename, f ) in modules:
    bc = make_bytecode( f )
    mods.append( "  %s: ( %s, %s )" % ( modulename.__repr__(), 
                                        f.__repr__(), 
                                        make_bytecode( f ).__repr__() ) )

  return ",\n".join( mods )


def make_launcher( main, modules ):

  return LAUNCHER_STUB % ( make_module_dict( modules ) )


def build( scriptname, outputname=None ):

  mainname, ext = os.path.splitext( scriptname )

  from modulefinder import ModuleFinder

  p = os.path.abspath( os.getcwd() )

  if os.path.dirname( scriptname ):
    os.chdir( os.path.dirname( scriptname ) )

  mf = ModuleFinder( [ "." ] )
  mf.run_script( os.path.basename( scriptname ) )

  libs = [ ( name, mod.__file__ ) for ( name, mod ) in mf.modules.iteritems()
                                  if mod.__file__ ]

  output = make_launcher( mainname, libs )

  os.chdir( p )

  if not outputname:
    print output

  else:
    file( outputname, "wb" ).write( output )


def main():

  if not len( sys.argv ) > 1:
    return

  if len( sys.argv ) > 2:
    build( sys.argv[1], sys.argv[2] )

  else:
    build( sys.argv[1] )


if __name__ == "__main__":
  main()
