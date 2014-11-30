from __future__ import division, absolute_import, print_function, unicode_literals

from array import array
import re
import abc
import cython
import collections
import itertools
import weakref

try:
    import builtins
except ImportError as e:
    import __builtin__ as builtins

@cython.locals(s=collections.Sequence, i=cython.int)
def _seq_get(s, i, *args):
    try:
        return s[i]
    except IndexError as e:
        if args:
            return args[0]
        else:
            raise e

def type_compatible(a, b):
    return isinstance(a, b.__class__) or isinstance(b, a.__class__)

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
        if len(self) != len(other): raise ValueError()
        assert type_compatible(self, other)
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

# TODO: swap out _InputMap with an _InputSequence
class InputSequence(collections.Sequence):
    """docstring for InputSequence"""
    pairtuple = collections.namedtuple('NodeInput', ['label', 'value'])

    def __init__(self, owner, max=1):
        super(InputSequence, self).__init__()
        self._max = int(max)
        self._owner = owner
        self._indexmap = dict()
        self._namemap = dict()

    def __getitem__(self, index):
        if index < 0 or index >= self._max:
            raise IndexError('InputSequence index out of range')
        return self._indexmap.get(index, None)

    def __setitem__(self, index, value):
        if index < 0 or index >= self._max:
            raise IndexError('InputSequence index out of range')
        elif value.parent != self._owner.parent:
            raise RuntimeError('Cannot add as an input a Node with a different parent.')
        self._indexmap[index] = value

    def __len__(self):
        return self._max

    def getLabel(self, index):
        if index < 0 or index >= self._max:
            raise IndexError('InputSequence index out of range')
        return self._namemap.get(index, 'Input %d' % index)

    def setLabel(self, index, label):
        if index < 0 or index >= self._max:
            raise IndexError('InputSequence index out of range')
        self._namemap[index] = str(label)

    def getPair(self, index):
        label = self.getLabel(index)
        value = self[index]
        return self.pairtuple(label, value)

    def iterLabels(self):
        for i in range(len(self)):
            yield self.getLabel(i)

    def iterPairs(self):
        for i in range(len(self)):
            yield self.getPair(i)

class _InputMap(weakref.WeakValueDictionary, object):
    """docstring for _InputMap"""

    def __init__(self, max):
        super(_InputMap, self).__init__()
        self.__max = int(max)

    def __setitem__(self, i, v):
        if not isinstance(v, Node) or not isinstance(i, int):
            raise TypeError("key must be an integer and value must be a Node")
        elif i < 0 or i >= self.max:
            raise ValueError("index value must be between 0 and %s" % self.max)

        return super(_InputMap, self).__setitem__(i, v)

    @property
    def max(self):
        return self.__max

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
        def check_type(o):
            if not isinstance(o, self.type): raise ValueError()
            else: return o
        return super(_TypedList, self).extend(map(check_type, iterable))

    def insert(self, i, v):
        if not isinstance(v, self.type):
            raise ValueError()
        return super(_TypedList, self).insert(i, v)

    @property
    def type(self):
        return self.__type

class TypedSet(collections.MutableSet):
    """docstring for TypedSet"""
    def __init__(self, iterable=[], *types):
        if not types:
            types = (object,) # This should accept instances of all new style classes
        else:
            types = tuple(types)

        for t in types:
            if not issubclass(t, object):
                raise TypeError('Class {c} is not a new style class.'.format(c=t))

        super(TypedSet, self).__init__()

        self._types = types
        self._set = set()

        self |= iterable

    def _from_iterable(self, it):
        return self.__class__(it, *self._types)

    def __repr__(self):
        types = map(lambda t: t.__name__, self._types)
        types = ', '.join(types)
        types = ''.join(['(', types, ')'])
        return '{cls}({it}, *{types})'.format(cls=self.__class__.__name__,
                                          types=types,
                                          it=list(self))

    def __contains__(self, value):
        return value in self._set

    def __iter__(self):
        return iter(self._set)

    def __len__(self):
        return len(self._set)

    def add(self, value):
        if not isinstance(value, self._types):
            raise TypeError('Value "{0!r}" was not of the right type.'.format(value))
        self._set.add(value)

    def discard(self, value):
        self._set.discard(value)

    def pop(self):
        return self._set.pop()

    def clear(self):
        self._set.clear()

