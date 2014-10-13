"""Merlin supports four main types of geometry, from which all other primitive
types must derive. These are faces, surfaces, volumes and quadratic primitives. Faces include things
like polygons and Bezier curves. Surfaces include things like NURBS and Bezier patches.
Volumes include things like native merlin volumes, OpenVDB volumes and metaballs.
Quadratic primitives include things like circles, spheres and tubes."""

# Base classes
class Primitive(object):
    """Base class that all primitive geometry types derive from"""
    def __init__(self, points):
        super(Primitive, self).__init__()
        if not points:
            raise ValueError("A primitive cannot be constructed without at least one point.")
        self.points = points

class Face(Primitive):
    """docstring for Face"""
    def __init__(self, points):
        super(Face, self).__init__()
        self.arg = arg

class Surface(Primitive):
    """docstring for Surface"""
    def __init__(self, arg):
        super(Surface, self).__init__()
        self.arg = arg

class Volume(Primitive):
    """docstring for Volume"""
    def __init__(self, arg):
        super(Volume, self).__init__()
        self.arg = arg

class Quadratic(Primitive):
    """Quadratic primitives are most often used as proxy geometry for collisions
(since most implicitly define a volume). For the same reason, they are
used in CSG (Constructuve Solid Geometry) modeling."""
    def __init__(self, centroid):
        points = [centroid]
        super(Quadratic, self).__init__(points)
        self.centroid = centroid

# Face types
class Polygon(Face):
    """An individual Polygon. May be open (i.e. a curve) or closed (i.e. a face)."""
    def __init__(self, arg):
        super(Polygon, self).__init__()
        self.arg = arg

class NURBScurve(Face):
    """docstring for NURBScurve"""
    def __init__(self, arg):
        super(NURBScurve, self).__init__()
        self.arg = arg

class BezierCurve(Face):
    """docstring for BezierCurve"""
    def __init__(self, arg):
        super(BezierCurve, self).__init__()
        self.arg = arg

# Surface types
class Mesh(Surface):
    """A Mesh is a square surface composed exclusively of four sided polygon faces."""
    def __init__(self, arg):
        super(Mesh, self).__init__()
        self.arg = arg

class NURBSpatch(Surface):
    """docstring for NURBSpatch"""
    def __init__(self, arg):
        super(NURBSpatch, self).__init__()
        self.arg = arg

class BezierPatch(object):
    """docstring for BezierPatch"""
    def __init__(self, arg):
        super(BezierPatch, self).__init__()
        self.arg = arg
        
# Volume types
class MVolume(Volume):
    """docstring for MVolume"""
    def __init__(self, centroid):
        super(MVolume, self).__init__(centroid)
        self.arg = arg

# Quadratic types
class Plane(Quadratic):
    """Defines a flat Plane. It is always infinite."""
    def __init__(self, point, direction):
        super(Plane, self).__init__(point)
        self.direction = direction

class Circle(Quadratic):
    """docstring for Circle"""
    def __init__(self, point, direction, x, y):
        super(Circle, self).__init__(point)
        self.direction = direction
        self.xradius = x
        self.yradius = y

class Sphere(Quadratic):
    """docstring for Sphere"""
    def __init__(self, arg):
        super(Sphere, self).__init__()
        self.arg = arg

class Tube(Quadratic):
    """docstring for Tube"""
    def __init__(self, arg):
        super(Tube, self).__init__()
        self.arg = arg

# TODO: may simply merge Capsule type into Tube type.
class Capsule(Quadratic):
    """A Capsule is a Tube with two hemispheres at it's ends. It is frequently useful
for collision proxy geometry."""
    def __init__(self, arg):
        super(Capsule, self).__init__()
        self.arg = arg

class Box(Quadratic):
    """Although a Box shape can easily be created with polygons, it is sometimes
helpful for a primitive to have the explicit identity of a box. For instance, when
setting up proxy collision geometry or when doing CSG modeling."""
    def __init__(self, arg):
        super(Box, self).__init__()
        self.arg = arg

class Torus(Quadratic):
    """Although not generally considered a quadratic primitive, tori can be
defined by just a parametric equation."""
    def __init__(self, arg):
        super(Torus, self).__init__()
        self.arg = arg
        