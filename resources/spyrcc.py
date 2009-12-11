#!/usr/bin/python
# -*- coding: utf-8 -*-

## Copyright (c) 2007-2009 Pascal Varet <p.varet@gmail.com>
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

import sys
import os
import time
import zlib

from xml.dom.minidom    import parse
from PyQt4              import QtCore

SPYRCC_MAJ   = 0
SPYRCC_MIN   = 8

TAG_RCC      = "RCC"
TAG_RESOURCE = "qresource"
TAG_FILE     = "file"

F_NOFLAGS    = 0x00
F_COMPRESSED = 0x01
F_DIRECTORY  = 0x02

HEADER = """# -*- coding: utf-8 -*-

# Resource object code
#
# Created: %s
#      by: The Spyrit Qt Resource Compiler v%d.%d
#
# WARNING! All changes made in this file will be lost!

import zlib

from encodings import base64_codec
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


class RCCFileInfo:

  def __init__( s, name, fDesc, locale, flags ):

    ## Store resource data

    s.flags  = flags
    s.name   = name
    s.fDesc  = fDesc
    s.locale = locale

    s.parent      = None
    s.children    = {}
    s.nameOffset  = 0
    s.dataOffset  = 0
    s.childOffset = 0


  def copy( s ):

    ## Return a deep copy of the object

    c = RCCFileInfo( s.name, s.fDesc, s.locale, s.flags )

    c.parent      = s.parent
    c.children    = s.children.copy()
    c.nameOffset  = s.nameOffset
    c.dataOffset  = s.dataOffset
    c.childOffset = s.childOffset

    return c


  def numberToStr( s, num, width ):

    ## Print out a number to a string in a binary format

    stg = ""
    div = 1

    if width == 2:
      div = 256

    elif width == 3:
      div = 65536

    elif width == 4:
      div = 16777216

    while div >= 1:

      tmp  = num / div
      stg += "%c" % tmp
      num -= tmp * div
      div /= 256

    return stg


  def writeDataBlob( s, offset ):

    ## Write file content and metadata

    s.dataOffset = offset

    try:
      data = s.fDesc.read()

    except:
      print "Couldn't read %s" % s.fDesc.name
      return False, ""

    ## TODO: compression stuff

    ## Length

    blob    = [ s.numberToStr( len( data ), 4 ) ]
    offset += 4

    ## Binary data

    for byte in data:
      blob.append( "%c" % byte )

    offset += len( data )
    blob    = "".join( blob )

    return offset, blob


  def writeDataName( s, offset ):

    s.nameOffset = offset

    ## Length

    outName = [ s.numberToStr( len( s.name ), 2 ) ]
    offset += 2

    ## Hash, we have no choice but to use a QString here

    outName.append( s.numberToStr( hash( QtCore.QString( s.name ) ), 4 ) )
    offset += 4

    ## Name unicode string

    outName += [ s.numberToStr( ord( c ), 2 ) for c in unicode( s.name ) ]
    offset  += len( s.name ) * 2

    outName  = "".join( outName )

    return offset, outName


  def writeDataInfo( s ):

    ## Pointer data
    ## Name offset

    info = [ s.numberToStr( s.nameOffset, 4 ) ]

    ## Flags

    info.append( s.numberToStr( s.flags, 2 ) )

    if s.flags & F_DIRECTORY:

      ## Child count

      info.append( s.numberToStr( len( s.children ), 4 ) )

      ## First child offset

      info.append( s.numberToStr( s.childOffset, 4 ) )

    else:

      ## Locale

      info.append( s.numberToStr( s.locale.country(), 2 ) )
      info.append( s.numberToStr( s.locale.language(), 2 ) )

      ## Data offset

      info.append( s.numberToStr( s.dataOffset, 4 ) )

    return "".join( info )


class RCCResourceLibrary:

  ## Python version of PyRCC resource library object

  def __init__( s, qrcFiles = [] ):

    s.qrcFiles  = qrcFiles
    s.verbose   = False

    s.root      = None

    s.parseResourceFiles()


  def parseResourceFiles( s ):

    ## Open .qrc files and build the list of resources to compile

    for qrc in s.qrcFiles:

      ## Figure out file type and working directory

      if qrc == "-":

        qrc = sys.stdin
        pwd = os.getcwdu()

      else:

        try:
          f   = file( qrc, "r" )
          pwd = os.path.join( os.getcwdu(), os.path.dirname( qrc ) )

        except:
          print "Unable to open file %s" % qrc
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

        if   child.nodeName == TAG_RESOURCE:

          lang   = child.getAttribute( "lang" ) or "C"
          prefix = child.getAttribute( "prefix" )

          if not prefix.startswith( "/" ):
            prefix = "/" + prefix

          if not prefix.endswith( "/" ):
            prefix += "/"

          ## Now, handle files for this resource path

          res = child.firstChild

          while res:

            if res.nodeType != res.ELEMENT_NODE or res.tagName != TAG_FILE:
              res = res.nextSibling
              continue

            filename = res.firstChild.data
            if not filename:
              print "Warning: Null node in XML"

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
              print "Cannot find file: %s" %  filename
              res = res.nextSibling
              continue

            ## Handle next file for this resource path until we run out
            ## TODO: handle directories

            s.addFile( alias, RCCFileInfo( alias.split( '/' )[-1], f,
                       QtCore.QLocale( lang ), F_NOFLAGS ) )

            res = res.nextSibling

        child = child.nextSibling


  def addFile( s, alias, rccFile ):

    ## Adds RCC file to our resource tree. We just need to add our provided
    ## rccFile node to that tree, creating intermediate 'directory' nodes in
    ## the process if needed.

    ## Check file size beforehand

    if os.fstat( rccFile.fDesc.fileno() ).st_size > 0xFFFFFFFFL:
      print "File too big: %s" % rccFile.fDesc.name
      return False

    if not s.root:
      s.root = RCCFileInfo( "", None, None, F_DIRECTORY )

    parent = s.root
    nodes  = alias.split( "/" )

    ## Traverse our resource tree to the last leaf of alias and create
    ## 'subdirs' on the fly if needed

    for node in nodes[1:-1]:

      if node not in parent.children:

        nodeInfo = RCCFileInfo( node, None, None, F_DIRECTORY )
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


  def writeHeader( s, out = sys.stdout ):

    ## Print python header

    try:
      print >> out, HEADER % ( time.ctime(), SPYRCC_MAJ, SPYRCC_MIN )

    except:
      return False

    return True


  def writeDataBlobs( s, out = sys.stdout ):

    ## Print data structure

    if not s.root:
      return False

    pending = [ s.root ]
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
    blobs = zlib.compress( blobs, 9 ).encode( "base64" )
    print >> out, "qt_resource_data = \"\"\"\n%s\"\"\"\n" % blobs

    return True


  def writeDataNames( s, out = sys.stdout ):

    ## Print names structure

    if not s.root:
      return False

    names    = {}
    pending  = [ s.root ]
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
          offset, outNames = child.writeDataName( offset )
          strNames.append( outNames )
          names[child.name] = offset

    ## Reduce our data size before printing it to be a bit more efficient
    ## than the original PyRCC

    strNames = "".join( strNames )
    strNames = zlib.compress( strNames, 9 ).encode( "base64" )
    print >> out, "qt_resource_name = \"\"\"\n%s\"\"\"\n" % strNames

    return True


  def cmpHashName( s, left, right ):

    ## Comparison function actually comparing the hash of two nodes' names

    leftName  = hash( QtCore.QString( left.name ) )
    rightName = hash( QtCore.QString( right.name ) )

    return leftName < rightName and -1 or leftName > rightName


  def writeDataStructure( s, out = sys.stdout ):

    ## Print final Qt data  structure

    if not s.root:
      return False

    pending  = [ s.root ]
    offset   = 1
    structs  = []

    ## Calculate the child offsets (flat)

    while pending:

      fileInfo = pending.pop()
      fileInfo.childOffset = offset

      ## Sort children by hash before adding them to the structure

      children = fileInfo.children.values()
      children.sort( s.cmpHashName )

      ## Keep looping until we get to leaf nodes, and update offsets

      for child in children:

        offset +=1

        if child.flags & F_DIRECTORY:
          pending.append( child )

    ## Now write out the structure (iterate with our new offsets)

    pending = [ s.root ]
    structs.append( s.root.writeDataInfo() )

    while pending:

      fileInfo = pending.pop()

      ## Sort children by hash before adding them to the structure

      children = fileInfo.children.values()
      children.sort( s.cmpHashName )

      ## Write out actual data now

      for child in children:

        structs.append( child.writeDataInfo() )

        if child.flags & F_DIRECTORY:
          pending.append( child )

    structs = "".join( structs )
    structs = zlib.compress( structs, 9 ).encode( "base64" )

    print >> out, "qt_resource_struct = \"\"\"\n%s\"\"\"\n" % structs

    return True


  def writeInitializer( s, out = sys.stdout ):

    ## Print python header

    try:
      print >> out, INIT_FUNCTIONS

    except:
      return False

    return True


  def output( s, out = sys.stdout ):

    ## Print out compiled resource file

    if s.verbose:
        print "Outputting code"

    if not s.writeHeader( out ):
        print "Couldn't write header"
        return False

    if not s.writeDataBlobs( out ):
        print "Couldn't write data blob"
        return False

    if not s.writeDataNames( out ):
        print "Couldn't write file names"
        return False

    if not s.writeDataStructure( out ):
        print "Couldn't write data tree"
        return False

    if not s.writeInitializer( out ):
        print "Couldn't write footer"
        return False

    return True


def usage( err = "" ):

  ## SpyRCC help

  print "Spyrit Qt Resource Compiler v%d.%d" % ( SPYRCC_MAJ, SPYRCC_MIN )

  if err:
    print "%s: %s" % ( sys.argv[0], err )

  print "Usage: %s  [options] <inputs>\n\n" \
        "Options:\n" \
        "\t-o file           Write output to file rather than stdout\n" \
        "\t-name name        Create an external initialization function with name\n" \
        "\t-threshold level  Threshold to consider compressing files\n" \
        "\t-compress level   Compress input files by level\n" \
        "\t-root path        Prefix resource access path with root path\n" \
        "\t-no-compress      Disable all compression\n" \
        "\t-version          Display version\n" \
        "\t-help             Display this information\n" % sys.argv[0]


def main():

  ## Check command-line arguments and get things started
  ## TODO: parse options

  outFile  = None
  debug    = False
  compress = False
  cmpThres = 70
  encode   = True
  qrcFiles = []
  errMsg   = ""

  ## Handle command-line options here

  for i in range( len( sys.argv[1:] ) ):

    if sys.argv[i].startswith( "-" ):

      opt = sys.argv[i][1:]

      if opt == "o":

        if not i < len( sys.argv ):
          errMsg = "Missing output name"
          break

        i += 1
        outFileName = sys.argv[i]

    else:

      if os.path.exists( sys.argv[i] ):
        qrcFiles.append( sys.argv[i] )

      else:
        errMsg = "File %s doesn't exist" % sys.argv[i]
        break


  if errMsg or len( sys.argv ) < 2:
    usage( errMsg )

  else:
    rcl = RCCResourceLibrary( sys.argv[1:] )

    if not outFile:
      outFile = sys.stdout

    else:

      try:
        outFile = open( outFileName, "w" )

      except:
        print "Unable to open %s for writing" % outFileName

    rcl.output( outFile )

    ## Tidy up

    if outFile != sys.stdout:
      outFile.close()


if __name__ == "__main__":
  main()
