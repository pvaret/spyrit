. :doctest:

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

>>> cc = ConfigBasket()
>>> cc.setParent( c )
>>> print cc[ 'key1' ]
TEST

A section can override a configuration key from its parent:

>>> cc[ 'key1' ] = 'OTHER TEST'
>>> print cc[ 'key1' ]
OTHER TEST
>>> print c[ 'key1' ]
TEST

A configuration object's own keys can be obtained without inheritance using the
get() method:

>>> c[ 'key2' ] = 'SECOND TEST'
>>> print c.get( 'key2' )
SECOND TEST
>>> print cc.get( 'key2' )
None

get() also takes a default argument:

>>> print c.get( 'missing_key', 'THIS KEY IS MISSING' )
THIS KEY IS MISSING

If a key is set on the child with the same value as propagated by the parent,
then the child forgets its instance of the key and uses that of the parent
instead.

>>> cc[ 'key1' ] = 'TEST'  ## Same value as in parent.
>>> print cc.get( 'key1' )
None

For the sake of easing the creation of configuration dialogs, the values of a
configuration object can be applied to its parent:

>>> temp_config = ConfigBasket( c )  ## This is the same as creating it without
...                                  ## arguments and calling
...                                  ## temp_config.setParent( c ) later.

>>> temp_config[ 'key1' ] = 'NEW TEST'
>>> print temp_config.isEmpty()
False
>>> print c[ 'key1' ]
TEST

>>> temp_config.apply()
>>> print c[ 'key1' ]
NEW TEST
>>> print temp_config.isEmpty()
True

You can test whether a key exists within a given object.

>>> print 'key1' in c
True

This tests the object alone, not its whole hierarchy:

>>> print 'key1' in cc
False

Subsections can be created with an explicit name:

>>> subsection = c.section( 'subsection', create=True )

They can then be accessed as keys on their parent object:

>>> c[ 'subsection' ] is subsection
True

>>> c[ 'subsection' ][ 'key1' ] = 'YET ANOTHER TEST'
>>> print subsection[ 'key1' ]
YET ANOTHER TEST

But subsections are also automatically inherited by children:

>>> print cc[ 'subsection' ][ 'key1' ]
YET ANOTHER TEST

Lastly, a configuration object can notify a callback when a key changes.

>>> def notifier( key, value ):
...   print "Notified: %s=%s" % ( key, value )

>>> cc.registerNotifier( notifier )

>>> cc[ 'key' ] = 'NEW VALUE'
Notified: key=NEW VALUE

Notifications are also propagated from parent to children:

>>> c[ 'otherkey' ] = 'OTHER VALUE'
Notified: otherkey=OTHER VALUE

Notifications are not emitted when the assigned value of a key doesn't change:

>>> c[ 'otherkey' ] = 'OTHER VALUE'
>>> ## Nothing happens -- the new value is identical to the old!

The callbacks are linked to with weak references, to ease garbage collection.

>>> del notifier
>>> c[ 'key' ] = 'YET ANOTHER VALUE'
>>> ## Nothing happens -- the notifier has been recycled!

>>> del c, cc, temp_config



DictAttrProxy
-------------

The module also provides the ``DictAttrProxy`` class, which makes the items in
a dict-like subclass accessible as underscore-prefixed attributes. It is used
internally in the implementation of ``ConfigBasket``.

>>> from ConfigBasket import DictAttrProxy

>>> class MyDictClass( dict, DictAttrProxy ):
...   pass

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

>>> del DictAttrProxy, MyDictClass, m
