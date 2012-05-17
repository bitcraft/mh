"""
Copyright 2010-2012  Leif Theden


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

from lib2d.common import res
from lib2d.client.banner import OutlineTextBanner, TextBanner

import pygame
from pygame.locals import *



class OutlineMenuItem(OutlineTextBanner):
    def __init__(self, t, cb, c, s, f):
        self.callback = cb
        self.disabled = False
        super(OutlineMenuItem, self).__init__(text=t, color=c, size=s, font=f)


class MenuItem(TextBanner):
    def __init__(self, t, cb, c, s, f):
        self.callback = cb
        self.disabled = False
        super(MenuItem, self).__init__(text=t, color=c, size=s, font=f)


class cMenu():

    move_sound = res.loadSound("bump0.wav")
    select_sound = res.loadSound("select1.wav")

    def __init__(self, rect, h_pad, v_pad, orientation, number, button_list,
        font=None, font_size=32, banner_style="outline", callback=None):

        ## menu items
        self.menu_items = []                      # List of menu items
        self.font = font                          # Font to use
        self.font_size = font_size

        self.rect = pygame.Rect(rect)             # Top left corner (of surface)
        self.change_number = number               # new row/col #
        self.orientation = orientation
        self.horizontal_padding = h_pad
        self.vertical_padding = v_pad

        self.selection = 0                        # The currently selected button
        self.u_color = (230,230,230)              # Color for unselected text
        self.s_color = (255,50,10)                # Color for selected text

        self.centered = False                     # True if the menu is centered
        self.update_buttons = False               # True if the positions of the
                                                  # buttons need to be updated

        # the callback will call a function with the current selection as the
        # first argument.  useful if you want to track state of the menu in a
        # sane way.  you could constantly poll, selection, but this is better.
        self.callback = callback

        self.banner_style = banner_style          # type of font to use
        self.dirty = True

        # This dictionary contains the alignment orientation of the buttons
        # related to each other.  It shifts the button within the bounds of
        # 'max_width' and 'max_height' in the self.position_items() method.
        self.alignment = {'vertical'  :'top',
                                'horizontal':'left'}


        [ self.add_button(self.create_button(*i[:2])) for i in button_list ]
        self.update_buttons = True

    def disable(self, i):
        """
        disable a specific option

        the option will be shown, but cannot be selected
        """

        self.menu_items[i].disabled = True
        self.update_buttons = True


    def enable(self, i):
        """
        enable a specific option
        """

        self.menu_items[i].disabled = False
        self.update_buttons = True

    def add_button(self, button):
        self.menu_items.append(button)

    def draw(self, surface):
        if self.update_buttons:
            self.position_items()
            self.render()
            self.update_buttons = False

        [ surface.blit(b.image, b.rect) for b in self.menu_items ]

    @property
    def drawables(self):
        return self.menu_items

    def render(self):
        # grey-out disabled menu items
        for b in self.menu_items:
            if b.disabled:
                b.color = (80,80,80)
            else:
                b.render()        
        self.dirty = True

    def set_padding(self, h_pad, v_pad):
        self.horizontal_padding = h_pad
        self.vertical_padding   = v_pad
        self.update_buttons = True

    def set_orientation(self, new_orientation):
        if new_orientation == 'vertical' or new_orientation == 'horizontal':
                self.orientation = new_orientation
                self.update_buttons = True
        else:
                print 'WARNING:  cMenu.set_orientation:  Invalid argument '\
                    'new_orientation (value: %d)' % new_orientation

    def set_font(self, font):
        self.font = font
        [ item.set_font(font) for item in self.menu_items ]

    def set_alignment(self, v_align, h_align):
        if v_align in ['top', 'center', 'bottom']:
                self.alignment['vertical'] = v_align
        if h_align in ['left', 'center', 'right']:
                self.alignment['horizontal'] = h_align
        self.update_buttons = True

    def remove_buttons(self, indexList):
        for index in indexList:
                if len(self.menu_items) > 1:
                    self.menu_items.pop(index)
        self.update_buttons = True

    def create_button(self, text, callback, color=None):
        if color == None:
            color = self.u_color

        if self.banner_style == "outline":
            new_button = OutlineMenuItem(text, callback, color, self.font_size, self.font)
        else:
            new_button = MenuItem(text, callback, color, self.font_size, self.font)

        return new_button

    def position_items(self):
        width = 0
        height = 0
        max_width = 0
        max_height = 0
        counter = 0

        x_loc = self.rect.left
        y_loc = self.rect.top

        # Get the maximum width and height of the surfaces
        for item in self.menu_items:
            max_width  = max(item.rect.width, max_width)
            max_height = max(item.rect.height, max_height)

        # Position the button in relation to each other
        for item in self.menu_items:
            # Vertical Alignment
            if self.alignment['vertical'] == 'top':
                offset_height = 0
            elif self.alignment['vertical'] == 'center':
                offset_height = (max_height - item.rect.height)/2
            elif self.alignment['vertical'] == 'bottom':
                offset_height = (max_height - item.rect.height)

            # Horizontal Alignment
            if self.alignment['horizontal'] == 'left':
                offset_width = 0
            elif self.alignment['horizontal'] == 'center':
                offset_width = (max_width - item.rect.width)/2
            elif self.alignment['horizontal'] == 'right':
                offset_width = (max_width - item.rect.width)

            # Move the button location slightly based on the alignment offsets
            x_loc += offset_width
            y_loc += offset_height

            # Assign the location of the button
            item.rect.topleft = (x_loc, y_loc)

            # Take the alignment offsets away after the button position has been
            # assigned so that the new button can start fresh again
            x_loc -= offset_width
            y_loc -= offset_height

            # Add the width/height to the position based on the orientation of the
            # menu.  Add in the padding.
            if self.orientation == 'vertical':
                y_loc += max_height + self.vertical_padding
            else:
                x_loc += max_width + self.horizontal_padding


    def handle_event(self, event):
        if event.type != KEYDOWN: return
        key = event.key

        o = self.orientation
        s = self.selection
        n = self.change_number

        d = 0

        if key == K_DOWN:
            self.move_sound.stop()
            self.move_sound.play()
            if (o == 'vertical') and ((s + 1) % n != 0):
                d = 1
            elif o == 'horizontal':
                d = n
        elif key == K_UP:
            self.move_sound.stop()
            self.move_sound.play()
            if (o == 'vertical') and ((s) % n != 0):
                d = -1
            elif o == 'horizontal':
                d = -n
        elif key == K_RIGHT:
            self.move_sound.stop()
            self.move_sound.play()
            if o == 'vertical':
                d = n
            elif (o == 'horizontal') and ((s + 1) % n != 0):
                d = 1
        elif key == K_LEFT:
            self.move_sound.stop()
            self.move_sound.play()
            if o == 'vertical':
                d = -n
            elif (o == 'horizontal') and ((s) % n != 0):
                d = -1
        elif key == K_RETURN:
            #self.select_sound.play()
            return [None], self.menu_items[self.selection].callback()

        self.check_disabled(d)

        if self.selection >= len(self.menu_items):
            self.selection = len(self.menu_items) -1

        elif self.selection < 0:
            self.selection = 0

        if s != self.selection:
            self.menu_items[self.selection].color = self.s_color
            self.menu_items[s].color = self.u_color
            if not self.callback == None:
                self.callback(self.selection)

        return None

    def check_disabled(self, d=0):
        try:
            if self.menu_items[self.selection + d].disabled:
                if self.selection + d == 0:
                    self.selection = 0
                    self.check_disabled(1)

                elif self.selection + d == len(self.menu_items) - 1:
                    self.selection = len(self.menu_items) - 1
                    self.check_disabled(-1)

                else:
                    if d < 0:
                        d -= 1
                    else:
                        d += 1

                    self.check_disabled(d)
            else:
                self.selection += d
        except:
            return

    def ready(self, start=0):
        self.selection = start
        self.check_disabled()
        self.menu_items[self.selection].color = self.s_color
