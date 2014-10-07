#! /usr/bin/env python
from __future__ import unicode_literals, print_function, absolute_import, division

import os
import sys
import unittest
import doctest
import argparse
import collections

def parse_args(args=sys.argv):
    parser = argparse.ArgumentParser(description='Run tests for %(prog)s framework')
    parser.add_argument('-l', '--level', action='count', default=0, help='Decide '
                        'what level of tests to run. Supplying this multiple '
                        'times will increase the level accordingly. Defaults '
                        'to 0, the lowest (and fastest) level.')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbose output. '
                        'Supplying this multiple times will increase verbosity. '
                        'This is usually unnecesary; the test suite will print '
                        'information when a test fails, which is usually '
                        'all we care about.')

    return parser.parse_args(args[1:])

def main(args=sys.argv):
    if isinstance(args, collections.Mapping):
        kwds = args
    elif isinstance(args, collections.Sequence):
        pargs = parse_args(args)
        kwds = vars(pargs).copy()
    else:
        raise ValueError('"args" argument to main must be mapping or sequence')

    abspath = os.path.abspath(__file__)
    dirname = os.path.dirname(abspath)

    suite = unittest.defaultTestLoader.discover(dirname)

    unittest.TextTestRunner(verbosity=kwds['verbose']).run(suite)

if __name__ == "__main__":
    retval = main(sys.argv)
    sys.exit(retval)
