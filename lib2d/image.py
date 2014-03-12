import pygame

from lib2d import res


"""
lazy image loading
"""


def get_defaults():
    return res.defaults.__dict__.copy()


class Image(object):
    """
    Surface class that is pickable.  :)
    """

    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self.args = args
        self.kwargs = get_defaults()
        self.kwargs.update(kwargs)
        self.loaded = False

    def load(self):
        self.loaded = True
        return res.loadImage(self.filename, *self.args, **self.kwargs)


class ImageTile(object):
    """
    Allows you to easily pull tiles from other images
    """

    def __init__(self, filename, tile, tilesize):
        self.image = Image(filename)
        self.tile = tile
        self.tilesize = tilesize

    def load(self):
        self.loaded = True
        if self.image.loaded:
            surface = self.image.load()
        else:
            surface = self.image.load()
        temp = pygame.Surface(self.tilesize).convert(surface)
        temp.blit(surface, (0, 0),
                  ((self.tilesize[0] * self.tile[0],
                    self.tilesize[1] * self.tile[1]),
                   self.tilesize))
        if self.image.kwargs['colorkey']:
            temp.set_colorkey(temp.get_at((0, 0)), pygame.RLEACCEL)
        return temp
