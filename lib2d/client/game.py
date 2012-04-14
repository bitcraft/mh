#!/usr/bin/env python

from lib2d.statedriver import driver as sd
from lib2d import gfx
import pygame


class Game(object):
    def __init__(self):
        self.config = {}
        pygame.init()
        pygame.mixer.init()
        gfx.init()
        self.sd = sd
        self.sd.set_parent(self)

    def load_config(self, location):
        pass

    def get_config(self):
        return self.config

    def get_screen(self):
        return gfx.screen

    def start(self):
        pass


