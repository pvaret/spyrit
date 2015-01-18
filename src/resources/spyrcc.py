#!/usr/bin/python
# -*- coding: utf-8 -*-

## Copyright (c) 2007-2015 Pascal Varet <p.varet@gmail.com>
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
## spyrcc.py
##
## Generates the resources.py file from a Qt Resource file, with more efficient
## storage.
##

import os
import sys
import time
import zlib

from xml.dom.minidom    import parse
from PyQt4              import QtCore

SPYRCC_MAJ   = 0
SPYRCC_MIN   = 9

TAG_RCC      = "RCC"
TAG_RESOURCE = "qresource"
TAG_FILE     = "file"

F_NOFLAGS    = 0x00
F_COMPRESSED = 0x01
F_DIRECTORY  = 0x02

HEADER = """## -*- coding: utf-8 -*-

## Resource object code
##
## Created: %s
##      by: The Spyrit Qt Resource Compiler v%d.%d
##
## WARNING! All changes made in this file will be lost!

import zlib

from PyQt4     import QtCore

"""

INIT_FUNCTIONS = """
_struct = zlib.decompress( qt_resource_struct.decode( "base64" ) )
_name   = zlib.decompress( qt_resource_name.decode(   "base64" ) )
_data   = zlib.decompress( qt_resource_data.decode(   "base64" ) )

def qInitResources():
    QtCore.qRegisterResourceData( 0x01, _struct, _name, _data )

def qCleanupResources():
    QtCore.qUnregisterResourceData( 0x01, _struct, _name, _data )

qInitResources()
"""

INIT_FUNCTIONS_LEGACY = """def qInitResources():
    QtCore.qRegisterResourceData( 0x01, qt_resource_struct, qt_resource_name, qt_resource_data )

def qCleanupResources():
    QtCore.qUnregisterResourceData( 0x01, qt_resource_struct, qt_resource_name, qt_resource_data )

qInitResources()
"""

class RCCFileInfo:

  def __init__( self, name, fDesc, locale, flags, opts={} ):

    ## Store resource data.

    self.flags  = flags
    self.name   = name
    self.fDesc  = fDesc
    self.locale = locale

    self.opts   = opts

    self.parent      = None
    self.children    = {}
    self.nameOffset  = 0
    self.dataOffset  = 0
    self.childOffset = 0


  def copy( self ):

    ## Return a deep copy of the object.

    c = RCCFileInfo( self.name, self.fDesc, self.locale, self.flags, self.opts )

    c.parent      = self.parent
    c.children    = self.children.copy()
    c.nameOffset  = self.nameOffset
    c.dataOffset  = self.dataOffset
    c.childOffset = self.childOffset

    return c


  def numberToStr( self, num, width ):

    ## Print out a number to a string in a binary format

    stg = ""
    div = 2 ** ( 8 * ( width - 1 ) )

    if self.opts.get( "legacy" ):
      fmt = "\\x%02x"

    else:
      fmt = "%c"

    while div >= 1:

      tmp  = num / div
      stg += fmt % tmp
      num -= tmp * div
      div /= 256

    return stg


  def writeDataBlob( self, offset ):

    ## Write file content and metadata

    self.dataOffset = offset

    try:
      data = self.fDesc.read()

    except:
      print "Couldn't read %s" % self.fDesc.name
      return False, ""

    ## TODO: compression stuff

    ## Length

    blob    = [ self.numberToStr( len( data ), 4 ) ]
    offset += 4

    if self.opts.get( "legacy" ):
      blob.append( "\\\n" )

    ## Binary data

    if self.opts.get( "legacy" ):
      for idx in range( len( data ) ):
        blob.append( self.numberToStr( ord( data[idx] ), 1 ) )

        ## This test should be done earlier as it produces an inelegant single
        ## first byte, but I want the exact same behavior as pyrcc.

        if not (idx % 16):
          blob.append( "\\\n" )

      blob.append( "\\\n" )

    else:
      for byte in data:
        blob.append( self.numberToStr( ord( byte ), 1 ) )

    offset += len( data )
    blob    = "".join( blob )

    return offset, blob


  def writeDataName( self, offset ):

    self.nameOffset = offset

    ## Length

    outName = [ self.numberToStr( len( self.name ), 2 ) ]
    offset += 2

    if self.opts.get( "legacy" ):
      outName.append( "\\\n" )

    ## Hash, we have no choice but to use a QString here

    outName.append( self.numberToStr( hash( QtCore.QString( self.name ) ), 4 ) )
    offset += 4

    if self.opts.get( "legacy" ):
      outName.append( "\\\n" )

    ## Name unicode string

    if self.opts.get( "legacy" ):
      uname = unicode( self.name )

      for idx in range( len( uname ) ):
        outName.append( self.numberToStr( ord( uname[idx] ), 2 ) )

        ## This test should be done earlier and use modulo 8 to avoid an
        ## inelegant single first word and unclean wrapping,
        ## but I want the exact same behavior as pyrcc.

        if not (idx % 16):
          outName.append( "\\\n" )

      outName.append( "\\\n" )

    else:
      outName += [ self.numberToStr( ord( c ), 2 ) for c in unicode( self.name ) ]

    offset  += len( self.name ) * 2

    outName  = "".join( outName )

    return offset, outName


  def writeDataInfo( self ):

    ## Pointer data
    ## Name offset

    info = [ self.numberToStr( self.nameOffset, 4 ) ]

    ## Flags

    info.append( self.numberToStr( self.flags, 2 ) )

    if self.flags & F_DIRECTORY:

      ## Child count

      info.append( self.numberToStr( len( self.children ), 4 ) )

      ## First child offset

      info.append( self.numberToStr( self.childOffset, 4 ) )

    else:

      ## Locale

      info.append( self.numberToStr( self.locale.country(), 2 ) )
      info.append( self.numberToStr( self.locale.language(), 2 ) )

      ## Data offset

      info.append( self.numberToStr( self.dataOffset, 4 ) )

    if self.opts.get( "legacy" ):
      info.append( "\\\n" )

    return "".join( info )


