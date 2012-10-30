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
import res, animation
from pygame.transform import flip
import itertools
from pymunk import Vec2d


class RenderGroup(object):
    """
    optional class from managing groups of avatars
    """

    pass


class Avatar(GameObject):
    """
    Avatar is a sprite-like class that supports multiple animations, animation
    controls, directions, is pickleable, and has lazy image loading. 
    update must be called occasionally for animations and rotations to work.
    """

    def __init__(self, animations, axis_offset=(0,0)):
        GameObject.__init__(self)
        self.axis_offset = Vec2d(axis_offset)

        self.curImage     = None    # cached for drawing ops
        self.curFrame     = None    # current frame number
        self.curAnimation = None
        self.animations   = {}
        self.looped     = 0
        self.timer      = 0.0
        self.ttl = 0
        self.flip = 0
        self.speed_mod = 1.0
        self._prevAngle = None
        self._changed = True
        self.axis = Vec2d(0,0)

        for animation in animations:
            self.add(animation)
            self.animations[animation.name] = animation

        self.play(self.animations.keys()[0])


    def _updateCache(self):
        angle = 0
        self.curImage = self.curAnimation.getImage(self.curFrame, angle) 
        self.axis = Vec2d(0, self.curImage.get_size()[1])
        self.axis += self.axis_offset
        if self.flip: self.curImage = flip(self.curImage, 1, 0)


    @property
    def image(self):
        if self._changed:
            self._updateCache()
            return self.curImage


    def unload(self):
        self.curImage = None


    def update(self, time):
        """
        call this as often as possible with a time.  the units in the
        animation files must match the units provided here.  ie: milliseconds.
        """

        if self.ttl < 0:
            return

        self.timer += time

        while (self.timer >= self.ttl):
            self.timer -= self.ttl

            try:
                self.ttl, self.curFrame = next(self.iterator)
                self.ttl *= self.speed_mod
            except StopIteration:
                if self.callback:
                    self.callback[0](*self.callback[1], **self.callback[2])

            else:
                self.changed = True

                # needed to handle looping
                if self.ttl < 0:
                    return

        else:
            self.changed = False

 
    def isPlaying(self, name):
        if isinstance(name, animation.Animation):
            if name == self.curAnimation: return True
        else:
            if self.getAnimation(name) == self.curAnimation: return True
        return False


    def play(self, name=None, loop=-1, loop_frame=None, callback=None):
        if isinstance(name, (animation.Animation, animation.StaticAnimation)):
            if name == self.curAnimation: return
            self.curAnimation = name
        elif name is None:
            self.play(self.animations.keys()[0])
        else:
            temp = self.getAnimation(name)
            if temp == self.curAnimation: return
            self.curAnimation = temp

        self.callback = (callback, [], {})
        self.looped = 0
        self.timer  = 0

        if loop >= 0:
            self.iterator = itertools.chain.from_iterable(
                                itertools.repeat(
                                   tuple(iter(self.curAnimation)), loop + 1))
            
        else:
            if loop_frame:
                self.iterator = itertools.chain(
                                    iter(self.curAnimation),
                                    itertools.cycle(((-1, loop_frame),))
                                )

            else:
                self.iterator = itertools.cycle(iter(self.curAnimation))

        self.ttl, self.curFrame = next(self.iterator)
        self.ttl *= self.speed_mod
        self._changed = True


    def getAnimation(self, name):
        """
        return the animation for this name.
        """

        try:
            return self.animations[name]
        except:
            raise


    def __str__(self):
        return "<Avatar %s>" % id(self)

