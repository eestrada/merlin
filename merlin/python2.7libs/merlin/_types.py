from array import array
import abc
import cython
import collections
import itertools

class _VecBase(object):
    __metaclass__ = abc.ABCMeta
    __slots__ = ()

    def __repr__(self):
        values = ', '.join(map(repr, self))
        return "{0.__class__.__name__}({1})".format(self, values)

    def __iadd__(self, other):
        assert len(self) == len(other)
        for i in range(len(self)):
            self[i] += other[i]
        return self

    def __add__(self, other):
        assert len(self) == len(other)
        rval = self.__class__(*self)
        for i in range(len(rval)):
            rval[i] += other[i]
        return rval

    def __imul__(self, other):
        assert len(self) == len(other)
        for i in range(len(self)):
            self[i] *= other[i]
        return self

    def __mul__(self, other):
        assert len(self) == len(other)
        rval = self.__class__(*self)
        for i in range(len(rval)):
            rval[i] *= other[i]
        return rval

    @cython.locals(i=cython.int)
    def __getitem__(self, i):
        return getattr(self, self.__slots__[:-1][i])

    @cython.locals(i=cython.int, v=cython.double)
    def __setitem__(self, i, v):
        return setattr(self, self.__slots__[:-1][i], v)

    def __len__(self):
        return len(self.__slots__) - 1

    def __delitem__(self, i):
        raise NotImplementedError("Cannot delete items on a {0.__class__.__name__}".format(self))

    def insert(self, i, v):
        raise NotImplementedError("Cannot insert items into a {0.__class__.__name__}".format(self))

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

    __slots__ = ('x', 'y', 'z', '__weakref__')

    cython.declare(x=cython.double, y=cython.double, z=cython.double)
    def __init__(self, *args, **kwargs):
        super(Vec, self).__init__()
        self.x = kwargs.get('x', _seq_get(args, 0, 0.0))
        self.y = kwargs.get('y', _seq_get(args, 1, 0.0))
        self.z = kwargs.get('z', _seq_get(args, 2, 0.0))

    def __len__(self):
        return 3


class Vec4(_VecBase, collections.MutableSequence):
    """docstring for Vec4"""

    __slots__ = ('x', 'y', 'z', 'w', '__weakref__')
    cython.declare(x=cython.double, y=cython.double, z=cython.double, w=cython.double)
    def __init__(self, *args, **kwargs):
        super(Vec4, self).__init__()
        self.x = kwargs.get('x', _seq_get(args, 0, 0.0))
        self.y = kwargs.get('y', _seq_get(args, 1, 0.0))
        self.z = kwargs.get('z', _seq_get(args, 2, 0.0))
        self.w = kwargs.get('w', _seq_get(args, 3, 1.0))

    @cython.locals(i=cython.int)
    def __getitem__(self, i):
        if i < 0 or i >= len(self): raise IndexError()
        return getattr(self, self.__slots__[i])

    @cython.locals(i=cython.int, v=cython.double)
    def __setitem__(self, i, v):
        if i < 0 or i >= len(self): raise IndexError()
        return setattr(self, self.__slots__[i], v)

    def __len__(self):
        return 4

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