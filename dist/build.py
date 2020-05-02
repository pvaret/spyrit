#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import bz2
import base64
import os.path

from modulefinder import ModuleFinder
from typing import List
from typing import Text
from typing import Tuple


LAUNCHER_STUB = """\
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import bz2
import importlib.abc
import importlib.util
import sys

EMBEDDED_MODULES = %(modules)s


class EmbeddedModuleLoader( importlib.abc.SourceLoader ):

  def __init__( self, modules ):

    super( EmbeddedModuleLoader, self ).__init__()
    self.modules = modules
    self.sources = {}

  def get_filename( self, fullname ):

    if fullname not in self.modules:
      raise ImportError( fullname )

    path, data = self.modules[ fullname ]
    self.sources.setdefault(
        path, bz2.decompress( base64.decodebytes( data ) ) )
    return path

  def get_data( self, path ):

    return self.sources[ path ]


class EmbeddedModuleFinder( importlib.abc.MetaPathFinder ):

  def __init__( self, modules ):

    super( EmbeddedModuleFinder, self ).__init__()
    self.loader = EmbeddedModuleLoader( modules )
    self.modules = modules

  def find_spec( self, fullname, path, target=None ):

    # We cannot import __main__ because that's already the name of the launcher
    # stub module. So instead we import a module with a dummy name from the
    # toplevel, and replace that with __main__ once inside the embedded module
    # finder.
    if fullname == "@BOOTSTRAP@":
      fullname = "__main__"

    if fullname in self.modules:
      return importlib.util.spec_from_file_location(
          fullname, loader=self.loader )

    return None


sys.meta_path.append( EmbeddedModuleFinder( EMBEDDED_MODULES ) )
importlib.import_module( "@BOOTSTRAP@" )"""


def make_source_archive( filename: Text ) -> bytes:

  return base64.encodebytes( bz2.compress( open( filename, 'rb' ).read() ) )


def compile_module_dict( modules: List[ Tuple[ Text, Text ] ] ) -> Text:

  mods = []

  for ( modulename, filename ) in sorted( modules ):
    if not filename:
      continue

    bc = make_source_archive( filename )
    mods.append( "    %s: ( %s, b\"\"\"\\\n%s\"\"\" )"
                 % ( repr( modulename ),
                     repr( filename ),
                     bc.decode( "latin1" ) ) )

  return "{\n%s\n}" % ",\n".join( mods )


def make_launcher( modules: List[ Tuple[ Text, Text ] ] ):

  return LAUNCHER_STUB % { "modules": compile_module_dict( modules ) }


def build( inputname: Text, outputname: Text = None, verbose: bool = True ):

  dirname, scriptname = os.path.split( inputname )
  previous_dir = os.path.abspath( os.getcwd() )

  if dirname:
    os.chdir( dirname )

  mf = ModuleFinder( path=[ "." ] )
  mf.run_script( scriptname )

  # Type checking wrongly thinks that Module object have no __file__ or
  # __path__ attributes. :/
  libs: List[ Tuple[ Text, Text ] ]
  libs = [ ( name, mod.__file__ )  # type: ignore
           for ( name, mod ) in mf.modules.items() ]

  if verbose:
    mf.report()

  output = make_launcher( libs )
  os.chdir( previous_dir )

  if not outputname:
    print( output )

  else:
    open( outputname, "w" ).write( output )


def main():

  parser = argparse.ArgumentParser(
      description="Builds all of a Python script's Python dependencies into a "
                  "single Python file." )
  parser.add_argument( "input", metavar="INPUT.py",
                       help="the input python file" )
  parser.add_argument( "output", metavar="OUTPUT.py", nargs="?",
                       help="the output python file", default=None )
  parser.add_argument( "-v", "--verbose", action="store_true",
                       help="display information on the collected modules" )

  args = parser.parse_args()

  return build( args.input, args.output, args.verbose )


if __name__ == "__main__":
  main()
