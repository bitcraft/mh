"""
Misc. software cursor.
"""

from pygame.transform import flip
import pygame


class Cursor(object):
    """
    Cursor base class that has a shadow and flips while moving
    """

    def __init__(self, image, hotspot=(0, 0)):
        """
        surface = Global surface to draw on
        cursor  = surface of cursor (needs to be specified when enabled!)
        hotspot = the hotspot for your cursor
        """
        self.enabled = 0
        self.image = None
        self.shadow = None
        self.hotspot = hotspot
        self.bg = None
        self.offset = 0, 0
        self.old_pos = 0, 0
        self.direction = 0
        self.do_flip = False

        if image:
            self.setImage(image, hotspot)


    def enable(self):
        """
        Enable the GfxCursor (disable normal pygame cursor)
        """
        raise NotImplementedError


    def disable(self):
        """
        Disable the GfxCursor (enable normal pygame cursor)
        """
        raise NotImplementedError


    def make_shadow(self):
        # generate an image for use as a shadow
        # this is a kludge
        self.shadow = self.image.copy()
        colorkey = self.image.get_at((0, 0))
        self.shadow.set_colorkey(colorkey)
        for x in range(self.image.get_rect().width):
            for y in range(self.image.get_rect().height):
                if not self.shadow.get_at((x, y)) == colorkey:
                    self.shadow.set_at((x, y), (0, 0, 0))
        self.shadow.convert()
        self.shadow.set_alpha(60)


    def setImage(self, image, hotspot=(0, 0)):
        """
        Set a new cursor surface
        """
        self.image = image
        self.offset = hotspot
        self.image.set_alpha(200)
        self.make_shadow()
        if self.direction == 1:
            self.do_flip = True


    def setHotspot(self, pos):
        """
        Set a new hotspot for the cursor
        """
        self.hide()
        self.offset = pos


    def draw(self, surface):
        if self.enabled:
            if self.do_flip:
                self.image = flip(self.image, True, False)
                if not self.shadow == None:
                    self.shadow = flip(self.shadow, True, False)
                self.do_flip = False

            pos = [self.old_pos[0] - self.offset[0], self.old_pos[1] - self.offset[1]]

            if not self.shadow == None:
                surface.blit(self.shadow, (pos[0] + 2, pos[1] + 2))
            surface.blit(self.image, pos)


    def setPos(self, pos):
        if self.direction == 0:
            if self.old_pos[0] > pos[0]:
                if self.do_flip == False:
                    self.direction = 1
                    self.do_flip = True

        else:
            if self.old_pos[0] < pos[0]:
                if self.do_flip == False:
                    self.direction = 0
                    self.do_flip = True

        self.old_pos = pos[:]


    def setFlip(self, flip):
        """
        The cursor can optionally flip left or right depending on the
        direction it is moving.  This is a neat-o effect for the hand cursor.
        """
        self.do_flip = bool(flip)


class MouseCursor(Cursor):
    """
    Replaces the normal pygame mouse cursor with any bitmap cursor
    """

    def enable(self):
        """
        Enable the GfxCursor (disables normal pygame cursor)
        """
        if not self.image or self.enabled: return
        pygame.mouse.set_visible(0)
        self.enabled = 1


    def disable(self):
        """
        Disable the GfxCursor (enables normal pygame cursor)
        """
        if self.enabled:
            pygame.mouse.set_visible(1)
            self.enabled = 0


class KeyCursor(Cursor):
    """
    A cursor that can be controlled by keys
    (not complete)
    """

    def enable(self):
        """
        Enable the GfxCursor
        """
        if not self.image or self.enabled: return
        self.enabled = 1


    def disable(self):
        """
        Disable the GfxCursor
        """
        if self.enabled:
            self.enabled = 0