class NodeSet(TypedSet):
    """docstring for NodeSet"""
    def __init__(self, iterable, parent, *types):
        if not types:
            types = (Node,)
        else:
            types = set(types) | set([Node])
        super(NodeSet, self).__init__(iterable, *types)
        self._parent = parent

    def _from_iterable(self, it):
        return self.__class__(it, self._parent, *self._types)

    def add(self, value):
        if not isinstance(value, self._types):
            raise TypeError('Value "{0!r}" was not of the right type.'.format(value))
        value._parent = self._parent
        value.name = value.name # this will rename "value" to have a unique name within its new parent
        self._set.add(value)

    def destroyall(self):
        '''Run destroy on all contained nodes, then clear self

        This is mainly useful for merlin Node types that need to destroy
        their children.'''
        for elem in self:
            elem.destroy()
        self.clear()

def _destroyer(obj):
    if isinstance(obj, collections.Callable):
        def wrapper(self, *args, **kwargs):
            if self.destroyed:
                raise RuntimeError('Cannot use attributes of a destroyed node.')
            return obj(self, *args, **kwargs)
        wrapper.__name__ = obj.__name__
        wrapper.__doc__ = obj.__doc__
        wrapper._destruction_ready = True
    elif isinstance(obj, property):
        def wrapper(self, *args, **kwargs):
            if self.destroyed:
                raise RuntimeError('Cannot use attributes of a destroyed node.')
            return obj
        wrapper = property()
        getter = _destroyer(obj.getter)
        setter = _destroyer(obj.setter)
        deleter = _destroyer(obj.deleter)
        wrapper.__doc__ = property(getter, setter, deleter, obj.__doc__)
        wrapper._destruction_ready = True
    else:
        wrapper = obj
        pass
    return wrapper

class _NodeClassBuilder(abc.ABCMeta, type):
    """docstring for _NodeClassBuilder"""

    def __new__(mcls, name, bases, attrs):
        print(type(attrs))
        for name in attrs:
            if name not in set(['destroy', 'destroyed', '_Node__destroyed', '__metaclass__']) or not (name.startswith('__') and name.endswith('__')):
                attrs[name] = _destroyer(attrs[name])
                print(repr(name))
                print(repr(attrs[name]))
        cls = super(_NodeClassBuilder, mcls).__new__(mcls, name, bases, attrs)
        return cls

class _NodeClassBuilder(abc.ABCMeta, type):
    """docstring for _NodeClassBuilder"""

    node_types = dict()
    def __new__(mcls, name, bases, attrs):
        cls = super(_NodeClassBuilder, mcls).__new__(mcls, name, bases, attrs)
        if name in mcls.node_types:
            RuntimeError('Node class "{0!r}" is being redefined. This is not allowed.'.format(name))
        else:
            mcls.node_types[name] = cls
        return cls

_name_splitter = re.compile(r'(?P<name>[a-zA-Z]+)(?P<num>[0-9]+)?')

