from random import uniform
from itertools import cycle
from threading import Thread
import queue

from pygame import Rect, Surface

from lib2d.gamestate import GameState
from lib2d.cmenu import cMenu
from lib2d.statedriver import driver as sd
from lib2d.banner import TextBanner
from lib2d.subpixelsurface import SubPixelSurface
from lib2d.objects import loadObject
from lib2d import res
from .worldstate import WorldState
from .cutscene import Cutscene


class SubPixelThread(Thread):
    """
    Process a subpixel image in the background.
    """

    def __init__(self, inQueue, outQueue):

        Thread.__init__(self)
        self.inQueue = inQueue
        self.outQueue = outQueue


    def run(self):
        while 1:

            try:
                surface = self.inQueue.get(0)
            except Empty:
                break
            else:
                subpix = SubPixelSurface(surface, 10, 10)
                self.outQueue.put(subpix)
                self.inQueue.task_done()


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
        self.change_delay = 8000        # seconds until map moves to next point
        self.map_fadeout = 60.0         # must be a float
        self.last_update = 0
        self.surfaceQueue = queue.Queue()
        self.subpixelQueue = queue.Queue()

        self.hotspots = cycle(([300,500], [750, 800], [350, 260], [700, 340], [120, 1000], [800, 830], [480, 900]))
        
        self.overworld = res.loadImage("overworld.png")

        self.menu = cMenu(Rect((42,20), sd.get_size()),
            20, 5, 'vertical', 100,
            [('New Game', self.new_game),
            ('Battle Test', self.continue_game),
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
        except queue.Empty:
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
        uni = loadObject("mh")
        village = uni.getChildByGUID(1001)
        sd.start_restart(WorldState(village))

    def continue_game(self):
        sd.start_restart(BattleState(None, None))


    def show_intro(self):
        s = Cutscene(res.miscPath("intro.txt", "scripts")) 
        sd.start_restart(s)


    def quit_game(self):
       sd.done() 

