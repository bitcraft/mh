import collections, itertools



def intersect(a, b):
    return (((a.back   >= b.back   and a.back   < b.front)   or
             (b.back   >= a.back   and b.back   < a.front))  and
            ((a.left   >= b.left   and a.left   < b.right)   or 
             (b.left   >= a.left   and b.left   < a.right))  and
            ((a.bottom >= b.bottom and a.bottom < b.top)     or
             (b.bottom >= a.bottom and b.bottom < a.top)))

# BUG: collisions on right side are not correct


class BBox(list):
    """
    Rect-like class for defining area in 3d space.
    subclassed from list to provide fast index access

    Not hashable.

    Many of the methods here have not been extensively tested, but most should
    work as expected.
    """

    __slots__ = []


    def copy(self):
        return BBox(self)


    def move(self, x, y, z):
        self[0] += x
        self[1] += y
        self[2] += z


    def inflate(self, x, y, z):
        self[0] -= x / 2
        self[1] -= y / 2
        self[2] -= z / 2
        self[3] += x
        self[4] += y
        self[5] += z


    def scale(self, x, y, z):
        self[0] *= x
        self[1] *= y
        self[2] *= z
        self[3] *= x
        self[4] *= y
        self[5] *= z


    def clamp(self):
        raise NotImplementedError


    def clip(self, other):
        raise NotImplementedError


    def union(self, other):
        raise NotImplementedError

 
    def unionall(self, *rects):
        raise NotImplementedError


    def fit(self):
        raise NotImplementedError


    def normalized(self):
        """
        return a normalized bbox of this one
        """
        x, y, z, d, w, h = self
        if d < 0:
            x += d
            d = -d
        if w < 0:
            y += w
            w = -w
        if h < 0:
            z += h
            h = -h
        return BBox(x, y, z, d, w, h)


    def contains(self, other):
        raise NotImplementedError
        other = BBox(other)
        # this is not correct!
        return ((self[0] <= other.back) and
                (self[1] <= other.top) and
                (self[2] <= other.front) and
                (self[0] + self[4] >= other.right) and
                (self[1] + self[5] >= other.bottom) and
                (self[2] + self[3] >= other.back) and
                (self[0] + self[4] > other.left) and
                (self[1] + self[5] > other.top) and
                (self[2] + self[3] > other.front))


    def collidepoint(self, (x, y, z)):
        return (x >= self[0] and x < self[0] + self[3] and 
                y >= self[1] and y < self[1] + self[4] and
                z >= self[2] and z < self[2] + self[5])


    def collidebbox(self, other):
        return intersect(self, BBox(other))


    def collidelist(self, l):
        for i, bbox in enumerate(l):
            if intersect(self, bbox):
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
        return self[0]


    @property
    def left(self):
        return self[1]


    @property
    def bottom(self):
        return self[2]


    @property
    def front(self):
        return self[0] + self[3]


    @property
    def right(self):
        return self[1] + self[4]


    @property
    def top(self):
        return self[2] + self[5]


    @property
    def size(self):
        return self[3], self[4], self[5]


    @property
    def origin(self):
        return self[0], self[1], self[2]


    @property
    def bottomcenter(self):
        return self[0]+self[3]/2, self[1]+self[4]/2, self[2]


    @property
    def topcenter(self):
        return self[0]+self[3]/2, self[1]+self[4]/2, self[2]+self[5]


    @property
    def center(self):
        return self[0]+self[3]/2, self[1]+self[4]/2, self[2]+self[5]/2


    @property
    def x(self):
        return self[0]


    @property
    def y(self):
        return self[1]


    @property
    def z(self):
        return self[2]


    @property
    def depth(self):
        return self[3]


    @property
    def width(self):
        return self[4]


    @property
    def height(self):
        return self[5]
