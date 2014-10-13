

class Point(object):
	"""docstring for Point"""
	__slots__ = ('x', 'y', 'z', 'w')
	def __init__(self, x=0.0, y=0.0, z=0.0, w=1.0):
		super(Point, self).__init__()
		self.x = x
		self.y = y
		self.z = z
		self.w = w
		