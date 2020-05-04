.. :doctest:

>>> import re

Let's exercise our URL extraction regex.

>>> from Globals import URL_RE

But first, a simple helper function:

>>> regex = re.compile( URL_RE )
>>> def extract_re( text ):
...   m = regex.search( text )
...   return m.group( 0 ) if m is not None else ""

And the data for our test:

>>> test_parameters = (
...   "noise noise http://github.com/",
...   "noise noise http://github.com",
...   "noise noise http://github.com/test.html",
...   "noise noise http://github.com/test/",
...   "noise noise xhttp://github.com/",
...   "noise noise https://github.com/",
...   "noise noise www.github.com",
...   "noise noise xwww.github.com",
...   "noise noise http://github.com:8080/",
...   "noise noise http://github.com.",
...   "noise noise http://github.com?",
...   "noise noise http://github.com!",
...   "noise noise (http://github.com)",
...   "noise noise http://github.com/xxx?xxx=xxx&yyy=yyy#zzz",
...   "noise noise 192.168.0.1",
...   "noise noise 192.168.0.1/test.html",
... )

>>> for input in test_parameters:
...   print( ( '"%s"' % input ) + " -> " + ( extract_re( input ) or "ø" ) )
"noise noise http://github.com/" -> http://github.com/
"noise noise http://github.com" -> http://github.com
"noise noise http://github.com/test.html" -> http://github.com/test.html
"noise noise http://github.com/test/" -> http://github.com/test/
"noise noise xhttp://github.com/" -> ø
"noise noise https://github.com/" -> https://github.com/
"noise noise www.github.com" -> www.github.com
"noise noise xwww.github.com" -> ø
"noise noise http://github.com:8080/" -> http://github.com:8080/
"noise noise http://github.com." -> http://github.com
"noise noise http://github.com?" -> http://github.com
"noise noise http://github.com!" -> http://github.com
"noise noise (http://github.com)" -> http://github.com
"noise noise http://github.com/xxx?xxx=xxx&yyy=yyy#zzz" -> http://github.com/xxx?xxx=xxx&yyy=yyy#zzz
"noise noise 192.168.0.1" -> 192.168.0.1
"noise noise 192.168.0.1/test.html" -> 192.168.0.1/test.html
