##
## Logger.py
##
## Defines a Logger class that can be used to keep track of errors, warnings,
## etc, that take place inside the program.
## By default, the class only prints to stdout.
##


class Logger:

  def info( s, txt ):
    print "INFO:", txt

  def debug( s, txt ):
    print "DEBUG:", txt

  def warn( s, txt ):
    print "WARN:", txt

  def error( s, txt ):
    print "ERROR:", txt



logger = Logger()
