import os

import pygame


def load(iterator):
    """
    given a list of strings, return classes that handle the given spell.

    somewhat jenky stuff here, but does this to prevent excessive opening
    and closing of the tilesheet.

    TODO: this needs to be properly finished
    """

    g = globals()
    classes = globals().keys()
    classes = [ i for i in classes if not i[0] == "_" ]

    remove = ("load", "tilesheet", "get_icon", "pygame", "os", "icon_size", "Spell")
    [ classes.remove(i) for i in remove ]
    ret = []

    if iterator == "all":
        return [ g[i]() for i in classes ]

    else:
        return [ g[i]() for i in iterator if i in classes ]

    return ret

tilesheet = os.path.join("resources", "misc", "spellicons.png")
icon_size = (32, 32)

def get_icon(position):
    image = pygame.image.load(tilesheet)
    x = position[0] * icon_size[0]
    y = position[1] * icon_size[1]
    icon = pygame.Surface(icon_size, pygame.SRCALPHA)
    icon.blit(image, (0,0), ((x,y), icon_size))
    return icon.convert()

class Spell(object):
    """
    Spells can be cast, also includes physical attacks.
    They are meant to be stored as and manged as simple python classes
    """

    uses = 1

    def __init__(self):
        self.icon = get_icon(self.icon)
        self.started = 0
        self.finished = 0
        self.text = self.name

    def start(self):
        self.started = 1

    def update(self):
        raise NotImplementedError

    def finish(self):
        raise NotImplementedError

    def __call__(self, *arg):
        self.cast(*arg)

    def cast(self, caller, target):
        self.caller = caller
        self.target = target

        if self.started:
            self.update()
        else:
            self.start()
            self.update()

        try:
            self.finish()
        except NotImplementedError:
            self.finished = 1

class Attack(Spell):
    icon = (5,2)
    name = "Attack" 
    description = "Does a basic attack on a creature"
    uses = -1

    def update(self):
        self.target.hp -= self.caller.str
        self.caller.avatar.play("attack00")
        self.text = "{0}".format(self.caller.str)

class Flee(Spell):
    icon = (8,13)
    name = "Flee" 
    description = "Run away!!!"
    uses = -1

    def update(self):
        self.text = "Run away!!"

class Poison(Spell):
    icon = (19, 18)
    name = "Poison"
    description = "Poison the target"
    strength = 1

    def update(self):
        from conditions import POISONED

        self.target.condition += POISONED
        self.target.hp -= 2
        self.text = "-{0}".format(self.strength)

    def finish(self):
        pass

class Focus(Spell):
    icon = (1, 27)
    name = "Focus"
    description = "Next spell cannot miss"

    def update(self):
        self.text = "Locked on!"

class Fire(Spell):
    icon = (5, 11)
    name = "Fire"
    description = "Burn the target"

    def update(self):
        self.text = "{0}".format(self.caller.int)

#class Freeze(Spell):
#    icon = (
#    name = "Freeze"
#    description = "Freeze the target"
#
#    def update(self):
#        self.text = "{0}".format(self.caller.int)

