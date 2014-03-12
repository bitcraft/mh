"""


"""

from math import cos, sin, radians, degrees

from pygame.surface import Surface
from pygame.rect import Rect
from pygame import draw, Color

from rpg import LivingObject


raw_colors = [(125,32,40), (32,64,128), (20,20,200), (200,200,40), \
              (134,54,231), (234,43,90), (80,1,84)]

colors = []
[ colors.append(Color(i[0], i[1], i[2])) for i in raw_colors ]


"""
this is a super basic set of functions for animation skeletons
not ready yet...
"""

def padimage(self, image): 
    """
    Do a little processing of the input image to make it purdyer.
    Pad the image with transparent pixels so the edges get antialised
    when rotated and scaled.  Looks real nice.
    """

    new = Surface(image.get_rect().inflate(2, 2).size, pygame.SRCALPHA)
    color = image.get_at((0,0))
    color[3] = 0
    new.fill(color)
    new.blit(image, (1,1))
    return new


class Body(object):
    """
    a rigid body sprite
    """

    def __init__(self, rect, image):
        self.rect = rect
        self.normal_image = image
        self.image = None
        self.angle = 0.0
        self.old_trans = None

    def update_rect(self):
        """
        position the rect to whatever the physics engine says it should be
        updates the image and rect based on rotation of the physics sprite
        """

        if slow_pc:
            angle = round(int(degrees(self.angle) % 360.0 / 360.0 * simple_no) * simple_angle, 2)
        else:
            angle = degrees(self.angle) % 360.0

        if angle != self.old_trans:
            old_trans = angle
            self.image = rotozoom(self.normal_image, angle, 1)
            self.rect = self.image.get_rect()

class Line(object):
    """
    2 points
    """

    def __init__(self, v0, v1):
        self.v0 = v0
        self.v1 = v1


    def joinWith(self, other, angle):
        self.rotate(angle)

    def rotate(self, angle):
        # rotate v1 around v0
        pass        

class Joint(object):
    """
    binds two bodies together
    """

    def __init__(self, body0, body1, position):
        self.body0 = body0
        self.body1 = body1
        self.position = position
        self.angle = 0.0


class Skeleton(object):
    """
    a single connected set of bodies and joints
    """

    def __init__(self):
        self.parts = []

    def join(self, part0, part1, position):
        j = Joint(part0, part1, position)    


def skinColor(mod):
    return colors[mod["skinColor"]]


def hsv(color, hsva):
    """
    return a new Color object with the HSV values adjusted

    pygame also includes an alpha channel (a)

    since i want to make simple gradations of value when
    rendering the physical bodies, we need a simple way
    to adjust the HSV values of a color.  the pygame
    Color objects have some functionality, but are missing
    features like this one that we are producing here.
    """

    new = Color(color.r, color.g, color.b, color.a)
    h, s, v, a = new.hsva
    h += hsva[0]
    s += hsva[1]
    v += hsva[2]
    a += hsva[3]
    new.hsva = (h,s,v,a)

def head(surface, mod, pos):
    # adjust for body size
    radius = ((mod["bodySize"] + 1) * 4) + 10

    color = skinColor(mod)

    draw.circle(surface, (0,0,0), pos, radius)
    draw.circle(surface, color, pos, int(radius * .90))
    return Rect(pos[0] - radius, pos[1] - radius, radius * 2, radius * 2)

def body(surface, mod, pos):

    # adjust for body size
    size = ((mod["bodySize"] + 1) * 6) + 30

    # get the correct skin color
    color0 = skinColor(mod)

    t = mod["bodyType"]

    # wide ellipse
    if t == 0:
        rect = Rect(pos,(size, size + size / 3))
        draw.ellipse(surface, color0, rect)
        return rect

    # wide curved
    elif t == 1:
        radius = size / 2
        x = pos[0] + radius
        y = pos[1] + radius
        draw.circle(surface, color0, (x - radius / 2, y), radius)
        draw.circle(surface, color0, (x + radius / 2, y), radius)
        rect = Rect((pos[0] - radius / 2, pos[1]),(size + radius, radius * 2))
        return rect

    # wide 3-segmented
    elif t == 2:
        segments  = 3
        radius    = size / 3
        dx        = size / segments
        x = pos[0] + radius
        y = pos[1] + radius
        for i in range(0,3):
            draw.circle(surface, color0, (x + dx * i, y), radius)
        rect = Rect((pos[0] - dx, pos[1]), (size + radius, radius * 2))
        return rect

    # tall ellipse
    if t == 3:
        rect = Rect(pos,(size + size / 3, size))
        draw.ellipse(surface, color0, rect)
        return rect

    # tall curved
    elif t == 4:
        radius = size / 2
        x = pos[0] + radius
        y = pos[1] + radius
        draw.circle(surface, color0, (x, y - radius / 2), radius)
        draw.circle(surface, color0, (x, y + radius / 2), radius)
        rect = Rect((pos[0], pos[1] - radius / 2),(radius * 2, size + radius))
        return rect

    # tall 3-segmented
    elif t == 5:
        segments  = 3
        radius    = size / 3
        dy        = size / segments
        x = pos[0] + radius
        y = pos[1] + radius
        for i in range(0,3):
            draw.circle(surface, color0, (x + dx * i, y + dy * i), radius)
        rect = Rect((pos[0], pos[1]- dy), (radius * 2, radius + size))
        return rect

    # block
    else:
        rect = Rect(pos,(size,size))
        draw.rect(surface, color0, rect)
        return rect

