.. :doctest:

This module provides the ``ConfigBasket`` class for easy storage and retrieval
of hierarchal configuration keys.

>>> from ConfigBasket import ConfigBasket
>>> c = ConfigBasket()
>>> c[ 'key1' ] = 'TEST'
>>> print c[ 'key1' ]
TEST

Key names must be made of alphanumerical or underscore characters. A KeyError
is raised otherwise.

>>> c[ 'key?' ] = 'TEST'
Traceback (most recent call last):
    ...
KeyError: "Invalid key name 'key?'"

Configuration objects are hierarchal: an object can have children, and they
inherit its keys. Children of a base configuration object are considered as
*sections* of the configuration.

>>> cc = c.createAnonymousSection()
>>> type( cc ) is ConfigBasket
True
>>> print cc[ 'key1' ]
TEST

A section can override a configuration key from its parent:

>>> cc[ 'key1' ] = 'OTHER TEST'
>>> print cc[ 'key1' ]
OTHER TEST
>>> print c[ 'key1' ]
TEST

If a key is set on the child with the same value as propagated by the parent,
then the child forgets its instance of the key and uses that of the parent
instead.

>>> print cc.owns( 'key1' )
True
>>> cc[ 'key1' ] = 'TEST'  ## Same value as in parent.
>>> print cc.owns( 'key1' )
False

A section created with ``createAnonymousSection`` is part of the configuration
hierarchy as far as key propagation goes, but is otherwise detached from the
tree, and won't be saved. An anonymous section can thus, for instance, be
bound to a configuration dialog, and then applied on its parent when the
dialog is okay'ed.

>>> cc[ 'key1' ] = 'NEW TEST'
>>> print cc.isEmpty()
False
>>> print c[ 'key1' ]
TEST

>>> cc.commit()
>>> print c[ 'key1' ]
NEW TEST
>>> print cc.isEmpty()
True

A section created with ``createAnonymousSection`` can be attached into the
hierarchy later on:

>>> cc.saveAsSection( 'subsection' )
>>> print c.getSectionList()
['subsection']
>>> print c.getSection( 'subsection' ) is cc
True

This is equivalent to creating a named section right away:

>>> cc2 = c.createSection( 'subsection2' )
>>> print sorted( c.getSectionList() )
['subsection', 'subsection2']

You can test whether a key exists within a given hierachy. This is true if the
key is held by this object or any of its parents.

>>> print cc2.exists( 'key1' )
True
>>> print cc2.owns( 'key1' )
False

Sections can be renamed:

>>> c.renameSection( 'subsection2', 'testsection' )
>>> print sorted( c.getSectionList() )
['subsection', 'testsection']

And they can be deleted:

>>> c.deleteSection( 'testsection' )
>>> print 'testsection' in c.getSectionList()
False

Configuration trees can be imported and exported as dicts.

>>> c.getSection( 'subsection' )[ 'key2' ] = 'TEST 2'
>>> print c.dumpAsDict()
{'key1': 'NEW TEST', '@subsection': {'key2': 'TEST 2'}}

>>> del c, cc
>>> c = ConfigBasket.buildFromDict(
...   {'key': 'TEST 1', '@section1': {'key': 'TEST 2'}}
... )

>>> print c[ 'key' ]
TEST 1
>>> cc = c.getSection( 'section1' )
>>> print cc[ 'key' ]
TEST 2

Lastly, a configuration object can notify a callback when a key changes.

>>> def notifier( key, value ):
...   print "Notified: %s=%s" % ( key, value )

>>> cc.registerNotifier( notifier )

>>> cc[ 'key' ] = 'NEW VALUE'
Notified: key=NEW VALUE

Notifications are also propagated from parent to children:

>>> c[ 'otherkey' ] = 'OTHER VALUE'
Notified: otherkey=OTHER VALUE

This happens even if the child is anonymous:

>>> c.deleteSection( 'section1' )
>>> del cc
>>> c2 = c.createAnonymousSection()
>>> c2.registerNotifier( notifier )
>>> c[ 'newkey' ] = 'TEST'
Notified: newkey=TEST

Notifications are not emitted when the assigned value of a key doesn't change:

>>> c[ 'newkey' ] = 'TEST'

## Nothing happens -- the new value is identical to the old!

The callbacks are linked to with weak references, to ease garbage collection.

>>> del notifier
>>> c['key'] = 'YET ANOTHER VALUE'

## Nothing happens -- the notifier has been recycled!

>>> del c, c2



MetaDictProxy
-------------

The module also provides the ``MetaDictProxy`` metaclass, which makes the
items in a dict-like class accessible as underscore-prefixed attributes. It is
used internally in the implementation of ``ConfigBasket``.

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


WeakList
--------

The ``WeakList`` class functions as the usual WeakDictionary class from the
weakref module, only with a list. It is used internally in the implementation
of ``ConfigBasket``.

>>> from ConfigBasket import WeakList
>>> wl = WeakList()

>>> class Dummy: pass
>>> o = Dummy()
>>> wl.append( o )
>>> print len( wl )
1

>>> del o
>>> print len( wl )
0

>>> del wl, WeakList
