##
## Helpers.py
##
## This file defines a number of helpers that add small and useful bits
## of functionality to the Python language.
##



## ---[ Function done() ]----------------------------------------------

def done():
  """
  def done()
  
  This is a convenience function. It simply raises StopIteration, so
  has to exit nicely from an iterator.
  """
  raise StopIteration




## ---[ endOfIterationMarker ]-----------------------------------------

## This object is used as a return value when the end of an iteration
## has been reached. It's essentially a None object, only more distinctive
## than None.

endOfIterationMarker = object()


## ---[ iter_and_peek_next() ]-----------------------------------------

def iter_and_peek_next(iterable):
  """
  Iterates over a sequence and yields both the current element and the next
  element of the sequence at each step. For the last element, None is returned
  as the next element.

  For instance:

  >>> for element, next in iter_and_peek_next([1, 2, 3]):
  ...   print (element, next)
  (1, 2)
  (2, 3)
  (3, None)
  """

  i = iter(iterable)

  last = i.next()

  for element in i:

    yield last, element
    last = element

  yield last, endOfIterationMarker