class RCCResourceLibrary:

  ## Python version of PyRCC resource library object

  def __init__( self, qrcFiles, opts={} ):

    self.qrcFiles  = qrcFiles
    self.opts      = opts

    self.root      = None

    self.parseResourceFiles()


  def parseResourceFiles( self ):

    ## Open .qrc files and build the list of resources to compile

    for qrc in self.qrcFiles:

      ## Figure out file type and working directory

      if qrc == "-":

        qrc = sys.stdin
        pwd = os.getcwdu()

      else:

        try:
          f   = file( qrc, "r" )
          pwd = os.path.join( os.getcwdu(), os.path.dirname( qrc ) )

        except:
          print >> sys.stderr, "Unable to open file %s" % qrc
          continue

      qrcDom = parse( f ).firstChild

      ## Reach RCC tag first

      while qrcDom:

        if qrcDom.nodeType == qrcDom.ELEMENT_NODE and qrcDom.tagName == TAG_RCC:
          break

        qrcDom = qrcDom.nextSibling

      child = qrcDom.firstChild

      while child:

        if child.nodeType != child.ELEMENT_NODE:
          child = child.nextSibling
          continue

        if child.nodeName == TAG_RESOURCE:

          lang   = child.getAttribute( "lang" ) or "C"
          prefix = child.getAttribute( "prefix" )

          prefix = "/" + prefix.strip( "/" ) + "/"

          ## Now, handle files for this resource path

          res = child.firstChild

          while res:

            if res.nodeType != res.ELEMENT_NODE or res.tagName != TAG_FILE:
              res = res.nextSibling
              continue

            filename = res.firstChild.data
            if not filename:
              print >> sys.stderr, "Warning: Null node in XML"

            alias = res.getAttribute( "alias" ) or filename

            ## Clean up alias if we got it from filename

            alias = os.path.normpath( alias ).lstrip( "../" )
            alias = prefix + alias

            ## Add file content to our RCC Library now, taking working
            ## directory into account

            filename = os.path.join( pwd, filename )

            try:
              f = file( filename, "rb" )

            except:
              print >> sys.stderr, "Cannot find file: %s" %  filename
              res = res.nextSibling
              continue

            ## Handle next file for this resource path until we run out
            ## TODO: handle directories

            self.addFile( alias, RCCFileInfo( alias.split( '/' )[-1], f,
                       QtCore.QLocale( lang ), F_NOFLAGS, self.opts ) )
            res = res.nextSibling

        child = child.nextSibling


  def addFile( self, alias, rccFile ):

    ## Adds RCC file to our resource tree. We just need to add our provided
    ## rccFile node to that tree, creating intermediate 'directory' nodes in
    ## the process if needed.

    ## Check file size beforehand

    if os.fstat( rccFile.fDesc.fileno() ).st_size > 0xFFFFFFFFL:
      print >> sys.stderr, "File too big: %s" % rccFile.fDesc.name
      return False

    if not self.root:
      self.root = RCCFileInfo( "", None, None, F_DIRECTORY, self.opts )

    parent = self.root
    nodes  = alias.split( "/" )

    ## Traverse our resource tree to the last leaf of alias and create
    ## 'subdirs' on the fly if needed

    for node in nodes[1:-1]:

      if node not in parent.children:

        nodeInfo = RCCFileInfo( node, None, None, F_DIRECTORY, self.opts )
        nodeInfo.parent = parent
        parent.children[node] = nodeInfo
        parent = nodeInfo

      else:
        parent = parent.children[node]

    filename = nodes[-1]
    nodeInfo = rccFile.copy()
    nodeInfo.parent = parent

    parent.children[filename] = nodeInfo

    return True


  def writeHeader( self, out = sys.stdout ):

    ## Print python header

    try:
      print >> out, HEADER % ( time.ctime(), SPYRCC_MAJ, SPYRCC_MIN )

    except:
      return False

    return True


  def writeDataBlobs( self, out = sys.stdout ):

    ## Print data structure

    if not self.root:
      return False

    pending = [ self.root ]
    offset  = 0
    blobs   = []

    while pending:

      fileInfo = pending.pop()

      for alias, child in fileInfo.children.items():

        if child.flags & F_DIRECTORY:
          pending.append( child )

        else:
          offset, outBlob = child.writeDataBlob( offset )
          blobs.append( outBlob )

    ## Reduce our data size before printing it to be a bit more efficient
    ## than the original PyRCC

    blobs = "".join( blobs )

    if self.opts.get( "legacy" ):
      print >> out, 'qt_resource_data = "\\\n%s"\n' % blobs

    else:
      blobs = zlib.compress( blobs, 9 ).encode( "base64" )
      print >> out, 'qt_resource_data = """\n%s"""\n' % blobs


    return True


  def writeDataNames( self, out = sys.stdout ):

    ## Print names structure

    if not self.root:
      return False

    names    = {}
    pending  = [ self.root ]
    offset   = 0
    strNames = []

    while pending:

      fileInfo = pending.pop()

      for child in fileInfo.children.values():

        if child.flags & F_DIRECTORY:
          pending.append( child )

        if child.name in names:
          child.nameOffset = names[child.name]

        else:
          names[child.name] = offset
          offset, outNames = child.writeDataName( offset )
          strNames.append( outNames )

    ## Reduce our data size before printing it to be a bit more efficient
    ## than the original PyRCC

    strNames = "".join( strNames )

    if self.opts.get( "legacy" ):
      print >> out, 'qt_resource_name = "\\\n%s"\n' % strNames

    else:
      strNames = zlib.compress( strNames, 9 ).encode( "base64" )
      print >> out, 'qt_resource_name = """\n%s"""\n' % strNames

    return True


  def cmpHashName( self, left, right ):

    ## Comparison function actually comparing the hash of two nodes' names

    leftName  = hash( QtCore.QString( left.name ) )
    rightName = hash( QtCore.QString( right.name ) )

    return leftName < rightName and -1 or leftName > rightName


  def writeDataStructure( self, out = sys.stdout ):

    ## Print final Qt data  structure

    if not self.root:
      return False

    pending  = [ self.root ]
    offset   = 1
    structs  = []

    ## Calculate the child offsets (flat)

    while pending:

      fileInfo = pending.pop()
      fileInfo.childOffset = offset

      ## Sort children by hash before adding them to the structure

      children = fileInfo.children.values()
      children.sort( self.cmpHashName )

      ## Keep looping until we get to leaf nodes, and update offsets

      for child in children:

        offset +=1

        if child.flags & F_DIRECTORY:
          pending.append( child )

    ## Now write out the structure (iterate with our new offsets)

    pending = [ self.root ]
    structs.append( self.root.writeDataInfo() )

    while pending:

      fileInfo = pending.pop()

      ## Sort children by hash before adding them to the structure

      children = fileInfo.children.values()
      children.sort( self.cmpHashName )

      ## Write out actual data now

      for child in children:

        structs.append( child.writeDataInfo() )

        if child.flags & F_DIRECTORY:
          pending.append( child )

    structs = "".join( structs )

    if self.opts.get( "legacy" ):
      print >> out, 'qt_resource_struct = "\\\n%s"\n' % structs

    else:
      structs = zlib.compress( structs, 9 ).encode( "base64" )
      print >> out, 'qt_resource_struct = """\n%s"""\n' % structs

    return True


  def writeInitializer( self, out = sys.stdout ):

    ## Print python header

    try:
      if self.opts.get( "legacy" ):
        print >> out, INIT_FUNCTIONS_LEGACY

      else:
        print >> out, INIT_FUNCTIONS

    except:
      return False

    return True


  def output( self, out = sys.stdout ):

    ## Print out compiled resource file

    if self.opts.get( "verbose" ):
        print >> sys.stderr, "Outputting code."

    if not self.writeHeader( out ):
        print >> sys.stderr, "Couldn't write header!"
        return False

    if not self.writeDataBlobs( out ):
        print >> sys.stderr, "Couldn't write data blob!"
        return False

    if not self.writeDataNames( out ):
        print >> sys.stderr, "Couldn't write file names!"
        return False

    if not self.writeDataStructure( out ):
        print >> sys.stderr, "Couldn't write data tree!"
        return False

    if not self.writeInitializer( out ):
        print >> sys.stderr, "Couldn't write footer!"
        return False

    return True



