from lib2d.tilemap import BufferedTilemapRenderer
from lib2d.objects import AvatarObject
from pygame import Rect, draw

import weakref


def screenSorter(a):
    return a[-1].x


class LevelCamera(object):
    """
    Base class for displaying maps.  Not really featured, here, you should
    subclass it.
    """

    def __init__(self, area, rect, tmxdata=None):
        rect = Rect(rect)
        self.rect = rect
        self.area = area
        self.set_extent(rect)

        # create a renderer for the map
        self.maprender = BufferedTilemapRenderer(tmxdata, rect)
        self.map_width = tmxdata.tilewidth * tmxdata.width
        self.map_height = tmxdata.tileheight*tmxdata.height
        self.blank = True

        # add the avatars
        #for child in self.area.getChildren():
        ##    if isinstance(child, AvatarObject):
        #        child.avatar.update(0)              # hack to re-init avatar

        self.ao = self.refreshAvatarObjects()
 

    def refreshAvatarObjects(self):
        return [ i for i in self.area.bodies.keys() if hasattr(i, "avatar")]
        

    # HACK
    def getAvatarObjects(self):
        if self.area.changedAvatars:
            self.area.changedAvatars = False
            self.ao = self.refreshAvatarObjects()
        return self.ao


    def set_extent(self, extent):
        """
        the camera caches some values related to the extent, so it becomes
        nessessary to call this instead of setting the extent directly.
        """

        self.extent = Rect(extent)
        self.half_width = self.extent.width / 2
        self.half_height = self.extent.height / 2
        self.width  = self.extent.width
        self.height = self.extent.height
        self.zoom = 1.0


    def update(self, time):
        self.maprender.update(None)
        for ao in self.refreshAvatarObjects():
            if ao: 
                # HACK
                try:
                   ao.avatar.update(time)
                except:
                    pass


    def center(self, pos):
        """
        center the camera on a pixel location.
        """

        x, y = self.toSurface(pos)

        if self.map_width > self.width:
            if x < self.half_width:
                x = self.half_width

            elif x > self.map_width - self.half_width - 1:
                x = self.map_width - self.half_width - 1

        else:
            x = self.map_width / 2


        if self.map_height > self.height:
            if y < self.half_height:
                y = self.half_height

            elif y > self.map_height - self.half_height:
                y = self.map_height - self.half_height
        else:
            y = self.map_height / 2

        self.extent.center = (x, y)
        self.maprender.center((x, y))


    def clear(self, surface):
        raise NotImplementedError


    def draw(self, surface):
        avatarobjects = self.refreshAvatarObjects()

        onScreen = []

        if self.blank:
            self.blank = False
            self.maprender.blank = True

        # quadtree collision testing would be good here
        for a in avatarobjects:
            bbox = self.area.getBBox(a)
            x, y, z, d, w, h = bbox
            x, y = self.toSurface((x, y, z))
            xx, yy = a.avatar.axis
            x += xx
            y += yy + h
            if self.extent.colliderect((x, y, w, h)):
                onScreen.append((a.avatar.image, Rect(self.toScreen((x, y)), (w, h)), 1, a, bbox))

        # should not be sorted every frame
        onScreen.sort(key=screenSorter)

        return self.maprender.draw(surface, onScreen)

        dirty = self.maprender.draw(surface, onScreen)

        clip = surface.get_clip()
        surface.set_clip(self.rect)

        for (x, y, w, h) in self.area.geoRect:
            draw.rect(surface, (128,128,255), \
            (self.toScreen(self.toSurface((0, x, y))), (w, h)), 1)

        for i, r, l, a in onScreen:
            x, y, z, d, w, h, = self.area.getBBox(a)
            x, y = self.toScreen(self.toSurface((x, y, z+h)))
            draw.rect(surface, (255,128,128), (x, y, w, h), 1)

        surface.set_clip(clip)
        return dirty


    def toScreen(self, (x, y)):
        """
        Transform the world to coordinates on the screen
        """

        return (x * self.zoom - self.extent.left + self.rect.left,
                y * self.zoom - self.extent.top + self.rect.top)


    def toSurface(self, pos):
        """ Translate world coordinates to coordinates on the surface """
        return pos[1], pos[2]

