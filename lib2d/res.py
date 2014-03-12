"""

MASSIVE module meant for loading data data:
    objects
    images
    sounds
    music

Attempt to consolidate game data into a system that can be accessed
through standard python calls without worrying about the underlying system
of how files and resources are stored.

The most important property will be the storage and managment of python pickles
that represent game objects.

Game objects should be pickable and able to be loaded off disk when needed.
Game objects should be accessed by a unique id (guid).
Game objects should be managed by the game.

If all objects inherit form this mythical object, then save games would be
simple:
    create a master "blank state"
    on a save, dump the changed state
    find any changes between the master state and the changed state
    the resulting delta will be the saved game
"""

import os.path

import pygame


DEBUG = False


def debug(text):
    if DEBUG: sys.stdout.write(text)


_resPath = "resources"
_defaultFont = None


class NoSound:
    def play(self): pass

    def stop(self): pass

    def set_volume(self, v): pass


dummySound = NoSound()


def setResourcePath(path):
    global _resPath
    _resPath = path


def defaultFont():
    global _defaultFont

    if _defaultFont == None:
        _defaultFont = pygame.font.get_default_font()

    return _defaultFont


def fontPath(filename):
    return os.path.join(_resPath, "fonts", filename)


def mapPath(filename):
    return os.path.join(_resPath, "maps", filename)


def aniPath(filename):
    return os.path.join(_resPath, "animations", filename)


def imagePath(filename):
    return os.path.join(_resPath, "images", filename)


def loadImage(name, alpha=False, colorkey=False):
    fullpath = imagePath(name)

    try:
        image = pygame.image.load(fullpath)

    except pygame.error:
        msg = "Cannot load image: {}"
        print(msg.format(fullpath))
        raise Exception

    if alpha:
        image = image.convert_alpha()

    elif colorkey:
        image = image.convert()
        image.set_colorkey(image.get_at((0, 0)), pygame.RLEACCEL)

    else:
        image = image.convert()

    return image


def soundPath(filename):
    return os.path.join(_resPath, "sounds", filename)


def loadSound(filename):
    fullpath = soundPath(filename)

    if not pygame.mixer:
        debug("Cannot load sound: pygame.mixer not ready\n")
        return dummySound

    # pygame will load a sound even if it doesn't exist... do a sanity check.
    open(fullpath).close()

    try:
        sound = pygame.mixer.Sound(fullpath)
    except pygame.error:
        debug("Cannot load sound: %s\n" % fullpath)
        return dummySound

    return sound


def musicPath(filename):
    return os.path.join(_resPath, "music", filename)


def playMusic(filename, *args, **kwargs):
    stopMusic()
    fullpath = musicPath(filename)
    pygame.mixer.music.load(fullpath)
    pygame.mixer.music.play(kwargs.get("loops", -1))


def stopMusic():
    pygame.mixer.music.stop()


def fadeoutMusic(time=3000):
    pygame.mixer.music.fadeout(time)


def miscPath(filename, folder):
    return os.path.join(_resPath, folder, filename)
