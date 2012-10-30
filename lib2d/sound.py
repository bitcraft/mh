from lib2d import res
import pygame


"""
lazy sound loading
"""

def get_defaults():
    return res.defaults.__dict__.copy()


class Sound(object):
    """
    Sound class that is pickable.  :)
    """

    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self.args = args
        self.kwargs = get_defaults()
        self.kwargs.update(kwargs)
        self.loaded = False

    def load(self):
        self.loaded = True
        return res.loadSound(self.filename, *self.args, **self.kwargs)



