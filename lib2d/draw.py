"""
Copyright 2009, 2010, 2011 Leif Theden

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

from itertools import product

from pygame import Rect
import pygame


class GraphicBox(object):
    """
    Generic class for drawing graphical boxes

    load it, then draw it wherever needed
    """

    def __init__(self, image):
        surface = image.load()
        iw, self.th = surface.get_size()
        self.tw = iw / 9
        names = "nw ne sw se n e s w c".split()
        tiles = [surface.subsurface((i * self.tw, 0, self.tw, self.th))
                 for i in range(len(names))]

        self.tiles = dict(zip(names, tiles))
        self.tiles['c'] = self.tiles['c'].convert_alpha()

    def draw(self, surface, rect, fill=False):
        ox, oy, w, h = Rect(rect)

        if fill:
            if fill == True:
                pass
            elif isinstance(fill, int):
                print("1")
                self.tiles['c'].set_alpha(fill)

            wmod = 0
            hmod = 0

            if float(w) % self.tw > 0:
                wmod = self.tw

            if float(h) / self.th > 0:
                hmod = self.th

            p = product(range(ox + 4, ox + w - wmod, self.tw),
                        range(oy + 4, oy + h - hmod, self.th))

            [surface.blit(self.tiles['c'], (x, y)) for x, y in p]

            # we were unable to fill it completly due to size restrictions
            if wmod:
                for y in range(oy + 4, oy + h - hmod, self.th):
                    surface.blit(self.tiles['c'], (ox + w - self.tw - 4, y))

            if hmod:
                for x in range(ox + 4, ox + w - wmod, self.tw):
                    surface.blit(self.tiles['c'], (x, oy + h - self.th - 4))

            if hmod or wmod:
                surface.blit(self.tiles['c'], (ox + w - self.tw - 4, oy + h - self.th - 4))

        for x in range(self.tw + ox, w - self.tw + ox, self.tw):
            surface.blit(self.tiles['n'], (x, oy))
            surface.blit(self.tiles['s'], (x, h - self.th + oy))

        for y in range(self.th + oy, h - self.th + oy, self.th):
            surface.blit(self.tiles['w'], (w - self.tw + ox, y))
            surface.blit(self.tiles['e'], (ox, y))

        surface.blit(self.tiles['nw'], (ox, oy))
        surface.blit(self.tiles['ne'], (w - self.tw + ox, oy))
        surface.blit(self.tiles['se'], (ox, h - self.th + oy))
        surface.blit(self.tiles['sw'], (w - self.tw + ox, h - self.th + oy))


# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
# passing None as the surface is ok
def drawText(surface, text, color, rect, font=None, aa=False, bkg=None):
    rect = Rect(rect)
    y = rect.top
    lineSpacing = -2
    maxWidth = 0
    maxHeight = 0

    if font is None:
        fullpath = pygame.font.get_default_font()
        font = pygame.font.Font(fullpath, 12)

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    # for very small fonts, turn off antialiasing
    if fontHeight < 16:
        aa = 0
        bkg = None

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            if text[i] == "\n":
                text = text[:i] + text[i + 1:]
                break
            i += 1
        else:
            # if we've wrapped the text, then adjust the wrap to the last word
            if i < len(text):
                i = text.rfind(" ", 0, i) + 1

        if surface:
            # render the line and blit it to the surface
            if bkg:
                image = font.render(text[:i], 1, color, bkg)
                image.set_colorkey(bkg)
            else:
                image = font.render(text[:i], aa, color)

            surface.blit(image, (rect.left, y))

        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text


def renderOutlineText(text, color, border, fontFilename, size,
                      colorkey=(128, 128, 0)):
    font = pygame.font.Font(fontFilename, size + 4)
    image = pygame.Surface(font.size(text), pygame.SRCALPHA)
    inner = pygame.font.Font(fontFilename, size - 4)
    outline = inner.render(text, 2, border)
    w, h = image.get_size()
    ww, hh = outline.get_size()
    cx = w / 2 - ww / 2
    cy = h / 2 - hh / 2
    for x in range(-3, 3):
        for y in range(-3, 3):
            image.blit(outline, (x + cx, y + cy))
    image.blit(inner.render(text, 1, color), (cx, cy))
    return image


class ScrollingTextPanel(object):
    """
    Area that can display text and maintains a buffer
    """

    def __init__(self, rect, maxlen):
        self.rect = rect
        self.maxlen = maxlen
        self.background = (0, 0, 0)

    def add(self, text):
        if len(self.text) == maxlen:
            self.text.popleft()

        self.text.append(text)

    def draw(self, surface):
        for line in self.text:
            banner = TextBanner(line, size=self.text_size)
            surface.blit(banner.render(self.background), (x, y))
            y += banner.font.size(line)[1]


