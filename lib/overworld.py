import math

from pygame import Rect
from pygame.transform import scale, rotate

from renderer import Camera
from lib2d.cursor import KeyCursor
from lib2d.gamestate import GameState
from lib2d.tilemap import BufferedTilemapRenderer
from lib2d.statedriver import driver as sd
from lib2d.buttons import *
import lib2d.res as res

HAND_OPEN = 0
HAND_CLOSED = 1
HAND_ARROW = 2


movt_fix = 1/math.sqrt(2)


class OverworldCamera(Camera):
    """
    Modified slightly to world with a different map format
    """

    def draw(self, surface):
        self.tilemap.draw(surface)

class OverworldState(GameState):
    """
    State for looking at the world map.  Tools can be used to check
    various aspects of it.  Kinda like...simcity.
    """

    def __init__(self, map_name=None):
        GameState.__init__(self)
        self.map_name = map_name


    def activate(self):
        GameState.activate(self)

        w, h = sd.get_size()

        self.cr_open = scale(res.loadImage("open.png", 0, 1), (20,30))
        self.cr_grasp = scale(res.loadImage("grasp.png", 0, 1), (20, 25))
        self.cr_arrow = res.loadImage("next_arrow.png", 0, 1)

        self.cr = KeyCursor(self.cr_open)
        self.cr_state = HAND_OPEN

        self.cr_bounds = Rect(0,0,w,h).inflate(-w*.2, -h*.2)
        self.cr_bounds.height -= 30
        self.cr_bounds.width -= 20
        self.cr_pos = list(self.cr_bounds.center)
        self.cr_speed = 0
        self.cr.enable()

        self.map_pos = self.cr_pos[:]

        path = res.mapPath("overworld3.tmx")

        self.tilemap = BufferedTilemapRenderer(path,
                       (w,h), force_colorkey=(128,0,63))

        self.camera = OverworldCamera([], self.tilemap, ((0,0), (w,h)))
        self.camera.center(self.cr_pos)
        self.tilemap.redraw()


        self.cleared = 0


    def deactivate(self):
        GameState.deactivate(self)
    

    def draw(self, surface):
        if self.cleared == 0:
            surface.fill((0,64,128))
            self.cleared = 1

        if self.cr_pos[0] < self.cr_bounds.left:
            self.map_pos[0] -= self.cr_bounds.left - self.cr_pos[0]
            self.cr_pos[0] = self.cr_bounds.left
            if self.cr_state == HAND_OPEN:
                self.cr.setImage(self.cr_arrow)
                self.cr_state = HAND_ARROW

        elif self.cr_pos[0] > self.cr_bounds.right:
            self.map_pos[0] -= self.cr_bounds.right - self.cr_pos[0]
            self.cr_pos[0] = self.cr_bounds.right
            if self.cr_state == HAND_OPEN:
                self.cr.setImage(self.cr_arrow)
                self.cr_state = HAND_ARROW
 
        if self.cr_pos[1] < self.cr_bounds.top:
            self.map_pos[1] -= self.cr_bounds.top - self.cr_pos[1]
            self.cr_pos[1] = self.cr_bounds.top
            if self.cr_state == HAND_OPEN:
                self.cr.setImage(rotate(self.cr_arrow, 90))
                self.cr_state = HAND_ARROW

        elif self.cr_pos[1] > self.cr_bounds.bottom:
            self.map_pos[1] -= self.cr_bounds.bottom - self.cr_pos[1]
            self.cr_pos[1] = self.cr_bounds.bottom
            if self.cr_state == HAND_OPEN:
                self.cr.setImage(rotate(self.cr_arrow, -90))
                self.cr_state = HAND_ARROW

        self.cr.setPos(self.cr_pos)
        self.tilemap.center(self.map_pos)
        self.camera.draw(surface)
        self.cr.draw(surface)


    def grasp(self):
        self.cr_state = HAND_CLOSED
        self.cr.setImage(self.cr_grasp)

    
    def ungrasp(self):
        self.cr_state = HAND_OPEN
        self.cr.setImage(self.cr_open)


    def update(self, time):
        self.camera.update(time)


    def handle_commandlist(self, cmdlist):
        buttonup = 0
        x = 0
        y = 0

        for cls, cmd, arg in cmdlist:
            if arg == BUTTONUP:
                if cmd == P1_ACTION1:
                    self.ungrasp()
 
                elif (cmd == P1_UP) or (cmd == P1_DOWN) \
                or (cmd == P1_LEFT) or (cmd == P1_RIGHT):
                    buttonup = 1  

            elif arg:
                if cmd == P1_UP:        y = -1
                elif cmd == P1_DOWN:    y = 1
                elif cmd == P1_LEFT:    x = -1
                elif cmd == P1_RIGHT:   x = 1
                elif (cmd == P1_ACTION1) and (self.cr_state == HAND_OPEN):
                    self.grasp()

        if (not x == 0) and (not y == 0):
            x *= movt_fix
            y *= movt_fix

        if (not x == 0) or (not y == 0):
            self.cr_speed += .8
            if self.cr_speed > 16: self.cr_speed = 16
            self.cr_pos[0] += x*self.cr_speed
            self.cr_pos[1] += y*self.cr_speed

        elif buttonup:
            self.cr_speed = 0
            if (x==y==0) or (self.cr_state == HAND_ARROW):
                self.cr_state = HAND_OPEN
                self.cr.setImage(self.cr_open)
