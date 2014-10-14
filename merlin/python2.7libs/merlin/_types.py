from array import array
import cython
import collections
import itertools

class _VecBase(object):

    def __iadd__(self, other):
        for i in range(len(self)):
            self[i] += other[i]
        return self

    def __add__(self, other):
        rval = self.__class__(*self)
        for i in range(len(rval)):
            rval[i] += other[i]
        return rval

@cython.locals(s=collections.Sequence, i=cython.int)
def _seq_get(s, i, *args):
    try:
        return s[i]
    except IndexError as e:
        if args:
            return args[0]
        else:
            raise e

class Vec(_VecBase, collections.MutableSequence):
    """docstring for Vec"""

    __slots__ = ('x', 'y', 'z')

    cython.declare(x=cython.double, y=cython.double, z=cython.double)
    def __init__(self, *args, **kwargs):
        super(Vec, self).__init__()
        self.x = kwargs.get('x', _seq_get(args, 0, 0.0))
        self.y = kwargs.get('y', _seq_get(args, 1, 0.0))
        self.z = kwargs.get('z', _seq_get(args, 2, 0.0))

    @cython.locals(i=cython.int)
    def __getitem__(self, i):
        if i == 0: return self.x
        elif i == 1: return self.y
        elif i == 2: return self.z
        else: raise IndexError()

    @cython.locals(i=cython.int, v=cython.double)
    def __setitem__(self, i, v):
        if i == 0: self.x = v
        elif i == 1: self.y = v
        elif i == 2: self.z = v
        else: raise IndexError()

    def __len__(self):
        return 3

    def __delitem__(self, i):
        raise NotImplementedError("Cannot delete items on a Vector")

    def insert(self, i, v):
        raise NotImplementedError("Cannot insert items into a Vector")

class Vec4(_VecBase, collections.MutableSequence):
    """docstring for Vec4"""

    __slots__ = ('x', 'y', 'z', 'w')
    cython.declare(x=cython.double, y=cython.double, z=cython.double, w=cython.double)
    def __init__(self, x, y, z, w):
        super(Vec4, self).__init__()
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    @cython.locals(i=cython.int)
    def __getitem__(self, i):
        if i == 0: return self.x
        elif i == 1: return self.y
        elif i == 2: return self.z
        elif i == 3: return self.w
        else: raise IndexError()

    @cython.locals(i=cython.int, v=cython.double)
    def __setitem__(self, i, v):
        if i == 0: self.x = v
        elif i == 1: self.y = v
        elif i == 2: self.z = v
        elif i == 3: self.w = v
        else: raise IndexError()

    def __delitem__(self, i):
        raise NotImplementedError("Cannot delete items on a Vector")

    def __len__(self):
        return 4

    def insert(self, i, v):
        raise NotImplementedError("Cannot insert items into a Vector")

class String(object):
    """docstring for String"""
    def __init__(self, arg):
        super(String, self).__init__()
        self.arg = arg

class Mat3(object):
    """docstring for Mat3"""
    # cython.declare(v=cython.double[9])
    def __init__(self, arg):
        super(Mat3, self).__init__()
        self.arg = arg

class Mat4(object):
    """docstring for Mat4"""
    # cython.declare(v=cython.double[16])
    def __init__(self, arg):
        super(Mat4, self).__init__()
        self.arg = arg