def mouth(surface, mod, pos):
    pos = list(pos)

    if mod["mouthPoison"] < 2:
        color0 = (255,0,0)
        color1 = (200,0,0)
    else:
        color0 = (255,0,200)
        color1 = (200,0,200)

    # adjust for body size
    radius = ((mod["bodySize"] + 1) * 2) + 6

    t = mod["mouthType"]
    if t == 0:
        draw.circle(surface, color0, pos, radius)
        draw.circle(surface, color1, pos, radius, 2)
        return Rect(pos[0] - radius, pos[1] - radius, radius * 2, radius * 2)
    else:
        rect = Rect((pos[0] - radius, pos[1] - radius / 2), (radius * 2, radius))
        draw.ellipse(surface, color0, rect)
        draw.ellipse(surface, color0, rect, 2)
        return rect

class MonsterPart(object):
    required = []
    image = Surface((10,10))

    colorkey = (12,13,12)

    def __init__(self, mod):
        self.disabled = False
        self.rect = self.image.get_rect() 
        self.mod = mod

    def check(self, mod=None):
        if mod == None: mod = self.mod
        for r in self.required:
            if r not in mod.keys():
                self.disabled = True

    def update(self, time):
        pass

    def render(self):
        pass

class MonsterEye(MonsterPart):
    required = ["eyeType", "eyeSkill", "skinColor"]

    def render(self):
        self.check()
        if self.disabled: return

        pos = self.rect.center

        t = self.mod["eyeType"]

        color0 = (255,255,255)
        color1 = (0,0,0)

        radius = (self.mod["eyeSkill"] + 2) * 3

        color = skinColor(self.mod)

        # we have to determine how big the eye will be before drawing
        size = (radius * 2, radius * 2)
        rect = Rect((0,0), size)

        image = Surface(size)
        image.fill(self.colorkey)
        image.set_colorkey(self.colorkey)

        # locking the surface makes multiple drawing operations quicker
        image.lock()

        # draw the border of the eye
        if radius < 10:
            steps = 16
        else:
            steps = 8

        for t in range(0,360,steps):
            t = radians(t)
            new_color = Color(color.r, color.g, color.b)
            h, s, v, a = new_color.hsva
            v = int(sin(t) * 50) + 50
            if v < 0: v = 0 - v
            new_color.hsva = (h, s, v, a)
            x = int(rect.centerx + cos(t) * (radius - 4))
            y = int(rect.centery + sin(t) * (radius - 4))
            draw.circle(image, new_color, (x, y), 3)

        # draw the white and pupil
        draw.circle(image, color0, rect.center, radius - 3)
        draw.circle(image, color1, rect.center, (radius - 3) / 3)

        image.unlock()

        rect.center = pos

        self.rect = rect
        self.image = image

def limb(surface, mod, pos):
    w = ((mod["limbLength"] + 3) * 2) + ((mod["limbWidth"] + 1) * 2)
    l = (mod["limbLength"] + 3) * 8

    color = skinColor(mod)

    t = mod["limbType"]

    # single jointed limb
    if t == 0:
        mid = (l/2) + (mod["limbWidth"] * 2)
        draw.line(surface, (0,0,0), pos, (pos[0] + w, pos[1] + mid), 8)
        draw.line(surface, (0,0,0), (pos[0] + w, pos[1] + mid), (pos[0], pos[1] + l), 8)
        draw.line(surface, color, pos, (pos[0] + w, pos[1] + mid), 4)
        draw.line(surface, color, (pos[0] + w, pos[1] + mid), (pos[0], pos[1] + l), 4)
        return Rect(pos, (w,l))

    # straight limb
    else:
        rect = Rect(pos,(w,l))
        draw.rect(surface, color, rect)
        draw.rect(surface, (0,0,0), rect, 3)
        return rect

class Monster(LivingObject):
    """
    this is a monster.
    """

    def __init__(self):
        LivingObject.__init__(self)
        self.mDNA = random_beast()

        # hold the "parts" (kinda like sprites) attached the the monster
        self.parts = []

        self.rect = None
        self.render()

    def render(self):
        """
        generate an image suitable to represnt this monster.
        return Rect(pos[0] - radius, pos[1] - radius, radius * 2, radius * 2)
        
        the image will be used in battle screens
        """

        d = self.mDNA.d
        color = (200,200,200)

        scratch = Surface((150, 150))
        s = Surface((150,150))
        s.lock()

        body_rect = body(s, d, (40,40))

        #draw.rect(s, color, body_rect, 2)

        if d["limbNum"] > 0:

            # draw one limb to see how big it is
            limb_rect = limb(scratch, d, (0, 0))

            t = d["limbLocation"]
            if t == 0:
                x, y = body_rect.bottomleft
                y -= body_rect.height / 4
            else:
                x, y = body_rect.midleft

            dx = body_rect.width / d["limbNum"]
            for i in range(0, d["limbNum"]):
                limb_rect = limb(s, d, (x, y))
                x += dx

        t = d["headLocation"]
        if t == 0:
            x, y = body_rect.midleft
        elif t == 1:
            x, y = body_rect.topleft
            y -= body_rect.height / 4
        else:
            x, y = body_rect.topleft

        head_rect = head(s, d, (x, y))
        x, y = head_rect.center
        y = y + head_rect.height / 6
        mouth_rect = mouth(s, d, (x, y))

        t = d["eyeLocation"]
        if t == 0:
            x, y = head_rect.center
            y -= head_rect.height / 4
        else:
            x, y = head_rect.topleft

        for i in range(0, d["eyeNum"]):
            eye = MonsterEye(d)
            eye.rect.center = (x, y)
            eye.render()
            self.parts.append(eye)
            x += (d["eyeSkill"] + 1) * 5

        s.unlock()

        # draw the parts onto the monster
        [ s.blit(part.image, part.rect) for part in self.parts ]

        self.image = s
        self.rect = s.get_rect()
