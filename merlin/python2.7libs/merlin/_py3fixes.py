from __future__ import unicode_literals, print_function, absolute_import, division

__all__ = ('ascii', 'filter', 'hex', 'map', 'oct', 'zip',
           'bytes', 'str', 'unicode', 'basestring', 'range', 'xrange',
           'int', 'long')

import sys

if sys.version_info[0] < 3:
    from future_builtins import ascii, filter, hex, map, oct, zip
    bytes = str
    str = unicode
    unicode = unicode
    basestring = basestring
    range = xrange
    xrange = xrange
    int = int
    long = long
else:
    from builtins import ascii, filter, hex, map, oct, zip
    bytes = bytes
    str = str
    unicode = str
    basestring = (str, bytes)
    range = range
    xrange = range
    int = int
    long = int