class Node(object):
    """docstring for Node"""
    # __metaclass__ = abc.ABCMeta
    __metaclass__ = _NodeClassBuilder

    child_types = (Node)

    def __new__(cls, parent, name=None):
        self = super(Node, cls).__new__(cls)

        if not isinstance(parent, (Node, type(None))):
            raise TypeError()

        self._parent = parent
        self._children = NodeSet([], self, cls.child_types)
        self._position = Vec2(x=0, y=0)
        self._inputs = InputSequence(self, self.numInputs)
        self._parameters = _TypedList(Parameter)
        self._destroyed = False

        if cls == Node:
            self._name = '/'
        else:
            if name is None:
                name = type(self).__name__ + str(1)
            self.name = name

        return self

    def __init__(self, *args, **kwrags): raise AttributeError("No public constructor defined")

    def __cmp_key(self):
        return (self.__class__, self.path, id(self))

    def __hash__(self):
        return hash(self.__cmp_key())

    def __eq__(self, other):
        sck = self.__cmp_key()
        ock = other.__cmp_key()
        if sck == sck:
            return True
        elif sck[1]==ock[1] and (sck[0]!=ock[0] or sck[2]!=ock[2]):
            # Catch identical nodes being created that are not the same python object
            raise RuntimeError('Nodes have same path but are not the same Python object!')
        else:
            return False

    def destroy(self):
        self._destroyed = True

    @property
    def destroyed(self):
        return self._destroyed

    def cook(self, **kwargs):
        """Method to call when a node instance is being cooked

        The value(s) it receives is context specific. For instance, in a
        geometry context, a geometry object would be passed in. The object
        must be mutated to have any effect.

        If an node requires data from its inputs, it must request that they also cook."""
        pass

    @property
    def path(self):
        """The full path to this node in the hierarchy."""
        return self._get_path()

    def _get_path(self, l=[]):
        l.append(self.name)
        if self.parent is None:
            l.reverse()
            return os.path.join(os.path.sep, *l)
        else:
            return self.parent._get_path(l)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        if not isinstance(n, str):
            if isinstance(n, bytes):
                n = str(n, encoding='utf8')
            else:
                raise TypeError()
        # TODO (eestrada): sanitize input
        if self.parent is not None:
            n = self.parent.uniqueName(n)
        self._name = n

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        """Returns a set-like object of the Node's children.

        For nodes that cannot have children, this should return None."""
        return self._children

    def createNode(self, type_name, node_name=None):
        """Create a node of the specified type as a child node and return it"""
        cls = self.__metaclass__.node_types[type_name]
        if not issubclass(cls, self.__class__.child_types):
            raise RuntimeError('Cannot create a node of this type as a child node.')

        child = cls.__new__(cls, self, node_name)
        self.children.add(child)
        return child

    def uniqueName(self, name):
        cs = set(map(lambda n: n.name, self.children))
        if name not in cs:
            return name

        raise NotImplementedError()
        def split_suffix_nums(n):
            nc = n.rstrip('0123456789')
            nd = n[len(nc):]
            return (nc, nd) if nc and nd else None

        childset = set(map(lambda o: o.name, self.children))

        if name in childset:
            pass

    @property
    def numInputs(self):
        return 0

    @property
    def position(self):
        return self._position

    @property
    def inputs(self):
        """Return a sequence of input values

        Empty inputs indices will simply return None."""
        return self._inputs

    @property
    def parameters(self):
        """Return a mutable sequence of all parameters.

        Parameters may be nested if they are of the correct type (e.g. Folder type)."""
        return self._parameters

class _RootNode(Node):
    """docstring for _RootNode"""
    def __new__(cls):
        self = super(_RootNode, cls).__new__(cls, None, '/')
        return self

    @property
    def numInputs(self):
        return 0

    def cook(self, **kwargs):
        """Do nothing, since we are root"""
        pass

    @property
    def children(self):
        pass

    @property
    def name(self):
        return super(_RootNode, self).name

    @name.setter
    def name(self, v):
        raise RuntimeError('Root node cannot be renamed.')

class _Scene(object):
    """docstring for _Scene"""
    def __init__(self, fpath=None):
        super(_Scene, self).__init__()
        self.fpath = fpath

        if self.fpath:
            self.loadScene()
        else:
            self.initEmpty()

    def loadScene(self):
        if not self.fpath:
            raise ValueError('fpath must be initialized to a value.')
        from . import spellscript
        spellscript.loadScene(self.fpath, self)

    def initEmpty(self):
        self.root = _RootNode(self)
