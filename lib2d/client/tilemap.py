"""
rewrite of the tilmap engine for lib2d.

this time has tiled TMX maps built in and required
"""

import pygame
from itertools import product, chain, ifilter


# this image will be used when a tile cannot be loaded
def generateDefaultImage(size):
    i = pygame.Surface(size)
    i.fill((0, 0, 0))
    i.set_alpha(128)
    return i


class BufferedTilemapRenderer(object):
    """
    Class to render a map onto a buffer that is suitable for blitting onto
    the screen as one surface, rather than a collection of tiles.

    The class supports differed rendering and multiple layers

    Jitter is unavoidable becuase python's interpreter is not time sensitive
    and will sometimes just slow everything down.

    This class works well for maps that operate on a small display and where
    the map is much larger than the display.

    For differed rendering to work, you will need to call update() often.

    The original library for this, Lib2d updates 4 times for every draw.  To
    take advantage of the processing done inbetween screen updates, update()
    will blit any tiles needed to the offscreen buffer.
    """

    def __init__(self, tmx, rect, **kwargs):
        import tmxloader

        self.default_image = generateDefaultImage((tmx.tilewidth,
                                                   tmx.tileheight))
        self.tmx = tmx
        self.setSize(rect.size)
        self.rect = rect


    def setSize(self, size):
        """
        There are many variables that are cached for quick drawing, so it is
        necessary to set the size with the function.
        """

        import quadtree

        left, self.xoffset = divmod(size[0] / 2, self.tmx.tilewidth)
        top,  self.yoffset = divmod(size[1] / 2, self.tmx.tileheight)

        self.view = pygame.Rect(left,top, (size[0] / self.tmx.tilewidth), 
                               (size[1] / self.tmx.tileheight))

        self.oldX = self.xoffset + (left * self.tmx.tilewidth) 
        self.oldY = self.yoffset + (top  * self.tmx.tileheight)

        self.bufferWidth  = size[0] + self.tmx.tilewidth * 2
        self.bufferHeight = size[1] + self.tmx.tileheight * 2

        self.size = size

        self.halfWidth  = size[0] / 2
        self.halfHeight = size[1] / 2

        # this is where the magic happens
        self.buffer = pygame.Surface((self.bufferWidth, self.bufferHeight))

        # how many tiles are blitted to the buffer during an update
        self.blitPerUpdate = int(self.view.width * 1.5)

        # quadtree is used to correctly draw tiles that cover 'sprites'
        rects = []
        p = product(range(self.view.width+2), range(self.view.height+2))
        for x, y in p:
            rect = pygame.Rect((x*self.tmx.tilewidth,y*self.tmx.tileheight),
                               (self.tmx.tilewidth, self.tmx.tileheight))
            rects.append(rect)
        self.layerQuadtree = quadtree.FastQuadTree(rects, 4)

        self.blank = True 
        self.queue = None


    def center(self, (x, y)):
        """
        center the map on a pixel

        opt: ok
        """

        x, y = int(x), int(y)

        if (self.oldX == x) and (self.oldY == y):
            return

        # calc the new postion in tiles and offset
        left, self.xoffset = divmod(x-self.halfWidth,  self.tmx.tilewidth)
        top,  self.yoffset = divmod(y-self.halfHeight, self.tmx.tileheight)
 
        # determine if tiles should be redrawn
        dx = left - self.view.left
        dy = top - self.view.top

        # determine which direction the map is moving, then
        # adjust the offsets to compensate for it:
        #    make sure the leading "edge" always has extra row/column of tiles
        #    see "small map debug mode" for a visual explanation!

        if self.oldX > x:
            if self.xoffset < self.tmx.tilewidth:
                self.xoffset += self.tmx.tilewidth
                dx -= 1

        if self.oldY > y:
            if self.yoffset < self.tmx.tileheight:
                self.yoffset += self.tmx.tileheight
                dy -= 1

        # don't adjust unless we have to
        if not (dx, dy) == (0,0):
            self.adjustView((int(dx), int(dy)))

        self.oldX, self.oldY = x, y


    def getTileImage(self, (x, y, l)):
        """
        Return a surface for this position.  Returns a blank tile if cannot be
        loaded.
        """

        try:
            return self.tmx.getTileImage(x, y, l)
        except:
            return self.default_image


    def scroll(self, (x, y)):
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

        # make sure that the map is completely drawn
        self.flushQueue()

        self.view = self.view.move((x, y))

        # scroll the image (much faster than reblitting the tiles!)
        self.buffer.scroll(-x * self.tmx.tilewidth, -y * self.tmx.tileheight)

        # queue the missing tiles
        self.queueEdgeTiles((x, y))

        # prevent edges on the screen if moving too fast or camera is shaking
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

        if self.queue == None:
            self.queue = iter([])


        # right
        if x > 0:
            p=product(xrange(self.view.right+1, self.view.right-x,-1),
                      xrange(self.view.top, self.view.bottom + 2),
                      xrange(len(self.tmx.visibleTileLayers)))
            self.queue = chain(p, self.queue) 

        # left
        elif x < 0:
            p=product(xrange(self.view.left, self.view.left - x),
                      xrange(self.view.top, self.view.bottom + 2),
                      xrange(len(self.tmx.visibleTileLayers)))
            self.queue = chain(p, self.queue) 

        # bottom
        if y > 0:
            p=product(xrange(self.view.left, self.view.right + 2),
                      xrange(self.view.bottom+1, self.view.bottom-y, -1),
                      xrange(len(self.tmx.visibleTileLayers)))
            self.queue = chain(p, self.queue) 

        # top
        elif y < 0:
            p=product(xrange(self.view.left, self.view.right + 2),
                      xrange(self.view.top, self.view.top - y),
                      xrange(len(self.tmx.visibleTileLayers)))
            self.queue = chain(p, self.queue)


    def update(self, time):
        """
        the drawing operations and management of the buffer is handled here.
        if you notice that the tiles are being drawn while the screen
        is scrolling, you will need to adjust the number of tiles that are
        bilt per update.
        """

        if self.queue:
            bufblit = self.buffer.blit
            getTile = self.getTileImage
            ltw = self.tmx.tilewidth * self.view.left
            tth = self.tmx.tileheight * self.view.top
            tw = self.tmx.tilewidth
            th = self.tmx.tileheight

            for i in range(self.blitPerUpdate):
                try:
                    x,y,l = next(self.queue)
                except StopIteration:
                    self.queue = None
                    break

                image = getTile((x, y, l))
                if not image == 0:
                    bufblit(image, (x * tw - ltw, y * th - tth))


    def draw(self, surface, surfaces=[]):
        """
        draw the map onto a surface.
    
        surfaces may optionally be passed that will be blited onto the surface.
        this must be a list of tuples containing a layer number, image, and
        rect in screen coordinates.  surfaces will be drawn in oder passed,
        and will be correctly drawn with tiles from a higher layer overlap
        the surface.

        passing a list here will correctly draw the surfaces to create the
        illusion of depth.

        TODO: make sure the soccrect rects are returned for dirty updates
        """

        if self.blank:
            self.redraw()
            self.blank = False

        surblit = surface.blit
        left, top = self.view.topleft
        ox, oy = self.xoffset, self.yoffset
        ox -= self.rect.left
        oy -= self.rect.top
        getTile = self.getTileImage

        # set clipping.  need to do this, otherwise the map will draw outside
        # its defined area.
        origClip = surface.get_clip()
        surface.set_clip(self.rect)

        surblit(self.buffer, (-ox, -oy))

        # TODO: make sure to filter out surfaces outside the screen
        dirty = [ (surblit(a[0], a[1]), a[2]) for a in surfaces ]

        # TODO: new sorting method for surfaces
        #       on each update, avatar sets a sorting flag if moved
        #       on drawing, avatars with the 'sort' flag are checked for
        #       collisions with other sprites, then those two are sorted
        #       finally, the 'sort' flag is set to 0 and draw order is saved

        # redraw tiles that overlap surfaces that were passed in
        for dirtyRect, layer in dirty:
            dirtyRect = dirtyRect.move(ox, oy)
            for r in self.layerQuadtree.hit(dirtyRect):
                x, y, tw, th = r
                if dirtyRect.bottom < y+th:
                    # create illusion of depth by sorting images and
                    # tiles that are on the same layer.  if the image is
                    # lower than the tile, don't reblit the tile
                    tile = getTile((x/tw + left, y/th + top, layer))
                    if not tile == 0:
                        surblit(tile, (x-ox, y-oy))

                for l in range(layer+1,len(self.tmx.visibleTileLayers)):
                    # there is a collision between a tile and a image, so
                    # we simply reblit the affected tiles over the sprite
                    tile = getTile((x/tw + left, y/th + top, l))
                    if not tile == 0:
                        surblit(tile, (x-ox, y-oy))

        # restore clipping area
        surface.set_clip(origClip)

        return self.rect


    def flushQueue(self):
        """
        draw all tiles that are sitting in the queue
        """

        if self.queue:
            tw = self.tmx.tilewidth
            th = self.tmx.tileheight
            blit = self.buffer.blit
            ltw = self.view.left * tw
            tth = self.view.top * th
            getTile = self.getTileImage

            images = [ (i, getTile(i)) for i in self.queue ]

            [ blit(image, (x*tw-ltw, y * th-tth))
              for ((x,y,l), image) in ifilter(lambda x: x[1], images) ]

            self.queue = None


    def redraw(self):
        """
        redraw the visible portion of the buffer, it is slow.

        should be called right after the map is created to initialize the the
        buffer.  will be slow, you've been warned.
        """

        self.queue = product(xrange(self.view.left, self.view.right + 2),
                             xrange(self.view.top, self.view.bottom + 2),
                             xrange(len(self.tmx.visibleTileLayers)))

        self.flushQueue()


    def toScreen(self, (x, y)):
        """
        Adjusted for change in the view

        opt: ok
        """

        return (x*self.tmx.tilewidth - (self.view.left*self.tmx.tilewidth),
                y*self.tmx.tileheight - (self.view.top*self.tmx.tileheight))


