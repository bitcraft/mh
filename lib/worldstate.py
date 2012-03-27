from renderer import AreaCamera
from rpg import GRAB, LIFT

from lib2d.gamestate import GameState
from lib2d.statedriver import driver as sd
from lib2d.buttons import *
from lib2d.vec import Vec2d
from lib2d.quadtree import QuadTree, FrozenRect
from lib2d.signals import *
from lib2d import tmxloader, res, gui

import math, pygame

debug = 1

movt_fix = 1/math.sqrt(2)


class ExitTile(FrozenRect):
    def __init__(self, rect, exit):
        FrozenRect.__init__(self, rect)
        self._value = exit

    def __repr__(self):
        return "<ExitTile ({}, {}, {}, {}): {}>".format(
            self._left,
            self._top,
            self._width,
            self._height,
            self._value)

class ControllerHandler(object):
    """
    Some kind of glue between the input of the player and the actions
    he is allowed to make.  New territory here.
    """

    def __init__(self, controller, model):
        self.model = model


    def getActions(self):
        """
        Return a list of actions the character is allowed to make at the
        moment
        """

        pass


class SoundManager(object):
    def __init__(self):
        self.sounds = {}

    def loadSound(self, name, filename):
        self.sounds[name] = res.loadSound(filename)

    def play(self, name, volume=1.0):
        sound = self.sounds[name]
        sound.set_volume(volume)
        sound.stop()
        sound.play()



SoundMan = SoundManager()

class WorldState(GameState):
    """
    This state is where the player will move the hero around the map
    interacting with npcs, other players, objects, etc.

    Expects to load a specially formatted TMX map created with Tiled.
    Layers:
        Control Tiles
        Upper Partial Tiles
        Lower Partial Tiles
        Lower Full Tiles

    The control layer is where objects and boundries are placed.  It will not
    be rendered.  Your map must not have any spaces that are open.  Each space
    must have a tile in it.  Blank spaces will not be rendered properly and
    will leave annoying trails on the map.

    The control layer must be created with the utility included with lib2d.  It
    contains metadata that lib2d can use to layout and position objects
    correctly.

    i would really like the game to be sandboxable...set traps,
    make contraptions, etc

    controls:
        picking up objects will affect what your buttons do
        equipted items always have a dedicated button
        should have hot-swap button and drop button
    """

    def __init__(self, area, startPosition=None):
        GameState.__init__(self)
        self.area = area
        self.heroOnExit = False         # use this flag when warping
        self.background = (203, 204, 177)
        self.foreground = (0, 0, 0)
        self.blank = True


    def activate(self):
        self.msgFont = pygame.font.Font((res.fontPath("volter.ttf")), 9)
        self.border = gui.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = gui.GraphicBox("dialog2.png")
        self.player_vector = Vec2d(0,0)

        # get the root and the hero from it
        root = self.area.getRoot()
        self.hero = root.getChildByGUID(1)
        self.hero.move_speed = 1

        # add the hero to this map if it isn't ready there
        if not self.area.hasChild(self.hero):
            self.area.add(self.hero)

        # load the tmx data here.  it will be shared with the camera.
        self.tmxdata = tmxloader.load_pygame(
                       self.area.mappath, force_colorkey=(128,128,0))

        # attach a camera
        sw, sh = sd.get_size()
        mw = sw * .75
        mh = sh * .75
        self.camera = AreaCamera(self.area,((0,0), (mw, mh)),
                                 tmxdata=self.tmxdata)

        self.mapBorder = pygame.Rect((0,0,mw+6,mh+6))
        self.msgBorder = pygame.Rect((0,mh,sw,sh-mh))
        self.hudBorder = pygame.Rect((mw,0,sw-mw,mh+6))


        # play music if any has been set in tiled
        try:
            res.playMusic(self.tmxdata.music)
        except AttributeError:
            res.fadeoutMusic()
            
        # quadtree for handling collisions with exit tiles
        rects = []
        for guid, param in self.area.exits.items():
            try:
                x, y, l = param[0]
            except:
                continue
            rects.append(ExitTile((x,y,
                self.tmxdata.tilewidth, self.tmxdata.tileheight),
                guid))

        self.exitQT = QuadTree(rects)

        # load tile sounds
        for i, layer in enumerate(self.tmxdata.tilelayers):
            props = self.tmxdata.getTilePropertiesByLayer(i)
            for gid, tileProp in props:
                for key, value in tileProp.items():
                    if key[4:].lower() == "sound":
                        SoundMan.loadSound(key, value)

        # determine if the hero is on an exit warp.
        # if so, then we need to ignore collisions with it until the player
        # moves off of the exit.
        #if self.exitQT.hit(self.area.getpygame.Rect(self.hero)):
        #    self.heroOnExit = True


    def deactivate(self):
        pass

       
    def drawSidebar(self, surface, rect):
        # draw the static portions of the sidebar
        sx, sy, sw, sh = rect

        self.border.draw(surface, self.hudBorder)
        titleFont = pygame.font.Font(res.fontPath("northwoodhigh.ttf"), 20)
        i = titleFont.render("MH", 1, (128,128,128))
        surface.blit(i, (sw/2+sx-i.get_size()[0]/2+1, sy+3))
        i = titleFont.render("MH", 1, self.foreground)
        surface.blit(i, (sw/2+sx-i.get_size()[0]/2, sy+2))

        headFont = pygame.font.Font(res.fontPath("red_mamba.ttf"), 6)

        i = headFont.render("Left Hand", 1, self.foreground, self.background)
        surface.blit(i, (sx+ 10, sy+30))


    def draw(self, surface):
        sx, sy = surface.get_size()

        if self.blank:
            self.blank = False
            surface.fill(self.background)
            self.drawSidebar(surface, self.hudBorder)

        # the main map
        self.camera.center(self.area.getPosition(self.hero))
        self.camera.draw(surface, origin=(4, 4))

        # borders
        self.borderFilled.draw(surface, self.msgBorder)
        self.border.draw(surface, self.mapBorder)

        log = "\n".join(self.area.messages[-5:])
        rect = self.msgBorder.inflate(-16,-12)
        gui.drawText(surface, log, (0,0,0), rect, self.msgFont)


        return

        # debug stuff...may/may not work
        for obj, pos in self.area.getPositions():
            y,x,w,h = self.area.topygame.Rect(self.area.getBBox(obj))
            surface.fill((128,0,64), (self.camera.toScreen((x,y)), (w,h)))


        for gid, param in self.area.exits.items():
            x, y, l = param[0]
            size = (16, 16)
            pygame.draw.rect(surface,(128,128,255),
                            (self.camera.toScreen((x,y)),size))

        for rect in self.area.geopygame.Rect:
            y, x, sx, sy = rect
            pygame.draw.rect(surface,
                     (255,0,128, 20),
                     (self.camera.toScreen((x, y)),
                     (sx, sy)))
    
 
    def update(self, time):
        self.area.update(time)
        self.camera.update(time)

        #if self.walkSoundPlaying > 0:
        #    self.walkSoundPlaying += time
        #    if self.walkSoundPlaying >= self.walkSoundDelay:
        #        self.walkSoundPlaying = 0

        x, y = self.player_vector

        if x==y==0:
            if self.hero.avatar.isPlaying("walk"):
                self.hero.avatar.play("stand")
        else:
            self.area.movePosition(self.hero, (x, y, 0), True, caller=self)


    def handle_commandlist(self, cmdlist):
        x = 0
        y = 0

        for cls, cmd, arg in cmdlist:
            if arg == BUTTONUP:
                if cmd == P1_UP:
                    self.player_vector.x = 0
                elif cmd == P1_DOWN:
                    self.player_vector.x = 0
                elif cmd == P1_LEFT:
                    self.player_vector.y = 0
                elif cmd == P1_RIGHT:
                    self.player_vector.y = 0
                elif cmd == P1_ACTION2:
                    self.hero.ungrab()
                elif cmd == P1_ACTION3:
                    self.hero.unlift()

            # these actions will repeat as button is held down
            elif arg == BUTTONDOWN or arg == BUTTONHELD:
                if   cmd == P1_UP:      x = -1
                elif cmd == P1_DOWN:    x = 1
                elif cmd == P1_LEFT:    y = -1
                elif cmd == P1_RIGHT:   y = 1

            # these actions will not repeat if button is held
            if arg == BUTTONDOWN:
                if cmd == P1_ACTION1:
                    self.hero.attack()

                elif cmd == P1_ACTION2:
                    self.hero.grab()

                elif cmd == P1_ACTION3:
                    self.hero.lift()


        if (not x == 0) and (not y == 0):
            x *= movt_fix
            y *= movt_fix

        if (not x == 0) or (not y == 0):
            self.player_vector.y = y * self.hero.move_speed
            self.player_vector.x = x * self.hero.move_speed

            # don't rotate the player if he's grabbing something
            if not self.hero.arms == GRAB:
                self.area.setOrientation(self.hero, math.atan2(x, y))



