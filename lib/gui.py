"""
various things for the gui
"""


class TimeDisplay(object):
    def update(self, time):
        self.time += time


    def draw(self, surface):
        print self.time
