from objects import GameObject
import res

import pygame


"""
TODO: make some sort of manager class for animations
      would make resource sharing less expensive
      in many cases, a cache doesn't make sense, but here...it does
"""     

def padimage(image):    
    """
    Do a little processing to the input image to make it prettier when rotated.
    Pad the image with transparent pixels so the edges get antialised when
    rotated and scaled.
    """

    # replacement surface that is slightly bigger then the original
    new = Surface(image.get_rect().inflate(2, 2).size, pygame.SRCALPHA)
    color = image.get_at((0,0))

    # set the color's alpha channel to be clear
    color[3] = 0
    new.fill(color)
    new.blit(image, (1,1))

    return new


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

    def __init__(self, filename, size, name=None, directions=1):
        GameObject.__init__(self)

        self.filename = filename
        self.size = size

        if name == None:
            self.name = filename

        self.directions = directions  # number of directions for animation
        self.frames = ([],) * directions


    def load(self):
        """
        load the images for use with pygame
        """

        tw, th = self.size
        image = pygame.image.load(self.filename)
        iw, ih = image.get_size()
        self.directions = ih/th
        self.frames = ([],) * self.directions
        for y in range(0, ih/th, th):
            for x in range(0, iw/tw, tw):
                frame = AnimationFrame(image.subsurface((x, y, tw, th)))
                self.add_frame(frame, y)

    def __len__(self):
        return self._len


    def get_frame(self, number, direction=0):
        """
        return the frame by number with the correct image for the direction
        """

        if direction < 0:
            direction = pi + (pi - abs(direction))

        d = int(ceil(direction / pi2 * (self.directions - 1)))

        return self.frames[d][number]


    def add_frame(self, frame, direction=0):
        frames[direction].append(frame)
        self._len = len(self.frames[0])


    def __repr__(self):
        return "<Animation %s: \"%s\">" % (id(self), self.name)