def main():

  ## Check command-line arguments and get things started
  ## TODO: parse options

  outFile   = None
  debug     = False
  compress  = False
  cmpThres  = 70
  encode    = True
  qrcFiles  = []
  extraOpts = {}

  ## Handle command-line options here

  from optparse import OptionParser

  parser = OptionParser( usage="%prog [options] <QRC files>",
                         version="Spyrit Qt Resource Compiler v%d.%d" \
                                 % ( SPYRCC_MAJ, SPYRCC_MIN ) )

  parser.add_option( "-o", "--out", dest="outFileName",
                     help="output to FILE rather than stdout",
                     metavar="FILE" )

  parser.add_option( "-l", "--legacy", action="store_true", dest="legacyMode",
                     default=False, help="generate legacy pyrcc4 code" )

  parser.add_option( "-v", "--verbose", action="store_true", dest="verbose",
                     default=False, help="extra output to stderr" )

  options, args = parser.parse_args()

  if not args:
    parser.error( "No QRC file provided!" )

  outFileName          = options.outFileName
  extraOpts['legacy']  = options.legacyMode
  extraOpts['verbose'] = options.verbose

  for arg in args:

    if os.path.exists( arg ):
      qrcFiles.append( arg )

    else:
      parser.error( "File %s doesn't exist!" % arg )

  rcl = RCCResourceLibrary( args, extraOpts )

  if not outFileName:
    outFile = sys.stdout

  else:

    try:
      outFile = file( outFileName, "w" )

    except IOError:
      print "Unable to open %s for writing!" % outFileName
      sys.exit()

  rcl.output( outFile )

  ## Tidy up

  if outFile != sys.stdout:
    outFile.close()


if __name__ == "__main__":
  main()
