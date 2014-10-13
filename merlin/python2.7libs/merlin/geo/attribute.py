
from array import array
import cython
import collections
import itertools

class Attribute(collections.Sequence):
    """docstring for Attribute"""
    def __new__(cls, *args, **kwargs):
        self = super(Attribute, cls).__new__(cls)
        return self

class Integer(array, Attribute):
    """docstring for Integer"""
    def __new__(cls, values=None, length=None):
        if values:
            self = super(Integer, cls).__new__(cls, 'l', values)
        elif length:
            r = itertools.repeat(int(), length)
            self = super(Integer, cls).__new__(cls, 'l', r)
        else:
            self = super(Integer, cls).__new__(cls, 'l')
        return self

class Float(Attribute):
    """docstring for Float"""
    def __init__(self, f):
        super(Float, self).__init__()
        self.arg = arg

class Vec(list, Attribute):
    """docstring for Vec"""
    def __init__(self, x, y, z):
        super(Vec, self).__init__()
        self.arg = arg

class Vec4(Attribute):
    """docstring for Vec4"""
    def __init__(self, x, y, z, w):
        super(Vec4, self).__init__()
        self.arg = arg

class String(object):
    """docstring for String"""
    def __init__(self, arg):
        super(String, self).__init__()
        self.arg = arg

class Mat3(object):
    """docstring for Mat3"""
    cython.declare(v=cython.double[9])
    def __init__(self, arg):
        super(Mat3, self).__init__()
        self.arg = arg

class Mat4(object):
    """docstring for Mat4"""
    cython.declare(v=cython.double[16])
    def __init__(self, arg):
        super(Mat4, self).__init__()
        self.arg = arg
        