def tileToWorld(state, (x, y, l)):
    xx = int(y) * state.tmxdata.tilewidth
    yy = int(x) * state.tmxdata.tileheight
    return xx, yy, l


def worldToTile(state, (x, y, l)):
    # return the tile position of an object
    xx = int(y) / state.tmxdata.tilewidth
    yy = int(x) / state.tmxdata.tileheight
    return xx, yy, 0


@receiver(emitSound)
def playSound(sender, **kwargs):
    pass


@receiver(bodyRelMove)
def bodyMove(sender, **kwargs):
    area = sender
    body = kwargs['body']
    position = kwargs['position']
    state = kwargs['caller']

    if body == state.hero:
        body.avatar.play("walk")
        tilePos = worldToTile(state, position)
        prop = state.tmxdata.getTileProperties(tilePos)

        """
        if prop == None:
            state.walkSound = res.dummySound
        
        else:
            t = prop.get('walkSound', None)
            if t:
                state.walkSound = state.sounds[t]
                state.walkSound.set_volume(.50)
            else:
                state.walkSound = res.dummySound


        if state.walkSoundPlaying == 0:
            state.walkSoundPlaying += time
            state.walkSound.play()

        """

        """
        # test for collisions with exits
        exits = self.exitQT.hit(area.getpygame.Rect(body))

        if not exits and bodyOnExit:
            bodyOnExit = False

        if exits and not bodyOnExit:
            # warp the player
            exit = exits.pop()
            position, guid = area.exits[exit.value]
            if not guid == None: 
                area = area.getRoot().getChildByGUID(guid)
                position, otherExit = area.exits[exit.value]
                x, y, l = position
                l = 4

                ox, oy, ol = area.getOldPosition(body)

                if x-ox > 0:
                    dx = self.tmxdata.tilewidth / 2
                elif x-ox < 0:
                    dx = -self.tmxdata.tilewidth / 2
                else:
                    dx = 0    

                if y-oy > 0:
                    dy = self.tmxdata.tileheight / 2
                elif y-oy < 0:
                    dy = -self.tmxdata.tileheight / 2
                else:
                    dy = 0
                
                face = area.getOrientation(body)

                area.add(body)
                print x+dx, y+dy
                area.setPosition(body, (x, y+dy, l))
                area.setOrientation(body, face)
                sd.push(WorldState(area))
                sd.done()
        """
