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

class _TypedSet(set):
    """docstring for _TypedSet"""
    def __init__(self, type):
        super(_TypedSet, self).__init__()
        self.__type = type

    def __setitem__(self, i, v):
        if not isinstance(v, self.type):
            raise ValueError()
        return super(_TypedSet, self).__setitem__(i, v)

    def add(self, elem):
        if not isinstance(elem, self.type):
            raise TypeError()
        return super(_TypedSet, self).add(elem)

    def _update(self, func, *iterables):
        if len(iterables) < 1:
            raise RuntimeError('At least one iterable must be specified')
        def check_type(o):
            if not isinstance(o, self.type): raise TypeError()
            else: return o
        tmpset = set()
        for i in iterables:
            tmpset.update(map(check_type, i))
        return super(_TypedSet, self).update(tmpset)

    def update(self, *iterables):
        if len(iterables) < 1:
            raise RuntimeError('At least one iterable must be specified')
        def check_type(o):
            if not isinstance(o, self.type): raise TypeError()
            else: return o
        tmpset = set()
        for i in iterables:
            tmpset.update(map(check_type, i))
        return super(_TypedSet, self).update(tmpset)

    @property
    def type(self):
        return self.__type

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

class _Counter(object):
    """docstring for _Counter"""
    def __init__(self):
        super(_Counter, self).__init__()
        self.__count = 1

    def increment(self):
        retval = int(self)
        self.__count += 1
        return retval

    def __int__(self):
        return int(self.__count)

class Node(object):
    """docstring for Node"""
    # __metaclass__ = abc.ABCMeta
    __metaclass__ = _NodeClassBuilder

    def __new__(cls, parent, name=None):
        self = super(Node, cls).__new__(cls)

        if not (isinstance(parent, Node) or parent is None):
            raise TypeError()

        self.__parent = parent
        self.__position = Vec2(x=0, y=0)
        self.__inputs = _InputMap(self.numInputs)
        self.__parameters = _TypedList(Parameter)
        self.__inputLabels = _TypedList(str)
        self.__inputLabels.extend(map("Input: {0}".format, range(self.numInputs)))
        self.__destroyed = False

        if name is None:
            name = type(self).__name__
        self.name = name

        return self

    def __init__(self, *args, **kwrags): raise AttributeError("No constructor defined")

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
        self.__destroyed = True

    @property
    def destroyed(self):
        return self.__destroyed

    @abc.abstractmethod
    def cook(self, **kwargs):
        """Method to call when a node instance is being cooked

        The value(s) it receives is context specific. For instance, in a geometry context, a geometry object would be passed in."""
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
        return self.__name

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
        self.__name = n

    @property
    def parent(self):
        return self.__parent

    @abc.abstractproperty
    def children(self):
        """Returns a set-like object of the Node's children.

        For nodes that cannot have children, this returns None."""
        return None

    @abc.abstractmethod
    def createNode(self, type_name, node_name=None):
        """Create and return a node of the specified type"""
        pass

    def uniqueName(self, name):
        raise NotImplementedError()
        def split_suffix_nums(n):
            nc = n.rstrip('0123456789')
            nd = n[len(nc):]
            return (nc, nd) if nc and nd else None

        childset = set(map(lambda o: o.name, self.children))

        if name in childset:
            pass

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
