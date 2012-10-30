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

import res
import pygame


pygame.font.init()


"""
simple functions wrap pygame's font module
"""


def loadFont(font, size):
    if font is None:
        return pygame.font.Font(res.defaultFont(), size)
            
    elif isinstance(font, str):
        return pygame.font.Font(res.fontPath(font), size)

    elif isinstance(font, pygame.font.Font):
        return font

    else:
        return font


def TextBanner(text, font_name=None, size=12, color=[0,0,0], alpha=False, background=None):
        font = loadFont(font_name, size)

        if alpha == True:
            return font.render(text, True, color).convert_alpha()
        elif background is None:
            return font.render(text, False, color).convert()
        else:
            image = font.render(text, True, color, bkg).convert()
            image.set_colorkey(bkg)
            return image


def outlinedText(text, font_name, font_size, color=[0,0,0], alpha=False, background=None):
    colorkey = (90,0,0)
    border = 3
    border_color = (0,0,0)

    font = loadFont(font_name, font_size-1)

    # render the font once to determine the size needed for our scratch surface
    size = font.render(text, True, color).get_size()

    # this is our scratch surface
    if alpha:
        s = pygame.Surface(size, pygame.SRCALPHA)

    else:
        s = pygame.Surface(size)
        s.fill(colorkey)
        s.set_colorkey(colorkey)

    # choose the font for the banner.  it must be smaller than the original size
    inner_font = loadFont(font_name, font_size - 4)

    # render the text for the border 
    border_image = inner_font.render(text, False, border_color)

    # build a border for the text by blitting it in a circle
    for x in xrange(border + 2):
        for y in xrange(border + 2):
            s.blit(border_image, (x, y))

    # render the innner portion of the banner
    text = inner_font.render(text, False, color)

    # blit the text over the border
    s.blit(text, (2,2))

    return s



def stretch2x(image):
    w, h = image.get_size()
    new_image = pygame.transform.scale(image, (int(w/2), h))
    return pygame.transform.scale(new_image, (w, h)).convert(image)


def retroOutlinedText(*arg, **kwarg):
    return stretch2x(outlinedText(*arg, **kwarg))

