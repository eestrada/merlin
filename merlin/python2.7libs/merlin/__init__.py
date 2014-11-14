from __future__ import division, absolute_import, print_function, unicode_literals

import sys
import os

def main(argv=sys.argv):
    print("we are running merlin main. Huzzah!")
    load_scene('')
    sys.exit()

def load_scene(path):
    """merlin scene files are simply a series of python statements

    We create a restricted environment, execute the python statements and
    return the scene object that is generated. If no scene object is built, then
    a keyerror is thrown."""
    print(type(__builtins__))
    bi = __builtins__
    if not isinstance(bi, dict):
        bi = vars(bi)
    bi = bi.copy()

    namespace = dict(__builtins__=bi)

    # for m in ['merlin', 'merlin.scene']:
        # exec('import %s' % m, namespace)

    bi.pop('__import__')
    bi.pop('execfile')
    bi.pop('file')
    bi.pop('open')
    bi.pop('exit')
    bi.pop('quit')

    # print(namespace)
    # namespace['merlin'] = merlin

    # execfile(path, namespace)

    # return namespace['scene']
