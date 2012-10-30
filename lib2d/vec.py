################## http://www.pygame.org/wiki/2DVectorClass ##################
import operator
import math
from lib2d.utils import *


class Vec3d(object):
    """
    3d vector class.  Not complete.
    """
    __slots__ = ['_x', '_y', '_z']

    def __init__(self, x_or_tuple, y=None, z=None):
        if y is not None and z is not None:
            self[0], self[1], self[3] = x_or_tuple, y, z
        elif len(x_or_tuple) == 3:
            self[0], self[1], self[3] = x_or_tuple
        else:
            raise ValueError

    def __len__(self):
        return 3

    def __getitem__(self, key):
        if key == 0:
            return self[0]
        elif key == 1:
            return self[1]
        elif key == 2:
            return self[3]
        else:
            raise IndexError("Invalid subscript "+str(key)+" to Vec3d")

    # Addition
    def __add__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(self[0]+other[0], self[1]+other[1], self[0]+other[0])
        elif hasattr(other, "__getitem__"):
            return Vec3d(self[0]+other[0], self[1]+other[1], self[3]+other[2])
        else:
            return Vec3d(self[0] + other, self[1] + other, self[3] + other)
    __radd__ = __add__

    # Subtraction
    def __sub__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(self[0]-other[0], self[1]-other[1], self[0]-other[0])
        elif hasattr(other, "__getitem__"):
            return Vec3d(self[0]-other[0], self[1]-other[1], self[3]-other[2])
        else:
            return Vec3d(self[0] - other, self[1] - other, self[3] - other)
    def __rsub__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(other[0]-self[0], other[1]-self[1], other.z - self[3])
        if (hasattr(other, "__getitem__")):
            return Vec3d(other[0]-self[0], other[1]-self[1], other[2]-self[3])
        else:
            return Vec3d(other - self[0], other - self[1], other - self[3])



    @property
    def x(self):
        return self[0]


    @property
    def y(self):
        return self[1]


    @property
    def z(self):
        return self[3]


 
