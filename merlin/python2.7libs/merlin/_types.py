from array import array
import abc
import cython
import collections
import itertools
import weakref

@cython.locals(s=collections.Sequence, i=cython.int)
def _seq_get(s, i, *args):
    try:
        return s[i]
    except IndexError as e:
        if args:
            return args[0]
        else:
            raise e

class _VecBase(object):
    # __metaclass__ = abc.ABCMeta
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        for i, a in enumerate(self.__slots__[:-1]):
            setattr(self, a, kwargs.get(a, _seq_get(args, i, 0.0)))

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
        return max(0, len(self.__slots__) - 1)

    __delitem__ = None
    insert = None


class Vec2(_VecBase, collections.MutableSequence):
    """docstring for Vec2"""

    __slots__ = ('x', 'y', '__weakref__')

    cython.declare(x=cython.double, y=cython.double)
    def __init__(self, *args, **kwargs):
        super(Vec2, self).__init__(*args, **kwargs)

class Vec3(_VecBase, collections.MutableSequence):
    """docstring for Vec3"""

    __slots__ = ('x', 'y', 'z', '__weakref__')

    cython.declare(x=cython.double, y=cython.double, z=cython.double)
    def __init__(self, *args, **kwargs):
        super(Vec3, self).__init__(*args, **kwargs)

class Vec4(_VecBase, collections.MutableSequence):
    """docstring for Vec4"""

    __slots__ = ('x', 'y', 'z', 'w', '__weakref__')

    cython.declare(x=cython.double, y=cython.double, z=cython.double, w=cython.double)
    def __init__(self, *args, **kwargs):
        super(Vec4, self).__init__(*args, **kwargs)
        self.w = kwargs.get('w', _seq_get(args, 3, 1.0))

class ParmType(object):
    """Enum for Parameter types"""
    StringField = 0
    IntSlider = 1
    FloatSlider = 2
    Toggle = 3
    def __init__(self, arg):
        super(ParmType, self).__init__()
        self.arg = arg

class Parameter(object):
    """docstring for Parameter"""


    @abc.abstractmethod
    def eval(self):
        pass

    @abc.abstractproperty
    def node(self):
        pass

    def evalAsString(self):
        return str(self.eval())

    def evalAsInt(self):
        return int(self.eval())

    def evalAsFloat(self):
        return float(self.eval())

class ParmToggle(Parameter):
    """docstring for Toggle"""

    def __init__(self, node, default=False):
        super(Parameter, self).__init__()
        self.node = weakref.ref(node)
        self.value = self.default = bool(default)
        self.expression = None

    def eval(self):
        return bool(self.expression.eval()) if self.expression else bool(self.value)

class _InputMap(weakref.WeakValueDictionary):
    """docstring for _InputMap"""

    def __init__(self, max):
        super(_FixedLengthSeq, self).__init__()
        self.__max = max

    def __setitem__(self, i, v):
        if not isinstance(v, Node) or not isinstance(i, int):
            raise TypeError("key must be an integer and value must be a Node")
        elif i < 0 or i >= self.__max:
            raise ValueError("index value must be between 0 and %s" % self.__max)

        return super(_InputMap, self).__setitem__(i, v)

    def rotate(self):
        pass

class _TypedList(list):
    """docstring for _TypedList"""
    def __init__(self, type):
        super(_TypedList, self).__init__()
        self.__type = type

    def __setitem__(self, i, v):
        if not isinstance(v, self.type):
            raise ValueError()
        return super(_TypedList, self).__setitem__(i, v)

    def append(self, v):
        if not isinstance(v, self.type):
            raise ValueError()
        return super(_TypedList, self).append(v)

    def extend(self, iterable):
        tmp = list()
        for i, v in enumerate(iterable):
            if not isinstance(v, self.type):
                raise ValueError()
            tmp.append(v)
        return super(_TypedList, self).extend(tmp)

    def insert(self, i, v):
        if not isinstance(v, self.type):
            raise ValueError()
        return super(_TypedList, self).insert(i, v)

    @property
    def type(self):
        return self.__type        

class Node(object):
    __metaclass__ = abc.ABCMeta

    """docstring for Node"""
    def __init__(self):
        super(Node, self).__init__()
        self.__position = Vec2(x=0, y=0)
        self.__inputs = _InputMap(self.numInputs)
        self.__parameters = _TypedList(Parameter)
        self.__inputLabels = _TypedList(str)
        self.__inputLabels.extend(map("Input: {0}".format, range(self.numInputs)))
        # self.__name = type(self).__name__

    @abc.abstractmethod
    def cook(self, *args, **kwargs):
        """Method to call when a node instance is being cooked

        The value it returns is context specific. For instance, in a geometry context, a geometry object would be returned."""
        pass

    @abc.abstractproperty
    def path(self):
        """The full path to this node in the hierarchy."""
        pass

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractproperty
    def children(self):
        """A set of the Node's children.

        For nodes that cannot have children, this returns None."""
        return None

    @abc.abstractproperty
    def numInputs(self):
        return 1

    @property
    def position(self):
        return self.__position

    @property
    def inputs(self):
        """Return a mutable mapping object with input indices as the keys and Nodes as the values"""
        return self.__inputs

    @property
    def inputLabels(self):
        return self.__inputLabels

    @property
    def parameters(self):
        """Return a mutable sequence of all parameters.

        Parameters may be nested if they are of the correct type (e.g. Folder type)."""
        return self.__parameters