
import weakref

class Vertex(object):
    """A Vertex is associated with only one point and one primitive."""
    def __init__(self, point, primitive):
        super(Vertex, self).__init__()
        self.point = point
        # self.primitive should be made a weak reference since
        # primitives also reference their vertices   
        self.primitive = primitive