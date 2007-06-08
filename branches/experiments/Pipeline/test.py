import sys
from Pipeline import *

def test( host, port ):
	
  pipe = Pipeline()
  pipe.addFilter( BaseFilter() )
  pipe.addFilter( EndLineFilter() )
  pipe.addFilter( UnicodeTextFilter() )
  
  def output( chunks ):
	  
    for chunk in chunks:
	    
      if chunk.chunktype == chunktypes.TEXT:
        sys.stdout.write( chunk.data.encode( "latin1" ) )
	
      elif chunk.chunktype == chunktypes.ENDOFLINE:
        sys.stdout.write( "\n" )
	
      elif chunk.chunktype == chunktypes.ENDOFPACKET:
        pass
      
      else: print chunk
      
  pipe.addSink( output )
  
  print "Begin..."
  
  import socket
  s=socket.socket()
  s.connect( ( host, port ) )
  s.settimeout( 1 )
  
  while True:
    while True:
	    
      try:
        buffer = s.recv(4096)
	
      except socket.timeout:
        break
      
      pipe.feedBytes(buffer)
      
    up=raw_input("> ")
    if up.strip(): s.sendall( up.strip() + "\r\n" )


test( sys.argv[ 1 ], int( sys.argv[ 2 ] ) )