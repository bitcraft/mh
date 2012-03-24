from lib2d.objects import AvatarObject
from lib2d.buttons import *
from conditions import *
from math import cos, sin, degrees

from dialog import *

icon_size = (16,16)


GRAB = 1
LIFT = 2
ATTACK = 3

status = """
# a list of all values that a rpg entity can have as a flag
# if an icon is to be used, then include after the name

normal,6,4
poisoned,19,2
frozen
burning
tired,4,5
sleeping,2,29
bleeding,6,0
gimped
berserk

"""

class Status(object):
    """
    simple object to determine the status of a object
    singleton-esque
    """

    def __init__(self, name, icon, description, value):
        self.name = name
        self.icon = icon
        self.description = desc
        self.value = value


for line in status:
    if not line[0] == "#" or line[0] == "":
        try:
            name, x, y = line.split(",")
        except:
            name = line

        

def default_icon():
    return None



class LivingObject(AvatarObject):
    """
    something that is alive
    """

    def __init__(self):
        AvatarObject.__init__(self)

        self.defaultSpells = []
        self.isAlive = True
        self.hp = 10
        self.wieght = 10

        # stats
        self.str = 1
        self.int = 1
        self.dex = 1
        self.exp = 0

        self.init()

        self._oldPosition = None

        self.arms = None
        self.leftHand = None
        self.rightHand = None
        self.join = None

        self.reach = 2   # number of pixels that char can reach to grab things


    def init(self):
        self.stuck = False


    def get_spells(self):
        """
        return a list of spells for the actor
        """

        return self.defaultSpells


    def stick(self):
        self.parent.stick(self)
        self.stuck = True


    def unstick(self):
        self.parent.unstick(self)
        self.stuck = False


    def getObjectInFront(self):
        """
        return reference to an object within self.reach distance that is
        in front of this object
        """
        a = self.parent.getOrientation(self)
        x = self.reach * round(cos(a))
        y = self.reach * round(sin(a))
        bbox = self.parent.getBBox(self).move(y, x, 0)
        collide = self.parent.testCollideObjects(bbox)
        if len(collide) > 1:
            collide.remove(self)
            return collide.pop()

        return None


    def lift(self):
        """
        attempt to lift and carry an object
        """
         
        if self.arms == None:
            other = self.getObjectInFront()
            if other:
                # TODO: test weight

                bOther = self.parent.getBBox(other)
                bSelf = self.parent.getBBox(self)

                dx = bSelf.back - bOther.back
                dy = bSelf.left - bOther.left
                dz = (bSelf.top + 6) - bOther.bottom
                self.parent.movePosition(other, (dx, dy, dz))
                self.arms = LIFT
                self.join = other
                self.parent.join(self, other)
                return True

        return False


    def unlift(self):
        """
        drops lifted object
        """

        if self.join == None:
            return

        a = self.parent.getOrientation(self)
        bOther = self.parent.getBBox(self.join)
        bSelf = self.parent.getBBox(self)

        dx = (bOther.depth + self.reach) * round(sin(a))
        dy = (bOther.width + self.reach) * round(cos(a))
        dz = -bOther.bottom

        if self.parent.movePosition(self.join, (dx, dy, dz)):
            self.parent.unjoin(self, self.join)
            self.arms = None
            self.join = None
            return True
   

    def grab(self):
        """
        attempt to grab something
        object will move around with this object
        """

        if self.arms == None:
            # play animation
            other = self.getObjectInFront()
            if other:
                self.parent.join(self, other)
                self.arms = GRAB
                self.join = other
                return True

        return False 
    

    def ungrab(self):
        """
        ungrab something
        """

        self.parent.unjoin(self, self.join)
        self.arms = None
        self.join = None
        return True


class Hero(LivingObject):
    """
    Special character that is played by a player
    """

    def attack(self):
        if self.arms == None:
            self.avatar.play("attack", loop=0)
            target = self.getObjectInFront()
            if not target == None:
                target.OnPush(self)

class NPC(LivingObject):
    """
    """

    def __init__(self):
        LivingObject.__init__(self)
        self.greeting = "<no greeting>"
        self.dialog = None
        self.d_arg = []
        self.d_kwarg = {}


    def OnPush(self, other):
        """
        When the player pushes this NPC.

        Will not be called when the NPC pushes into the player.
        """

        if self.dialog == None:
            dialog = TextDialog(self.greeting, title=self.short_name)
            sd.start(dialog)
        else:
            dialog = self.dialog(*self.d_arg, **self.d_kwarg)
            sd.start(dialog)
       
 
    def OnActivate(self, other):
        """
        When the player uses the Action button on or facing this object.
        """

        dialog = TextDialog(self.greeting, self.short_name)
        sd.start(dialog) 
