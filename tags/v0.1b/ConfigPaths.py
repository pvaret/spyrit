##
## ConfigPaths.py
##
## Contains the code that figures out the paths used by this program depending
## on the OS.
##


import os

if os.name in ( 'posix', 'mac' ):

  HOME_DIR    = os.path.expanduser( "~" )
  CONFIG_DIR  = os.path.join( HOME_DIR,   ".spyrit" )
  CONFIG_FILE = os.path.join( CONFIG_DIR, "spyrit.conf" )

  if not os.path.exists( CONFIG_DIR ):

    try:
      os.mkdir( CONFIG_DIR )

    except IOError:
      pass
    

#elif os.name in ( 'nt,' ):
#  pass

else:
  raise NotImplementedError( "This program doesn't support your OS yet. Sorry!" )