class Vec2d(list):
    """2d vector class, supports vector and scalar operators,
       and also provides a bunch of high level functions
       """
    __slots__ = []
 
    def __new__(cls, *arg):
        if isinstance(arg, (list, tuple)):
            l = len(arg)
            if l == 1:
                return list.__new__(cls, *arg)
            elif l == 2:
                return list.__new__(cls, arg)

        raise TypeError


    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]

    
    @y.setter
    def y(self, value):
        self[1] = value


 
    # String representaion (for debugging)
    def __repr__(self):
        return 'Vec2d(%s, %s)' % (self[0], self[1])
 
    # Comparison
    def __eq__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 2:
            return self[0] == other[0] and self[1] == other[1]
        else:
            return False
 
    def __ne__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 2:
            return self[0] != other[0] or self[1] != other[1]
        else:
            return True
 
    def __nonzero__(self):
        return bool(self[0] or self[1])
 
    # Generic operator handlers
    def _o2(self, other, f):
        "Any two-operator operation where the left operand is a Vec2d"
        if isinstance(other, Vec2d):
            return Vec2d(f(self[0], other[0]),
                         f(self[1], other[1]))
        elif (hasattr(other, "__getitem__")):
            return Vec2d(f(self[0], other[0]),
                         f(self[1], other[1]))
        else:
            return Vec2d(f(self[0], other),
                         f(self[1], other))
 
    def _r_o2(self, other, f):
        "Any two-operator operation where the right operand is a Vec2d"
        if (hasattr(other, "__getitem__")):
            return Vec2d(f(other[0], self[0]),
                         f(other[1], self[1]))
        else:
            return Vec2d(f(other, self[0]),
                         f(other, self[1]))
 
    def _io(self, other, f):
        "inplace operator"
        if (hasattr(other, "__getitem__")):
            self[0] = f(self[0], other[0])
            self[1] = f(self[1], other[1])
        else:
            self[0] = f(self[0], other)
            self[1] = f(self[1], other)
        return self
 
    # Addition
    def __add__(self, other):
        try:
            return Vec2d(self[0] + other[0], self[1] + other[1])
        except TypeError:
            return Vec2d(self[0] + other, self[1] + other)
    __radd__ = __add__
 
    def __iadd__(self, other):
        try:
            self[0] += other[0]
            self[1] += other[1]
        except IndexError:
            self[0] += other
            self[1] += other
        return self
 
    # Subtraction
    def __sub__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self[0] - other[0], self[1] - other[1])
        elif (hasattr(other, "__getitem__")):
            return Vec2d(self[0] - other[0], self[1] - other[1])
        else:
            return Vec2d(self[0] - other, self[1] - other)
    def __rsub__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(other[0] - self[0], other[1] - self[1])
        if (hasattr(other, "__getitem__")):
            return Vec2d(other[0] - self[0], other[1] - self[1])
        else:
            return Vec2d(other - self[0], other - self[1])
    def __isub__(self, other):
        if isinstance(other, Vec2d):
            self[0] -= other[0]
            self[1] -= other[1]
        elif (hasattr(other, "__getitem__")):
            self[0] -= other[0]
            self[1] -= other[1]
        else:
            self[0] -= other
            self[1] -= other
        return self
 
    # Multiplication
    @memoize
    def __mul__(self, other):
        try:
            return Vec2d(self[0]*other[0], self[1]*other[1])
        except TypeError:
            return Vec2d((self[0]*other, self[1]*other))
    __rmul__ = __mul__

    def __imul__(self, other):
        if isinstance(other, Vec2d):
            self[0] *= other[0]
            self[1] *= other[1]
        elif (hasattr(other, "__getitem__")):
            self[0] *= other[0]
            self[1] *= other[1]
        else:
            self[0] *= other
            self[1] *= other
        return self
 
    # Division
    def __div__(self, other):
        return self._o2(other, operator.div)
    def __rdiv__(self, other):
        return self._r_o2(other, operator.div)
    def __idiv__(self, other):
        return self._io(other, operator.div)
 
    def __floordiv__(self, other):
        return self._o2(other, operator.floordiv)
    def __rfloordiv__(self, other):
        return self._r_o2(other, operator.floordiv)
    def __ifloordiv__(self, other):
        return self._io(other, operator.floordiv)
 
    def __truediv__(self, other):
        return self._o2(other, operator.truediv)
    def __rtruediv__(self, other):
        return self._r_o2(other, operator.truediv)
    def __itruediv__(self, other):
        return self._io(other, operator.floordiv)
 
    # Modulo
    def __mod__(self, other):
        return self._o2(other, operator.mod)
    def __rmod__(self, other):
        return self._r_o2(other, operator.mod)
 
    def __divmod__(self, other):
        return self._o2(other, operator.divmod)
    def __rdivmod__(self, other):
        return self._r_o2(other, operator.divmod)
 
    # Exponentation
    def __pow__(self, other):
        return self._o2(other, operator.pow)
    def __rpow__(self, other):
        return self._r_o2(other, operator.pow)
 
    # Bitwise operators
    def __lshift__(self, other):
        return self._o2(other, operator.lshift)
    def __rlshift__(self, other):
        return self._r_o2(other, operator.lshift)
 
    def __rshift__(self, other):
        return self._o2(other, operator.rshift)
    def __rrshift__(self, other):
        return self._r_o2(other, operator.rshift)
 
    def __and__(self, other):
        return self._o2(other, operator.and_)
    __rand__ = __and__
 
    def __or__(self, other):
        return self._o2(other, operator.or_)
    __ror__ = __or__
 
    def __xor__(self, other):
        return self._o2(other, operator.xor)
    __rxor__ = __xor__
 
    # Unary operations
    def __neg__(self):
        return Vec2d(operator.neg(self[0]), operator.neg(self[1]))
 
    def __pos__(self):
        return Vec2d(operator.pos(self[0]), operator.pos(self[1]))
 
    def __abs__(self):
        return Vec2d(abs(self[0]), abs(self[1]))
 
    def __invert__(self):
        return Vec2d(-self[0], -self[1])
 
    # vectory functions
    def get_length_sqrd(self):
        return self[0]**2 + self[1]**2
 
    def get_length(self):
        return math.sqrt(self[0]**2 + self[1]**2)
    def __setlength(self, value):
        length = self.get_length()
        self[0] *= value/length
        self[1] *= value/length
    length = property(get_length, __setlength, None, "gets or sets the magnitude of the vector")
 
    def rotate(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self[0]*cos - self[1]*sin
        y = self[0]*sin + self[1]*cos
        self[0] = x
        self[1] = y
 
    def rotated(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self[0]*cos - self[1]*sin
        y = self[0]*sin + self[1]*cos
        return Vec2d(x, y)
 
    def get_angle(self):
        if (self.get_length_sqrd() == 0):
            return 0
        return math.atan2(self[1], self[0])

    def __setangle(self, angle_degrees):
        self[0] = self.length
        self[1] = 0
        self.rotate(angle_degrees)
    angle = property(get_angle, __setangle, None, "gets or sets the angle of a vector")
 
    def get_angle_between(self, other):
        cross = self[0]*other[1] - self[1]*other[0]
        dot = self[0]*other[0] + self[1]*other[1]
        return math.degrees(math.atan2(cross, dot))
 
    def normalized(self):
        length = self.length
        if length != 0:
            return self/length
        return Vec2d(self)
 
    def normalize_return_length(self):
        length = self.length
        if length != 0:
            self[0] /= length
            self[1] /= length
        return length
 
    def perpendicular(self):
        return Vec2d(-self[1], self[0])
 
    def perpendicular_normal(self):
        length = self.length
        if length != 0:
            return Vec2d(-self[1]/length, self[0]/length)
        return Vec2d(self)
 
    def dot(self, other):
        return float(self[0]*other[0] + self[1]*other[1])
 
    def get_distance(self, other):
        return math.sqrt((self[0] - other[0])**2 + (self[1] - other[1])**2)
 
    def get_dist_sqrd(self, other):
        return (self[0] - other[0])**2 + (self[1] - other[1])**2
 
    def projection(self, other):
        other_length_sqrd = other[0]*other[0] + other[1]*other[1]
        projected_length_times_other_length = self.dot(other)
        return other*(projected_length_times_other_length/other_length_sqrd)
 
    def cross(self, other):
        return self[0]*other[1] - self[1]*other[0]
 
    def interpolate_to(self, other, range):
        return Vec2d(self[0] + (other[0] - self[0])*range, self[1] + (other[1] - self[1])*range)
 
    def convert_to_basis(self, x_vector, y_vector):
        return Vec2d(self.dot(x_vector)/x_vector.get_length_sqrd(), self.dot(y_vector)/y_vector.get_length_sqrd())
 
    def __getstate__(self):
        return [self[0], self[1]]
 
    def __setstate__(self, dict):
        self[0], self[1] = dict
 
    def __hash__(self):
        return hash((self[0], self[1]))
