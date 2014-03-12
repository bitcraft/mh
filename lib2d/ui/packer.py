import collections
import itertools

import pygame

from lib2d.ui.element import Element


class GridPacker(Element):
    """
    positions widgets in a grid
    """

    def __init__(self):
        Element.__init__(self)
        self.ordered = []
        self.free = collections.deque()


    @property
    def elements(self):
        return itertools.chain(self.free, self.ordered)


    def add(self, element, free=False):
        if free:
            self.free.appendleft(element)
        else:
            self.ordered.append(element)


    def remove(self, element):
        try:
            self.ordered.remove(element)
        except:
            pass

        try:
            self.free.remove(element)
        except:
            pass


    def resize(self):
        """ resize the rects for the panes """
        Element.resize(self)

        if len(self.ordered) == 1:
            self.ordered[0].rect = self.rect.copy()

        elif len(self.ordered) == 2:
            w, h = self.rect.size
            self.ordered[0].rect = pygame.Rect((0, 0, w, h / 2))
            self.ordered[1].rect = pygame.Rect((0, h / 2, w, h / 2))

        elif len(self.ordered) == 3:
            w, h = self.rect.size
            self.ordered[0].rect = pygame.Rect((0, 0, w, h / 2))
            self.ordered[1].rect = pygame.Rect((0, h / 2, w / 2, h / 2))
            self.ordered[2].rect = pygame.Rect((w / 2, h / 2, w / 2, h / 2))

        elif len(self.ordered) == 4:
            w = self.rect.width / 2
            h = self.rect.height / 2
            self.ordered[0].rect = pygame.Rect((0, 0, w, h))
            self.ordered[1].rect = pygame.Rect((w, 0, w, h))
            self.ordered[2].rect = pygame.Rect((0, h, w, h))
            self.ordered[3].rect = pygame.Rect((w, h, w, h))
