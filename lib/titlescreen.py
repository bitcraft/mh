from lib2d.client.gamestate import GameState
from lib2d.client.waitscreen import WaitScreen
from lib2d.client.cmenu import cMenu
from lib2d.client.tilemap import BufferedTilemapRenderer
from lib2d.client.statedriver import driver as sd
from lib2d.client.banner import TextBanner
from lib2d.client.subpixelsurface import SubPixelSurface
from lib2d.common.objects import loadObject
from lib2d.common import res

from pygame import Rect, Surface
import pygame

from worldstate import WorldState
from cutscene import Cutscene
import world

from collections import deque
from random import randint, random, uniform
from itertools import cycle
from threading import Thread
from Queue import Queue as queue
from Queue import Empty
import os.path, time


class SubPixelThread(Thread):
    """
    Process a subpixel image in the background.
    """

    def __init__(self, inQueue, outQueue):

        Thread.__init__(self)
        self.inQueue = inQueue
        self.outQueue = outQueue
        self.running = True
        self.done = False


    def run(self):
        while self.running:

            try:
                surface = self.inQueue.get(0)
            except Empty:
                break
            else:
                subpix = SubPixelSurface(surface, 10, 10)
                self.outQueue.put(subpix)
                self.inQueue.task_done()

            if not self.running: self.done = True


class TitleScreen(GameState):
    """
    Fancy title screen that uses a thread and subpixel rendering to draw
    a slow panning map under the main menu.

    Only tested on an intel dual-core macbook.
    """


    def activate(self):
        self.activated = True

        res.fadeoutMusic()

        self.maps = []
        self.change_delay = 2000        # seconds until map moves to next point
        self.map_fadeout = 60.0         # must be a float
        self.last_update = 0
        self.surfaceQueue = queue()
        self.subpixelQueue = queue()

        self.hotspots = cycle(([300,500], [750, 800], [350, 260], [700, 340], [120, 1000], [800, 830], [480, 900]))
        
        self.overworld = res.loadImage("overworld.png")

        self.menu = cMenu(Rect((42,20), sd.get_size()),
            20, 5, 'vertical', 100,
            [('New Game', self.new_game),
            ('Load Game', self.load_game),
            ('Introduction', self.show_intro),
            ('Quit Game', self.quit_game)],
            font="northwoodhigh.ttf", font_size=24)

        self.menu.ready()
        self.change_map()

    def change_map(self):
        pos = list(next(self.hotspots)[:])
        r = Rect((0,0), sd.get_size()).inflate((48, 48))
        r.center = pos
        clip = Surface(r.size)
        clip.blit(self.overworld, (0,0), r)

        self.surfaceQueue.put(clip)
        self.thread = SubPixelThread(self.surfaceQueue, self.subpixelQueue)
        self.thread.start()


    def deactivate(self):
        self.thread.running = False
        while not self.thread.done:
            pass


    def update(self, time):

        for i in self.maps:
            i[0] += i[2]
            i[1] += i[3]
            if i[4] > 0:
                i[4] += 1

        self.last_update += time
        if self.last_update >= self.change_delay:
            self.change_map()
            self.last_update -= self.change_delay

        try:
            image = self.subpixelQueue.get(0)
        except Empty:
            pass

        else:
            if not len(self.maps) == 0:
                self.maps[0][4] = 1  # mark it for fadeout

            w0, h0 = sd.get_size()
            w1, h1 = image.get_size()

            self.maps.insert(0, [-(w1-w0)/2, -(h1-h0)/2,
                             round(uniform(-0.08, 0.08), 3),
                             round(uniform(-0.08, 0.08), 3), 0, image])

            self.subpixelQueue.task_done()

        self.maps = [ i for i in self.maps if i[4] < self.map_fadeout ][:2]


    def handle_event(self, event):
        self.menu.handle_event(event)


    def draw(self, surface):
        if len(self.maps) == 0:
            surface.fill((0,0,0))
            msg = TextBanner("Please wait...", (128, 128, 128), size=10)
            surface.blit(msg.render(alpha=True), (140,140))
            return

        for i in self.maps:
            if i[4] > 0:
                s = i[5].at(i[0], i[1])
                m = i[4] / self.map_fadeout
                s.set_alpha(255 - (m * 255))

            else:
                s = i[5].at(i[0], i[1])
            
            pos = i[0], i[1]
            surface.blit(s, pos)

        self.menu.draw(surface)


    def new_game(self):
        from lib2d.server.start import start_local


        def build():
            print "world stat"
            game = world.build()
            sd.start(WorldState(game.getChildByGUID(5001)))

        res.fadeoutMusic(1000)
        #sd.start(WaitScreen(build))
        game = world.build()
        start_local()
        sd.start(WorldState(game.getChildByGUID(5001)))


    def load_game(self):
        res.fadeoutMusic(1000)
        try:
            path = os.path.join("resources", "saves", "save")
            self.game = loadObject(path)
        except IOError:
            return self.new_game()

        level = self.game.getChildByGUID(5001)
        sd.start(WorldState(level))


    def show_intro(self):
        s = Cutscene(res.miscPath("intro.txt", "scripts")) 
        sd.start_restart(s)


    def quit_game(self):
        self.thread.running = False
        while not self.thread.done:
            pass
        sd.done() 

