from pygame.rect import Rect

from lib2d.tilemap import BufferedTilemapRenderer
from lib2d.objects import AvatarObject


def screenSorter(x):
    return x[1][1]


class AreaCamera(object):
    """
    Base class for displaying maps.  Not really featured, here, you should
    subclass it.
    """

    def __init__(self, area, extent=None, tmxdata=None):
        self.area = area
        self.set_extent(extent)
        self.zoom = 1.0
        self.avatars = []

        # create a renderer for the map
        self.maprender = BufferedTilemapRenderer(tmxdata, self.extent.size)

        self.map_width = tmxdata.tilewidth * tmxdata.width
        self.map_height = tmxdata.tileheight*tmxdata.height
        self.center(self.extent.center)
        self.blank = True

        # load the children
        for child in self.area.getChildren():
            child.load()

        # add the avatars
        for child in self.area.getChildren():
            if isinstance(child, AvatarObject):
                child.avatar.update(0)              # hack to re-init avatar
                self.avatars.append(child.avatar)


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


    def update(self, time):
        self.maprender.update(None)
        [ a.update(time) for a in self.avatars ]


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


    def draw(self, surface, origin=(0,0)):
        avatars = []
        for a in self.avatars:
            aWidth, aHeight = a.get_size()
            d, w, h = a.getSize()
            x, y = self.toSurface(a.getPosition())

            rect = Rect((x-(aWidth-w)/2, y-aHeight+d, aWidth, aHeight))
            if self.extent.colliderect(rect):
                x, y = self.toScreen(a.getPosition())
                x += origin[0]
                y += origin[1]
                rect = Rect((x-(aWidth-w)/2, y-aHeight+d, aWidth, aHeight))
                avatars.append((a, rect))

        onScreen = [ (a.image, r, 2) for a, r in avatars ]
        onScreen.sort(key=screenSorter)

        self.maprender.draw(surface, onScreen, origin)


    def toScreen(self, pos):
        """
        Transform the world to coordinates on the screen
        """

        x = pos[1] * self.zoom - self.extent.left
        y = pos[0] * self.zoom - self.extent.top

        # if there is a z value, just subtract it from y
        try:
            y -= pos[2]
        except:
            pass

        return x, y


    def toSurface(self, pos):
        """ Translate world coordinates to coordinates on the surface """
        return pos[1], pos[0]
