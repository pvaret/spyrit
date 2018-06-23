#!/usr/bin/python
## -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

## Python 3 compatibility
from io import open

import sys
import imp
import bz2
import time
import struct
import base64
import marshal
import os.path


LAUNCHER_STUB = """\
#!/usr/bin/env python
## -*- coding: utf-8 -*-


EMBEDDED_MODULES = %(modules)s


import sys
import imp
import bz2
import base64


class embedded_module_importer:

  def find_module( self, fullname, path=None ):

    if fullname == "MAIN":
      fullname = "__main__"

    return self if fullname in EMBEDDED_MODULES else None


  def load_module( self, fullname ):

    if fullname == "MAIN":
      fullname = "__main__"

    filename, path, source = EMBEDDED_MODULES[ fullname ]
    source = bz2.decompress( base64.decodestring( source ) )
    code   = compile( source, filename, 'exec' )

    mod = sys.modules.setdefault( fullname, imp.new_module( fullname ) )
    mod.__file__ = filename
    mod.__loader__ = self
    if path:
      mod.__path__ = path

    exec( code, mod.__dict__ )

    return mod


sys.meta_path.append( embedded_module_importer() )

try:
  import MAIN
except KeyError:
  ## The name rewriting trick we do here confuses the Python 3 import machinery,
  ## which works but reports a spurious KeyError.
  pass
"""



def get_timestamp_long():

  return struct.pack( "l", int( time.time() ) )


def make_source_archive( filename ):

  return base64.encodestring( bz2.compress( open( filename, 'rb' ).read() ) )


#def make_bytecode( filename ):
#
#  m  = compile( open( filename, 'rb' ).read(), filename, 'exec' )
# #  bc = imp.get_magic() + get_timestamp_long() + marshal.dumps( m )
#  bc = bz2.compress( marshal.dumps( m ) )
#
#  return bc


def compile_module_dict( modules ):

  mods = []

  for ( modulename, filename, path ) in sorted( modules ):
    #bc = make_bytecode( filename )
    bc = make_source_archive( filename )
    mods.append( "  %s: ( %s, %s, %s )" % ( repr( modulename ),
                                            repr( filename ),
                                            repr( path or '' ),
                                            repr( bc ) ) )

  return "{\n%s\n}" % ",\n".join( mods )


def make_launcher( main, modules ):

  return LAUNCHER_STUB % { 'modules': compile_module_dict( modules ) }


def build( scriptname, outputname=None ):

  mainname, ext = os.path.splitext( scriptname )

  from modulefinder import ModuleFinder

  p = os.path.abspath( os.getcwd() )

  if os.path.dirname( scriptname ):
    os.chdir( os.path.dirname( scriptname ) )

  mf = ModuleFinder( [ "." ] )
  mf.run_script( os.path.basename( scriptname ) )

  libs = [ ( name, mod.__file__, mod.__path__ )
               for ( name, mod ) in mf.modules.items()
               if mod.__file__ ]

  output = make_launcher( mainname, libs )

  os.chdir( p )

  if not outputname:
    print( output )

  else:
    open( outputname, "wb" ).write( output )


def main():

  if not len( sys.argv ) > 1:
    return

  if len( sys.argv ) > 2:
    build( sys.argv[1], sys.argv[2] )

  else:
    build( sys.argv[1] )


if __name__ == "__main__":
  main()
