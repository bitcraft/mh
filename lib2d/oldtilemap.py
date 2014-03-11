"""
rewrite of the tilmap engine for lib2d.

this time has tiled TMX maps built in and required
"""

from pygame import Surface, Rect, draw
from itertools import product, chain
from math import ceil


# this image will be used when a tile cannot be loaded
def generateDefaultImage(size):
    i = Surface(size)
    i.fill((0, 128, 128))
    i.set_alpha(128)
    return i


class ScreenTile(Rect):
    def __init__(self, x, y, rect):
        Rect.__init__(self, rect)
        self.x = x
        self.y = y


class BufferedTilemapRenderer(object):
    """
    Class to render a map onto a buffer that is suitable for blitting onto
    the screen as one surface, rather than a collection of tiles.

    The class supports differed rendering, multiple layers, a collision layer
    and a small memory footprint.

    Jitter is unavoidable becuase python's interpreter is not time sensitive
    and will sometimes just slow everything down.

    This class works well for maps that operate on a small display and where
    the map is much larger than the display. 
    """

    def __init__(self, path, size, **kwargs):
        import tmxloader
        import quadtree

        data = tmxloader.load_pygame(path, **kwargs)

        self.colorkey = kwargs.get("force_colorkey", False)

        self.default_image = generateDefaultImage((data.tilewidth,
                                                  data.tileheight))

        left, self.xoffset = divmod(size[0] / 2, data.tilewidth)
        top,  self.yoffset = divmod(size[1] / 2, data.tileheight)

        self.view = Rect(left,top, (size[0] / data.tilewidth), 
                        (size[1] / data.tileheight))

        self.oldX = self.xoffset + (left * data.tilewidth) 
        self.oldY = self.yoffset + (top  * data.tileheight)

        self.bufferWidth  = size[0] + data.tilewidth * 2
        self.bufferHeight = size[1] + data.tileheight * 2

        self.size = size

        self.blitPerUpdate = 4
        self.background_update = 1
        self.data = data
        self.queue = []

        self.buffer = Surface((self.bufferWidth, self.bufferHeight))

        if self.colorkey:
            self.buffer.fill(self.colorkey)

        # the layer quadtree is used to correctly draw tiles that are over
        # sprites
        rects = []
        p = product(range(self.view.width+2), range(self.view.height+2))
        for x, y in p:
            rect = Rect((x*self.data.tilewidth,y*self.data.tileheight),
                        (self.data.tilewidth, self.data.tileheight))
            rects.append(rect)

        self.layerQuadtree = quadtree.QuadTree(rects, 4)

        self.blank = True

    def center(self, (x, y)):
        """
        center the map on a pixel

        opt: ok
        """

        x, y = int(x), int(y)

        if (self.oldX == x) and (self.oldY == y):
            return

        # calc the new postion in tiles and offset
        left, self.xoffset = divmod(x-self.size[0]/2, self.data.tilewidth)
        top,  self.yoffset = divmod(y-self.size[1]/2, self.data.tileheight) 

        # determine if tiles should be redrawn
        dx = left - self.view.left
        dy = top - self.view.top

        # determine which direction the map is moving, then
        # adjust the offsets to compensate for it:
        #    make sure the leading "edge" always has extra row/column of tiles
        #    see "small map debug mode" for a visual explanation!

        if self.oldX > x:
            if self.xoffset < self.data.tilewidth:
                self.xoffset += self.data.tilewidth
                dx -= 1

        if self.oldY > y:
            if self.yoffset < self.data.tileheight:
                self.yoffset += self.data.tileheight
                dy -= 1

        # don't adjust unless we have to
        if not (dx, dy) == (0,0):
            self.adjustView((int(dx), int(dy)))

        self.oldX, self.oldY = x, y

    def makeCollisionLayer(self, layer, gid=None):
        """
        Builds a Quadtree for collision detection using tiles from the
        specified layer and tile.  The quadtree can be queried for collisions
        between a rect and the layer, but not between objects in the layer.

        The quad tree reduces the number of checks that must be made and is
        overall better than a brute force collision check.
        """
        
        import quadtree
        import maputils

        if gid == None:
            gid = self.data.gidmap[self.data.tilesets[-1].firstgid]
        layer_data = self.data.getLayerData(layer)
        p = product(range(self.data.width),range(self.data.height))
        points = [ (x,y) for (x,y) in p if layer_data[y][x] == gid ]
        rects=maputils.simplify(points,self.data.tilewidth,self.data.tileheight)
        self.collisionQuadtree = quadtree.QuadTree(rects, 8)

    def getTileImage(self, (x, y, l)):
        """
        Return a surface for this position.  Returns a blank tile if cannot be
        loaded.
        """

        if (x < 0 ) or (y < 0):
            return self.default_image
        if (x >= self.data.width) or (y >= self.data.height):
            return self.default_image

        return self.data.get_tile_image(x, y, l)

    def scroll(self, v):
        """
        move the background in pixels
        """

        self.center((x + self.oldX, y + self.oldY))

    def adjustView(self, (x, y)):
        """
        adjusts the view by re-tiling the background

        v is a tuple that expresses how the axis should be adjusted in tiles,
        not pixels.

        for example v=(1, 0) will shift the map one tile to the right and fill
        the blit queue with the tiles needed to complete it.

        if background updating is not enabled for whatever reason, then the
        buffer will be redrawn here.

        this method is mostly for internal use only
        """

        self.flushQueue()

        self.view.move_ip((x, y))

        # scroll the image (much faster than reblitting the tiles!)
        self.buffer.scroll(-x * self.data.tilewidth, -y * self.data.tileheight)

        # queue the missing tiles
        self.queueEdgeTiles((x, y))

        # the the map is scrolled past the edge
        # we should draw the new tiles right away
        if (abs(x) > 1) or (abs(y) > 1):
            self.flushQueue()

    def optSurfaces(self, surface=None, depth=None, flags=0):
        """
        The display may have changed since the map was loaded.
        Calling this on will convert() all the surfaces to the same format
        as the surface passed.
        """

        if (surface==depth==None) and (flags==0):
            raise ValueError, "Need to pass a surface, depth, for flags"

        if surface:
            for i, t in enumerate(self.tilemap.images):
                if not t == 0: self.tilemap.images[i] = t.convert(surface)
            self.buffer = self.buffer.convert(surface)

        elif depth or flags:
            for i, t in enumerate(self.tilemap.images):
                if not t == 0:
                    self.tilemap.images[i] = t.convert(depth, flags)
            self.buffer = self.buffer.convert(depth, flags)

    def queueEdgeTiles(self, (x, y)):
        """
        add the tiles on the edge that need to be redrawn to the queue also,
        for colorkey layers, we will fill the new edge with the colorkey color
        here

        uses a standard python list for the queue
        override if you want a different type of queue

        for internal use only
        """

        # right
        if x > 0:
            for xx in range(x):
                self.queue.extend([
                    (self.view.right + 1 - xx, yy)
                    for yy in range(self.view.top, self.view.bottom + 2) ])

            # "clear" the area to be redrawn
            r = ((self.bufferWidth - (abs(x) * self.data.tilewidth), 0),
                (abs(x) * self.data.tilewidth, self.bufferHeight))
            self.buffer.fill(self.colorkey, r)

        # left
        elif x < 0:
            for xx in range(abs(x)):
                self.queue.extend([
                    (self.view.left + xx, yy)
                    for yy in xrange(self.view.top, self.view.bottom + 2) ])

            # "clear" the area to be redrawn
            r = ((0, 0),
                (abs(x) * self.data.tilewidth, self.bufferHeight))
            self.buffer.fill(self.colorkey, r)

        # down
        if y > 0:
            for yy in range(y):
                self.queue.extend([
                    (xx, self.view.bottom + 1 - yy)
                    for xx in xrange(self.view.left, self.view.right + 2) ])

            # "clear" the area to be redrawn
            r = ((0, self.bufferHeight - (abs(y) * self.data.tileheight)),
                (self.bufferWidth, abs(y) * self.data.tileheight))
            self.buffer.fill(self.colorkey, r)

        # up
        elif y < 0:
            for yy in range(abs(y)):
                self.queue.extend([
                    (xx, self.view.top + yy)
                    for xx in xrange(self.view.left, self.view.right + 2) ])

            # "clear" the area to be redrawn
            r = ((0, 0),
                (self.bufferWidth, abs(y) * self.data.tileheight))
            self.buffer.fill(self.colorkey, r)

    def draw(self, surface, sprites=[]):
        """
        draw the map onto a surface.

        for the illusion of depth, you must supply a list of surfaces to blit.
        the list should be a list of tuples (surface, rect, layer)
        """

        if self.blank:
            self.redraw()
            self.blank = False

        tw = self.data.tilewidth
        th = self.data.tileheight

        # blit a few tiles to the buffer that are in the queue
        for i in range(self.blitPerUpdate):
            try:
                x, y = self.queue.pop()
            except:
                break

            for l in range(len(self.data.layers)):
                image = self.getTileImage((x, y, l))
                if not image == 0:
                    pos = (x * tw - (self.view.left * tw),
                           y * th - (self.view.top * th))
                    self.buffer.blit(image, pos)

        surface.blit(self.buffer, (-self.xoffset,-self.yoffset))
        dirty = [ (surface.blit(a[0], a[1]), a[2]) for a in sprites ]

        # redraw the tiles are are above the sprites
        for dirtyRect, layer in dirty:
            dirtyRect = dirtyRect.move(self.xoffset, self.yoffset)
            for r in self.layerQuadtree.hit(dirtyRect):
                x, y, tw, th = r
                for toplayer in range(layer, len(self.data.tilelayers)):
                    tile = self.getTileImage((x/tw + self.view.left,
                                              y/th + self.view.top, toplayer))
                    if not tile == 0:
                        surface.blit(tile, (x-self.xoffset,
                                            y-self.yoffset))


    def flushQueue(self):
        """
        draw all tiles that are sitting in the queue
        """

        tw = self.data.tilewidth
        th = self.data.tileheight
        blit = self.buffer.blit
        getTile = self.getTileImage
        left, top = self.view.topleft
 
        for x, y in self.queue:
            for l in range(len(self.data.layers)):
                image = getTile((x, y, l))
                if not image == 0:
                    pos = (x * tw - (left * tw),
                           y * th - (top * th))
                    blit(image, pos)

        self.queue = []

    def redraw(self):
        """
        redraw the visible portion of the map, it is slow.

        should be called right after the map is created to initialize the the
        buffer.  will be slow, you've been warned.
        """

        blit = self.buffer.blit
        getTile = self.getTileImage
        ox, oy = self.view.topleft
        tw = self.data.tilewidth
        th = self.data.tileheight

        p=product(xrange(self.view.width+2),
                  xrange(self.view.height+2),
                  xrange(len(self.data.tilelayers)))

        for x,y,l in p:
            image = getTile((x+ox, y+oy, l))
            if not image == 0: blit(image, (x * tw, y * th))

    def toScreen(self, (x, y)):
        """
        Adjusted for change in the view

        opt: ok
        """

        return (x*self.data.tilewidth - (self.view.left*self.data.tilewidth),
                y*self.data.tileheight - (self.view.top*self.data.tileheight))
