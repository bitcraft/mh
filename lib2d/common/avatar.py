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


from objects import GameObject
import res

import pygame
import sys
from math import pi, radians, ceil
from itertools import product
from random import randint

from pygame.transform import flip

import time

pi2 = pi * 2



class Avatar(GameObject):
    """
    Avatar is a sprite-like class that supports multiple animations, animation
    controls, directions, and is pickleable.
    update must be called occasionally for animations and rotations to work.
    """

    def __init__(self):
        GameObject.__init__(self)
        self.default      = None
        self.callback     = None    # called when animation finishes
        self.curImage     = None    # cached for drawing ops
        self.curFrame     = None    # current frame number
        self.curAnimation = None
        self.animations   = {}
        self.axis = (0,0)
        self.loop_frame = 0
        self.looped     = 0
        self.loop       = -1
        self.timer      = 0.0
        self.flip       = 0
        self._prevAngle = None
        self._prevFrame = None
        self._is_paused = False
        self._rect = None

    def _updateCache(self):
        angle = self.getOrientation()

        if self.curAnimation == None:
            self.play(self.default)

        if not angle == self._prevAngle:
            self.curImage = self.curAnimation.getImage(self.curFrame, angle)
            self._rect = self.curImage.get_rect().move(self.axis)
            if self.flip: self.curImage = flip(self.curImage, 1, 0)

        elif not self.curFrame == self._prevFrame:
            self.curImage = self.curAnimation.getImage(self.curFrame, angle) 
            self._rect = self.curImage.get_rect().move(self.axis)
            if self.flip: self.curImage = flip(self.curImage, 1, 0)

        elif self.curImage == None:
            self.curImage = self.curAnimation.getImage(self.curFrame, angle) 
            self._rect = self.curImage.get_rect().move(self.axis)
            if self.flip: self.curImage = flip(self.curImage, 1, 0)


    def get_rect(self):
        self._updateCache()
        return self._rect


    def get_size(self):
        self._updateCache()
        return self._rect.get_size()


    @property
    def rect(self):
        self._updateCache()
        return self._rect


    @property
    def image(self):
        self._updateCache()
        return self.curImage


    @property    
    def visible(self):
        return self._is_visible


    @visible.setter
    def visible(self, value):
        self._is_visible = bool(value)


    @property
    def state(self):
        return (self.curAnimation, self.curFrame)


    @property
    def paused(self):
        return self._is_paused


    @paused.setter
    def paused(self, value):
        self._is_paused = bool(value)


    def unload(self):
        self.curImage = None


    def update(self, time):
        """
        call this as often as possible with a time.  the units in the
        animation files must match the units provided here.  ie: milliseconds.
        """

        if not self.curAnimation:
            self.reset()
        if self._is_paused: return

        self.timer += time

        ttl = self.curAnimation.getTTL(self.curFrame)
        while (self.timer >= ttl):
            if ttl < 0:
                self.paused = 1
                return

            self.timer -= ttl
            self.advanceFrame()

            # the animation may have been lost after the advance
            if self.curAnimation:
                ttl = self.curAnimation.getTTL(self.curFrame)
            else:
                break


    def advanceFrame(self):
        """
        advance the the frame in the current animation by one.

        animation will stop or loop here if needed.
        """

        if self._is_paused: return
        if not self.curAnimation: return

        self.curFrame += 1

        if self.curFrame >= self.curAnimation.frames:
            # the animation has reached the end
            if self.loop == 0:
                self.stop()

            # loop, but count the loops
            elif self.loop > 0:
                if self.looped >= self.loop:
                    self.stop()
                else:
                    self.setFrame(self.loop_frame)
                    self.looped += 1

            # loop forever, don't count the loops
            else:
                self.setFrame(self.loop_frame)
        else:
            # just set the next frame
            self.setFrame(self.curFrame)


    def stop(self):
        """
        pauses the current animation and runs the callback if needed.
        """

        self.reset()
        self.doCallback()


    def doCallback(self):
        if self.callback:
            self.callback[0](*self.callback[1])


    def reset(self):
        """
        sets defaults of the avatar.
        """

        if len(self.animations) == 0:
            return 
        self.play(self.default)


    def setFrame(self, frame):
        """
        set the frame of the animation
        frame should be 0-indexed number of frame to show
        """
        self._prevFrame = frame
        self.curFrame = frame
        


    def isPlaying(self, name):
        if isinstance(name, Animation):
            if name == self.curAnimation: return True
        else:
            if self.getAnimation(name) == self.curAnimation: return True
        return False


    def play(self, name=None, start_frame=0, loop=-1, loop_frame=0, \
             callback=None, arg=[]):

        if isinstance(name, Animation):
            if name == self.curAnimation: return
            self.curAnimation = name
        else:
            temp = self.getAnimation(name)
            if temp == self.curAnimation: return
            self.curAnimation = temp

        self.loop = loop
        self.loop_frame = loop_frame
        self.paused = False
        self.timer  = 0
        self.looped = 0

        if callback:
            self.callback = (callback, arg)

        self.setFrame(start_frame)


    def add(self, other):
        if isinstance(other, Animation) or isinstance(other, StaticAnimation):
            self.animations[other.name] = other
            if self.default == None:
                self.setDefault(other)
        GameObject.add(self, other)


    def remove(self, other):
        playing = False
        if isinstance(other, Animation) or isinstance(other, StaticAnimation):
            if self.isPlaying(other):
                playing = True
            del self.animations[other.name]
        
        GameObject.remove(self, other)

        # handle when there are no animations left
        if len(self.animations) == 0:
            self.callback = None
            self.curAnimation = None
            self.curImage = None
            self.curFrame = None
            self.default = None
            self._is_paused = True
        elif playing:
            self.setDefault(self.animations.keys()[0])
            self.reset()


    def getAnimation(self, name):
        """
        return the animation for this name.
        """

        try:
            return self.animations[name]
        except:
            raise


    def setDefault(self, name):
        """
        set the defualt animation to play if the avatar has nothing else to do
        """

        if isinstance(name, Animation) or isinstance(name, StaticAnimation):
            self.default = name
        else:
            try:
                self.default = self.getAnimation(name)
            except KeyError:
                return


    def __str__(self):
        return "<Avatar %s>" % id(self)


