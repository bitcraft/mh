def intersect(a, b):
    return (((a.back   >= b.back   and a.back   < b.front)   or
             (b.back   >= a.back   and b.back   < a.front))  and
            ((a.left   >= b.left   and a.left   < b.right)   or 
             (b.left   >= a.left   and b.left   < a.right))  and
            ((a.bottom >= b.bottom and a.bottom < b.top)     or
             (b.bottom >= a.bottom and b.bottom < a.top)))

# BUG: collisions on right side are not correct

#def intersect(a, b):
#    return not (b.back > a.front or b.front < a.back or
#                b.left > a.right or b.right < a.left or
#                b.bottom > a.top or b.top < a.bottom)

class BBox(object):
    """
    Rect-like class for defining area in 3d space.

    Once created cannot be modified.  Hashable.
    """

    __slots__ = ['_x', '_y', '_z', '_w', '_h', '_d']

    def __init__(self, *arg):
        """
        should accept rect like object or tuple of two tuples or one tuple
        of four numbers, store :x,y,h,w
        """

        # hack!!!
        if len(arg) == 1:
            arg = arg[0]

        if isinstance(arg, BBox):
            self._x, self._y, self._z, self._w, self._h, self._d = arg
        elif isinstance(arg, list) or isinstance(arg, tuple):
            if len(arg) == 2:
                self._x, self._y, self._z = arg[0]
                self._w, self._h, self._d = arg[1]
            elif len(arg) == 6:
                self._x, self._y, self._z, self._w, self._h, self._d = arg
            else:
                raise ValueError, arg
        elif hasattr(arg, 'bbox'):
            self._x, self._y, self._z, self._w, self._h, self._d = arg.bbox
        else:
            try:
                self._x, self._y, self._z, self._w, self._h, self._d = arg
            except:
                raise ValueError, arg


    def __repr__(self):
        return "<bbox: {} {} {} {} {} {}>".format(
            self._x, self._y, self._z, self._w, self._h, self._d)

 
    def __len__(self): return 6


    def __getitem__(self, key):

        if key == 0:
            return self._x
        elif key == 1:
            return self._y
        elif key == 2:
            return self._z
        elif key == 3:
            return self._w
        elif key == 4:
            return self._h
        elif key == 5:
            return self._d
        raise IndexError, key


    def copy(self):
        return BBox(self)


    def move(self, x, y, z):
        return BBox(self._x + x, self._y + y, self._z + z,
                      self._w,     self._h,     self._d)


    def inflate(self, x, y):
        return Rect((self._x - x / 2, self._y - y / 2, self._z - z /2,
                     self._w + x,     self._h + y,     self._d + z))


    def clamp(self):
        raise NotImplementedError


    def clip(self, other):
        raise NotImplementedError


    def union(self, other):
        return Rect((min(self._x, other.left), min(self._y, other.top),
                     max(self._w, other.right), max(self._h, other.height)))

 
    def unionall(self, *rects):
        rects.append(self)
        front  = min([ r.front for r in rects ])
        left   = min([ r.left for r in rects ])
        bottom = min([ r.bottom for r in rects ])
        back   = max([ r.back for r in rects ]) 
        right  = max([ r.right for r in rects ])
        top    = max([ r.top for r in rects ])
        return Rect(front, left, bottom, depth, width, height)


    def fit(self):
        raise NotImplementedError


    def normalize(self):
        if self._w < 0:
            self._x += self._w
            self._w = -self._x
        if self._h < 0:
            self._y += self._h
            self._h = -self._y
        if self._d < 0:
            self._z += self._d
            self._d = -self._y


    def contains(self, other):
        other = BBox(other)
        return ((self._x <= other.left) and
                (self._y <= other.top) and
                (self._z <= other.front) and
                (self._x + self._w >= other.right) and
                (self._y + self._h >= other.bottom) and
                (self._z + self._d >= other.back) and
                (self._x + self._w > other.left) and
                (self._y + self._h > other.top) and
                (self._z + self._d > other.front))


    def collidepoint(self, (x, y, z)):
        return (x >= self._x and x < self._x + self._w and 
                y >= self._y and y < self._y + self._h and
                z >= self._z and z < self._z + self._z)


    def collidebbox(self, other):
        return intersect(self, BBox(other))


    def collidelist(self, l):
        for i, bbox in enumerate(l):
            if intersect(self, bbox):
                print i, bbox
                return i
        return -1


    def collidelistall(self, l):
        return [ i for i, bbox in enumerate(l)
                if intersect(self, bbox) ]


    def collidedict(self):
        raise NotImplementedError


    def collidedictall(self):
        raise NotImplementedError


    @property
    def back(self):
        return self._x


    @property
    def left(self):
        return self._y


    @property
    def bottom(self):
        return self._z


    @property
    def front(self):
        return self._x + self._d


    @property
    def right(self):
        return self._y + self._w


    @property
    def top(self):
        return self._z + self._h


    @property
    def size(self):
        return self._d, self._w, self._h


    @property
    def origin(self):
        return self._x, self._y, self._z


    @property
    def bottomcenter(self):
        return self._x + self._d / 2, self._y + self._w /2, self._z


    @property
    def width(self):
        return self._w


    @property
    def height(self):
        return self._h


    @property
    def depth(self):
        return self._d


    @property
    def x(self):
        return self._x


    @property
    def y(self):
        return self._y


    @property
    def z(self):
        return self._z
