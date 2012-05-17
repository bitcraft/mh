"""
Module contains two classes for quadtree collision detection.

In Lib2d, they are used in various parts in rendering and collision detection
between 'sprites' and world geometry.

It is important to remember that once the quadtree's are useful for static
objects (which is why it is being used for world geometry).  There are
probably better solutions for moving objects.
"""


from rect import Rect
import pygame


NE, NW, SE, SW = range(4)



class FrozenRect(object):
    """
    This rect is hashable, unlike normal pygame rects
    contains a reference to another object
    """

    __slots__ = ['_left', '_top', '_width', '_height', '_value']

    def __init__(self, rect, value=None):
        self._left, self._top, self._width, self._height = rect
        self._value = value

    def __len__(self): return 4

    def __getitem__(self, key):
        if key == 0:
            return self._left
        elif key == 1:
            return self._top
        elif key == 2:
            return self._width
        elif key == 3:
            return self._height
        raise IndexError

    @property
    def value(self): return self._value

    @property
    def left(self): return self._left

    @property
    def top(self): return self._top

    @property
    def widht(self): return self._width

    @property
    def height(self): return self._height

    @property
    def right(self): return self._left + self._width

    @property
    def bottom(self): return self._top + self._height

    def __iter__(self):
        return iter([self._left, self._top, self._width, self._height])



# from http://pygame.org/wiki/QuadTree

class FastQuadTree(object):
    """An implementation of a quad-tree.
 
    This faster version of the quadtree class is tuned for pygame's rect
    objects, or objects with a rect attribute.  The return value will always
    be a set of a tuples that represent the items passed.  In other words,
    you will not get back the objects that were passed, just a tuple that
    describes it.

    Once the quadtree object is created, it cannot be modified.  Useful for
    static geometry.

    Items being stored in the tree must be a pygame.Rect or have have a
    .rect (pygame.Rect) attribute that is a pygame.Rect
        ...and they must be hashable.
    """

    __slots__ = ['items', 'cx', 'cy', 'nw', 'sw', 'ne', 'se']
 
    def __init__(self, items, depth=16, bounding_rect=None):
        """Creates a quad-tree.
 
        @param items:
            A sequence of items to store in the quad-tree. Note that these
            items must be a pygame.Rect or have a .rect attribute.
            
        @param depth:
            The maximum recursion depth.
            
        @param bounding_rect:
            The bounding rectangle of all of the items in the quad-tree. For
            internal use only.
        """
 
        # The sub-quadrants are empty to start with.
        self.nw = None
        self.ne = None
        self.se = None
        self.sw = None
        
        # If we've reached the maximum depth then insert all items into this
        # quadrant.
        depth -= 1
        if depth == 0 or not items:
            self.items = items
            return
 
        # Find this quadrant's center.
        if bounding_rect:
            bounding_rect = pygame.Rect( bounding_rect )
        else:
            # If there isn't a bounding rect, then calculate it from the items.
            bounding_rect = pygame.Rect( items[0] )
            for item in items[1:]:
                bounding_rect.union_ip( item )
        cx = self.cx = bounding_rect.centerx
        cy = self.cy = bounding_rect.centery
 
        self.items = []
        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []
 
        for item in items:
            # Which of the sub-quadrants does the item overlap?
            in_nw = item.left <= cx and item.top <= cy
            in_sw = item.left <= cx and item.bottom >= cy
            in_ne = item.right >= cx and item.top <= cy
            in_se = item.right >= cx and item.bottom >= cy

            # If it overlaps all 4 quadrants then insert it at the current
            # depth, otherwise append it to a list to be inserted under every
            # quadrant that it overlaps.
            if in_nw and in_ne and in_se and in_sw:
                self.items.append(item)
            else:
                if in_nw: nw_items.append(item)
                if in_ne: ne_items.append(item)
                if in_se: se_items.append(item)
                if in_sw: sw_items.append(item)
           
        # Create the sub-quadrants, recursively.
        if nw_items:
            self.nw = FastQuadTree(nw_items, depth, \
                      (bounding_rect.left, bounding_rect.top, cx, cy))
 
        if ne_items:
            self.ne = FastQuadTree(ne_items, depth, \
                      (cx, bounding_rect.top, bounding_rect.right, cy))

        if se_items:
            self.se = FastQuadTree(se_items, depth, \
                      (cx, cy, bounding_rect.right, bounding_rect.bottom))
  
        if sw_items:
            self.sw = FastQuadTree(sw_items, depth, \
                      (bounding_rect.left, cy, cx, bounding_rect.bottom))


    def hit(self, rect):
        """Returns the items that overlap a bounding rectangle.
 
        Returns the set of all items in the quad-tree that overlap with a
        bounding rectangle.
        
        @param rect:
            The bounding rectangle being tested against the quad-tree. This
            must possess left, top, right and bottom attributes.
        """
        
        # Find the hits at the current level.
        hits = set(tuple(self.items[i])
                   for i in rect.collidelistall(self.items))

        # Recursively check the lower quadrants.
        if self.nw and rect.left <= self.cx and rect.top <= self.cy:
            hits |= self.nw.hit(rect)
        if self.sw and rect.left <= self.cx and rect.bottom >= self.cy:
            hits |= self.sw.hit(rect)
        if self.ne and rect.right >= self.cx and rect.top <= self.cy:
            hits |= self.ne.hit(rect)
        if self.se and rect.right >= self.cx and rect.bottom >= self.cy:
            hits |= self.se.hit(rect)
 
        return hits



