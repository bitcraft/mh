"""
Copyright 2010, 2011 Leif Theden

This file is part of lib2d.

lib2d is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

lib2d is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with lib2d.  If not, see <http://www.gnu.org/licenses/>.
"""

from pygame import Color
import pygame

from . import res


pygame.font.init()


class TextBanner(object):
    """
    Wrapper around Pygame's Font class

    Loading fonts in pygame can be slow, and to make up for it,
    this class caches fonts returned from pygame and can make
    multiple renders faster.  It also includes some hacks
    to make blitting pretty
    """

    def __init__(self, text, color=[0, 0, 0], size=12, font=None):
        super(TextBanner, self).__init__()

        self._font_size = size
        self._text = text
        self._color = color
        self._rect = pygame.rect.Rect(0, 0, 0, 0)

        if font == None:
            font = res.defaultFont()
            self._font = pygame.font.Font(font, size)
            self._font_name = font

        else:
            if isinstance(font, str):
                fullpath = res.fontPath(font)
                self.set_font(fullpath)
            else:
                self._font = font
                self._font_name = font

        self.dirty = 1

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text
        self.dirty = 1

    text = property(get_text, set_text)

    def get_font(self):
        return self._font

    def set_font(self, font=None):
        if font == None:
            font = default_font
        self._font = pygame.font.Font(font, self.font_size)
        self._font_name = font
        self.dirty = 1

    font = property(get_font, set_font)

    def get_font_size(self):
        return self._font_size

    def set_font_size(self, size):
        self._font_size = size
        self.dirty = 1

    font_size = property(get_font_size, set_font_size)

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = Color(*color)
        self.dirty = 1

    color = property(get_color, set_color)

    @property
    def image(self):
        if self.dirty:
            self.render()
        return self._image

    @property
    def rect(self):
        if self.dirty:
            self.render()
        return self._rect

    def render(self, bkg=None, alpha=False):
        try:
            if alpha == True:
                self._image = self.font.render(self.text, True, self._color).convert_alpha()
            elif bkg == None:
                self._image = self.font.render(self.text, False, self._color).convert()
            else:
                self._image = self.font.render(self.text, True, self._color, bkg).convert()
                self._image.set_colorkey(bkg)
            self._rect.size = self._image.get_rect().size
            return self._image
        except AttributeError:
            print("font not set correctly")
            raise

        self.dirty = 0


class OutlineTextBanner(TextBanner):
    colorkey = (90, 0, 0)
    border = 3
    border_color = (0, 0, 0)

    def render(self, bkg=None, alpha=False):
        try:
            # render the font once to determine the size needed for our scratch surface
            image = self.font.render(self.text, True, self._color)

            # this is our scratch surface
            s = pygame.Surface(image.get_size())

            # we need to fanagle the image a bit to make sure colorkey surfaces work
            if not alpha:
                s.fill(self.colorkey)
                s.set_colorkey(self.colorkey)

            # choose the font for the banner.  it must be smaller than the original size
            if self._font_name == None:
                inner_font = pygame.font.Font(default_font, self.font_size - 4)
            else:
                inner_font = pygame.font.Font(self._font_name, self.font_size - 4)

            # render the text for the border 

            text = inner_font.render(self.text, False, self.border_color)

            # build a border for the text by blitting it in a circle
            for x in range(self.border + 2):
                for y in range(self.border + 2):
                    s.blit(text, (x, y))

            # render the innner portion of the banner
            text = inner_font.render(self.text, False, self._color)

            # blit the text over the border
            s.blit(text, (2, 2))

            self._image = s.convert()
            self._rect.size = self._image.get_rect().size

            return self._image
        except AttributeError:
            print("1")
            raise


class RetroOutlineTextBanner(OutlineTextBanner):
    """
    Outlined text banner, but stretches out the image to give it
    a look not unlike 80's era fonts that have rectangluar pixels
    """

    def render(self, bkg=None, alpha=True):
        super(RetroOutlineTextBanner, self).render(bkg, alpha)

        w, h = self.image.get_size()
        self._image = pygame.transform.scale(self._image, (int(w / 2), h))
        self._image = pygame.transform.scale(self._image, (w, h)).convert()

