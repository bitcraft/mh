from lib2d.client.gamestate import GameState
from lib2d.client.buttons import *
from lib2d.client.statedriver import driver as sd
from lib2d.common import res
import pygame

from dialog import TextDialog 

import os.path



class Cutscene(GameState):
    """
    This state can read a text file and make a series of dialogs from it.

    Each individual dialog must be it's own line.
    Blank lines are ignored.
    Comments may be added using a #.  Inline comments are not supported.

    Special commands are available:

    #image:filename             load the image and blit it
    #image-colorkey:filename    load image and use top-left corner as colorkey
    #image-alpha:filename       load image with per-pixel alpha

    if you add a "+" before the filename, the image will be scaled to fit the
    screen

    """

    def __init__(self, path):
        GameState.__init__(self)

        self.dialogs = []

        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line != "":
                    self.dialogs.append(line)

        self.dialogs.reverse()

        self.queue_image = None
        self.queue_music = None
        self.queue_dialog = None

    def deactivate(self):
        GameState.deactivate(self)
        res.fadeoutMusic()

    def activate(self):
        GameState.activate(self)

        # this is hack, for sure, but ensure our music will start
        # playing if we are being transition'd from another state

        if self.dialogs[-1][:6] == "#music":
            text = self.dialogs.pop()
            tag, path = text.split(":")
            #res.playMusic(path, loops=-1)
        
        self.cleared = False

    def reactivate(self):
        GameState.reactivate(self)
        self.cleared = False

    def draw(self, surface):
        if not self.cleared:
            surface.fill((0,0,0))
            self.cleared = True

            if self.queue_image != None:
                surface.blit(*self.queue_image)

    def update(self, time):
        if self.queue_dialog:
            if self.cleared:
                sd.start(self.queue_dialog)
                self.queue_dialog = None
                self.cleared = False

        else:

            try:
                text = self.dialogs.pop()
            except IndexError:
                sd.done()
                return

            if text[:6] == "#image":
                fill = False
                tag, path = text.split(":")

                if path[0] == "+":
                    fill = True
                    path = path[1:]

                if tag[-8:] == "colorkey":
                    image = res.loadImage(path, colorkey=1)
                elif tag[-5:] == "alpha":
                    image = res.loadImage(path, alpha=1)
                else:
                    image = res.loadImage(path)
     
                rect = image.get_rect()
                if fill:
                    size = [ int(i) for i in sd.get_size() ]
                    x = size[0] - rect.w
                    y = size[1] - rect.h
                    r = float(rect.w) / rect.h
                    if x > y:
                        rect = pygame.Rect((0,0,size[0],size[1]*r))
                    else:
                        rect = pygame.Rect((0,0,size[0]*r,size[1]))

                    rect.center = size[0] / 2, size[1] / 2
                    image = pygame.transform.smoothscale(image, rect.size)
                else:
                    rect.topleft = ((sd.get_size()[0]/2)-(rect.width/2), 10)
                
                self.queue_image = (image, rect)
                self.cleared = False

            elif text[:6] == "#music":
                tag, path = text.split(":")
                self.queue_music = path

            else:
                self.queue_dialog = TextDialog(text)


    def handle_event(self, event):
        pass

    def handle_commandlist(self, cmdlist):
        pass