def floydsteinberg(surface):
    """SLOW"""

    def closest(color):
        r = 255 if color[0] > 128 else 0
        g = 255 if color[1] > 128 else 0
        b = 255 if color[2] > 128 else 0
        return r, g, b

    def diff(a, b):
        return a[0]-b[0], a[1]-b[1], a[2]-b[2]

    def calc(s, p, c, e):
        try:
            s.set_at(p, [ v + c * e[i] for i, v in enumerate(s.get_at(p)[:3]) ])
        except:
            pass

    sx, sy = surface.get_size()
    surface = surface.copy()
    surface.lock()
    cf1 = 7/16
    cf2 = 3/16
    cf3 = 5/16
    cf4 = 1/16
    p = product(xrange(sx), xrange(sy))
    for x, y in p:
        op = surface.get_at((x, y))
        np = closest(op)
        surface.set_at((x, y), np)
        error = diff(op, np)
        calc(surface, (x+1,y), cf1, error)
        calc(surface, (x-1,y+1), cf2, error)
        calc(surface, (x,y+1), cf3, error)
        calc(surface, (x+1,y+1), cf4, error)
    surface.unlock()
    return surface


class ShadowMask(object):
    """
    Renders shadows onto a map by blitting black tiles with dittered tiles, or
    optionally black tiles with an alpha value to simulate shadows.
    """

    def __init__(self, grad):
        image = res.loadImage(grad)
        iw, self.th = image.get_size()
        self.tw = iw / 64

        for x in xrange(0,iw,tw):
            self.images = [ image.subsurface((x,0,self.tw,self.th)) ]

    def center(self, (x,y)):
        pass

    def draw(self, surface, origin):
        pass        