class FullQuadTree(object):
    """Another implementation of a quad-tree.

    Slower than the FastQuadTree, but is able to be modified at runtime and
    has slightly lower memory requirements.

    Only the root node of the tree is able to insert or remove nodes.
    Attempting to directly insert an item into a leaf node will throw an
    exception.
    """

    __slots__ = ['items', 'bounds', 'nw', 'sw', 'ne', 'se']

    def __init__(self, bounds=None):
        """
        Creates a quad tree node
        """

        # The sub-quadrants are empty to start with.
        self.nw = None
        self.ne = None
        self.se = None
        self.sw = None
        
        # Find this quadrant's center.
        if bounds:
            self.bounds = Rect(bounds)
        else:
            self.bounds = None 
 
        self.items = []


    def calc_bounds(self, quad=None):
        """
        return a iterator of all the bounding boxes of this node and the
        children.
        will raise exception if this is not the root node
        """
       
        if not self.bounds:
            raise AttributeError

        closed = []
        queue = [(self, None, self.bounds)]
        while queue:
            node, quad, bounds = queue.pop()
            closed.append(node)

            if quad:
                bounds = self._calc_bounds(quad, bounds)
                yield bounds
            else:
                yield self.bounds


            if self.nw and self.nw not in closed:
                queue.append((self.nw, NW, bounds))

            if self.ne and self.ne not in closed:
                queue.append((self.ne, NE, bounds))

            if self.sw and self.sw not in closed:
                queue.append((self.sw, SW, bounds))

            if self.se and self.se not in closed:
                queue.append((self.se, SE, bounds))


    def _calc_bounds(self, quad, bounds):
        size = bounds.width / 2, bounds.height / 2
        if quad == NW: return Rect(bounds.topleft, size)
        if quad == NE: return Rect(bounds.midtop, size)
        if quad == SW: return Rect(bounds.midleft, size)
        if quad == SE: return Rect(bounds.center, size)


    def remove(self, item):
        # Which of the sub-quadrants does the item overlap?
        in_nw = item.left <= self.cx and item.top <= self.cy
        in_sw = item.left <= self.cx and item.bottom >= self.cy
        in_ne = item.right >= self.cx and item.top <= self.cy
        in_se = item.right >= self.cx and item.bottom >= self.cy

        if in_nw and in_ne and in_se and in_sw:
            self.items.remove(item)
        else:
            if in_nw: self.nw.remove(item)
            if in_ne: self.ne.remove(item)
            if in_se: self.se.remove(item)
            if in_sw: self.sw.remove(item)


    def insert(self, item, max_depth=8, center=None):
        """
        insert an object into this quadtree node
        """

        # If we've reached the maximum depth then insert all items into this
        # quadrant.
        max_depth -= 1
        if max_depth == 0:
            self.items.append(item)
            return

        # get the bounds of this cell
        # it is calculated each time to save memory
        if center:
            cx, cy = center
        else:
            if self.bounds == None:
                raise AttributeError
            else:
                cx, cy = self.bounds.center

        # Which of the sub-quadrants does the item overlap?
        in_nw = item.left <= cx and item.top <= cy
        in_sw = item.left <= cx and item.bottom >= cy
        in_ne = item.right >= cx and item.top <= cy
        in_se = item.right >= cx and item.bottom >= cy
            
        # If it overlaps all 4 quadrants then insert it at the current
        # depth, otherwise append it to a list to be inserted under every
        # quadrant that it overlaps.
        if in_nw and in_ne and in_se and in_sw:
            self.items.append(item)
        else:
            if in_nw:
                if self.nw == None: self.nw = FullQuadTree()
                self.nw.insert(item, max_depth, (cx/2, cy/2))

            if in_ne:
                if self.ne == None: self.ne = FullQuadTree()
                self.ne.insert(item, max_depth, (cx * 1.5, cy/2))

            if in_se:
                if self.se == None: self.se = FullQuadTree()
                self.se.insert(item, max_depth, (cx/2, cy * 1/5))

            if in_sw:
                if self.sw == None: self.sw = FullQuadTree()
                self.sw.insert(item, max_depth, (cx * 1.5, cy * 1.5))


if __name__ == "__main__":
    import pygame
    import random
    from itertools import starmap, repeat, islice, izip



    dim = (320, 240)

    def group(l, n):
        return izip(*[islice(l, i, None, n) for i in xrange(n)]) 


    qt = FullQuadTree((0,0,dim[0], dim[1]))
    data = starmap(random.randint, repeat((0, dim[0]/2), 400))
    rects = [ Rect(r).normalize() for r in group(data, 4) ]
    [ qt.insert(r) for r in rects ]

    pygame.init()
    screen = pygame.display.set_mode(dim)
    pygame.display.set_caption('qt test')

    screen.fill((192,192,192))

    for bounds in qt.calc_bounds():
        pygame.draw.rect(screen, (0,0,0), bounds, 1)
        
    queue = [qt]
    while queue:
        node = queue.pop()

        #for item in node.items:
        #    pygame.draw.rect(screen, (128,32,32), item, 1)

        neighbors = (node.nw, node.ne, node.sw, node.se)
        queue.extend(n for n in neighbors if not n == None)

    pygame.display.flip()

    run = True
    while run:
        try:
            event = pygame.event.wait()
            if ((event.type == pygame.QUIT) or 
                (event.type == pygame.KEYDOWN)): 
                run = False

        except KeyboardInterrupt:
            run = False


