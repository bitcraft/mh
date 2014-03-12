"""
Copyright 2010, 2011  Leif Theden


This file is part of lib2d.

lib2d is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

lib2d is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with lib2d.  If not, see <http://www.gnu.org/licenses/>.
"""

from collections import namedtuple

from pygame.locals import *

from lib2d.ui import Element
from lib2d import banner


def OutlinedFactory(text, font, size, color):
    return banner.outlinedText(text, font, size, color, True, None)


MenuOption = namedtuple('MenuOption', 'label callback image')


def positionRects(rects, alignment, spacing=(0, 0), origin=(0, 0)):
    """
    returns a list of tuples that are the top-left corner of a surface
    this list is used to correctly position images for the menu

    NOTE: all rects MUST have an topleft value of (0,0)
    """

    width, height = rects[0].unionall(rects[1:]).size

    column = 0
    row = 0

    points = []

    for rect in rects:
        if alignment['vertical'] == 'top':
            dy = 0

        elif alignment['vertical'] == 'center':
            dy = (height - rect.height) / 2

        elif alignment['vertical'] == 'bottom':
            dy = height - rect.height

        if alignment['horizontal'] == 'left':
            dx = 0

        elif alignment['horizontal'] == 'center':
            dx = (width - rect.width) / 2

        elif alignment['horizontal'] == 'right':
            dx = width - rect.width

        cx = (width + spacing[0]) * column + origin[0]
        cy = (height + spacing[1]) * row + origin[1]
        points.append((cx + dx, cy + dy))
        row += 1

    return points


class Menu(Element):
    """
    simple menu that is controlled by keys
    
    """

    def __init__(self, h_pad, v_pad, orientation, number, option_list,
                 font=None, font_size=32, item_factory=OutlinedFactory, callback=None):

        self.font = font
        self.font_size = font_size
        self.change_number = number  # new row/col #
        self.orientation = orientation
        self.horizontal_padding = h_pad
        self.vertical_padding = v_pad

        self.selection = 0  # The currently selected button
        self.u_color = (230, 230, 230)  # Color for unselected text
        self.s_color = (255, 50, 10)  # Color for selected text

        self.update_buttons = False  # True if the positions of the
        # buttons need to be updated

        # the callback will call a function with the current selection as the
        # first argument.  useful if you want to track state of the menu in a
        # sane way.  you could constantly poll, selection, but this is better.
        self.callback = callback

        self.item_factory = item_factory

        # This dictionary contains the alignment orientation of the buttons
        # related to each other.  It shifts the button within the bounds of
        # 'max_width' and 'max_height' in the self.position_items() method.
        self.alignment = {'vertical': 'top', 'horizontal': 'left'}
        self.spacing = (0, 0)

        self.options = []
        for i, (label, callback) in enumerate(option_list):
            if i == self.selection:
                color = self.s_color
            else:
                color = self.u_color
            option = MenuOption(label,
                                callback,
                                item_factory(label, font, font_size, color))
            self.options.append(option)

        self.points = []

        self.update_buttons = True


    def draw(self, surface):
        if self.update_buttons:
            rects = [o.image.get_rect() for o in self.options]
            self.points = positionRects(rects, self.alignment, self.spacing, self.rect.topleft)
            self.update_buttons = False

        return [surface.blit(o.image, self.points[i]) for i, o in enumerate(self.options)]


    def handle_event(self, event):
        if event.type != KEYDOWN: return
        key = event.key

        o = self.orientation
        s = self.selection
        n = self.change_number

        d = 0

        if key == K_DOWN:
            if (o == 'vertical') and ((s + 1) % n != 0):
                d = 1
            elif o == 'horizontal':
                d = n
        elif key == K_UP:
            if (o == 'vertical') and ((s) % n != 0):
                d = -1
            elif o == 'horizontal':
                d = -n
        elif key == K_RIGHT:
            if o == 'vertical':
                d = n
            elif (o == 'horizontal') and ((s + 1) % n != 0):
                d = 1
        elif key == K_LEFT:
            if o == 'vertical':
                d = -n
            elif (o == 'horizontal') and ((s) % n != 0):
                d = -1
        elif key == K_RETURN:
            return [None], self.options[self.selection].callback()

        s += d

        if s >= len(self.options):
            s = len(self.options) - 1

        elif s < 0:
            s = 0

        if s != self.selection:
            label, callback, image = self.options[self.selection]
            image = self.item_factory(label, self.font, self.font_size, self.u_color)
            new_option = MenuOption(label, callback, image)
            self.options[self.selection] = new_option

            label, callback, image = self.options[s]
            image = self.item_factory(label, self.font, self.font_size, self.s_color)
            new_option = MenuOption(label, callback, image)
            self.options[s] = new_option

            if self.callback is not None:
                self.callback(s)

            self.selection = s

        return None

