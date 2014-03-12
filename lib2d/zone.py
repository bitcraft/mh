"""
Zones are a special construct that detects when objects are inside of them
"""

from pygame import Rect

from objects import GameObject



# expects to be given a PyTMX object node
class Zone(GameObject):
    def __init__(self, data):
        GameObject.__init__(self)
        self.extent = Rect(data.x, data.y, data.width, data.height)
        if hasattr(data, 'points'):
            self.points = data.points
        else:
            self.points = None
        self.name = data.name
        self.properties = data.properties

        self.entered = False
