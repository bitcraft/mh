#!/usr/bin/env python

from lib2d import res, gfx
import pygame



class Game(object):
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        gfx.init()

    def get_screen(self):
        return gfx.screen

    def start(self):
        pass