# TODO: make this more like a list object.  slices, etc.
class Animation(GameObject):
    """
    Animation is a collection of frames with a few control variables.
    Animations can store multiple directions and are picklable.

    each set of animation added will count as a seperate direction.
    1 animation  = no rotations
    2 animations = left and right (or up and down)
    4 animations = left, right, up, down
    6 animations = up, down, nw, ne, sw, se (for hex maps)
    and so on.

    The animation loader expects the image to be in a specific format.

    TODO: implement some sort of timing, rather than relying on frames
    """

    def __init__(self, filename, name, frames, directions=1, timing=None,
                 order=None):

        GameObject.__init__(self)

        self.filename = filename
        self.name = name
        self.order = None

        if isinstance(frames, int):
            self.frames = frames
            self.real_frames = frames

        elif isinstance(frames, list):
            self.frames = len(frames)
            self.real_frames = max(frames) + 1
            self.order = frames

        self.directions = directions
        self.timing = timing
        self.images = []


    def returnNew(self):
        return self


    def load(self, force=False):
        """
        load the images for use with pygame
        """

        if not self.images == [] and not force:
            return

        image = res.loadImage(self.filename, 0, 0, 1)

        iw, ih = image.get_size()
        tw = iw / self.real_frames
        th = ih / self.directions
        self.images = [None] * (self.directions * self.real_frames)
      
        d = 0
        for y in range(0, ih, th):
            #if d == ih/th: d = 0
            for x in range(0, iw, tw):
                try:
                    frame = image.subsurface((x, y, tw, th))
                except ValueError as e:
                    raise ValueError, self.filename
                self.images[(x/tw)+d*self.real_frames] = frame
            d += 1

        if isinstance(self.timing, int):
            self.timing = [self.timing] * self.frames

        elif self.timing == None:
            self.timing = [200] * self.frames


    def unload(self):
        self.images = []


    def getTTL(self, number):
        if self.images == []:
            raise Exception, "Avatar hasn't loaded images yet"

        return self.timing[number]


    def getImage(self, number, direction=0):
        """
        return the frame by number with the correct image for the direction
        direction should be expressed in radians
        """

        if self.images == []:
            raise Exception, "Avatar hasn't loaded images yet"

        if direction < 0:
            direction = pi + (pi - abs(direction))
        d = int(ceil(direction / pi2 * (self.directions - 1)))

        if self.order:
            number = self.order[number]

        # this is a work around for a bug
        if number >= self.frames:
            number = 0

        try:
            return self.images[number+d*self.real_frames]
        except IndexError:
            msg="{} cannot find image for animation ({}/{})"
            raise IndexError, msg.format(self, number+d*self.real_frames, len(self.images))


    def __repr__(self):
        return "<Animation %s: \"%s\">" % (id(self), self.filename)


class StaticAnimation(Animation):
    """
    Animation that only supports one frame
    """

    def __init__(self, filename, name, tile=None, size=None):
        GameObject.__init__(self)

        self.filename = filename
        self.name = name
        self.tile = tile
        self.size = size

        self.image = None

    def returnNew(self):
        return self


    def unload(self):
        self.image = None


    def load(self):
        """
        load the images for use with pygame
        TODO: this is super hackish.
        """

        image = res.loadImage(self.filename, 0, 0, 1)
      
        if self.tile:
            x, y = self.tile
            x *= self.size[0]
            y *= self.size[1]
            ck = image.get_colorkey()
            self.image = pygame.Surface(self.size)
            self.image.blit(image,(0,0),area=(x,y, self.size[0], self.size[1]))
            image.set_colorkey(ck, pygame.RELACCEL) 

        else:
            self.image = image

        self.frames = [self.image]


    def getTTL(self, number):
        return -1


    def getImage(self, number, direction=0):
        """
        return the frame by number with the correct image for the direction
        direction should be expressed in radians
        """

        return self.image

    def __repr__(self):
        return "<Animation %s: \"%s\">" % (id(self), self.filename)

