:doctest:

This module provides the ``ConfigBasket`` class for easy storage and retrieval
of hierarchal configuration keys.

>>> from ConfigBasket import ConfigBasket
>>> c=ConfigBasket() 
>>> c['key1']='TEST'
>>> print c['key1']
TEST


It also provides the ``MetaDictProxy`` metaclass, which makes the items in a
dict-like class accessible as underscore-prefixed attributes:

>>> from ConfigBasket import MetaDictProxy

>>> class MyDictClass( dict ):
...   __metaclass__ = MetaDictProxy

>>> m = MyDictClass()
>>> m['test'] = 'TEST'
>>> print m._test
TEST

>>> m._test = 'TEST2'
>>> print m['test']
TEST2

>>> print 'test' in m
True
>>> del m._test
>>> print 'test' in m
False

>>> del MetaDictProxy, MyDictClass, m
