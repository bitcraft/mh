from lib.levelstate import LevelState
from lib import world

from lib2d.gamestate import GameState
from lib2d.cmenu import cMenu
from lib2d.statedriver import driver as sd
from lib2d.objects import loadObject
from lib2d import res, gui

import pygame, os


hints = """You must defeat the evil scientist in the lower levels!


You arrive unarmed.  Use your cunning to defeat him!
Q - Use items
W - Jump
E - Grab items


When grabbing things, hold the key and you can push or pull them.
Use Q to activate terminals, search items, press buttons, or open doors.
The orange buttons near an elevator will call it to your level.


Good luck, Agent!"""



class InstructionScreen(GameState):
    def activate(self):
        self.foreground = (0,0,0)
        self.background = (109, 109, 109)
        self.border = gui.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = gui.GraphicBox("dialog2.png")
        self.msgFont = pygame.font.Font((res.fontPath("volter.ttf")), 9)
        self.activated = True
        self.redraw = True

    def draw(self, surface):
        if self.redraw:
            sw, sh = surface.get_size()
            self.redraw = False
            self.borderFilled.draw(surface, ((0,0), (sw, sh)))
            rect = pygame.Rect((sw*.05, sh*.05, sw*.90, sh*.90))
            gui.drawText(surface, hints, (128, 129, 129), rect.move(1,1), self.msgFont)
            gui.drawText(surface, hints, self.foreground, rect, self.msgFont)

    def handle_event(self, event):
        if event.type == pygame.locals.KEYDOWN:
            sd.done()


class TitleScreen(GameState):

    def activate(self):
        self.background = (109, 109, 109)
        self.border = gui.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = gui.GraphicBox("dialog2.png")
        self.counter = 0
        self.game = None
        self.activated = True
        self.reactivate()


    def deactivate(self):
        GameState.deactivate(self)


    def reactivate(self):
        if self.game:
            self.menu = cMenu(((32,20), sd.get_size()),
                20, -5, 'vertical', 100,
                [('New Game', self.new_game),
                ('Continue', self.continue_game),
                #('Save', self.save_game),
                #('Reload', self.load_game),
                #('Save and Quit', self.savequit_game),
                ('Quit', self.quit_game)],
                font="visitor1.ttf", font_size=20)
        else:
            self.menu = cMenu(((32,20), sd.get_size()),
                20, -5, 'vertical', 100,
                [('New Game', self.new_game),
                #('Continue', self.load_game),
                ('Introduction', self.show_intro),
                ('Quit', self.quit_game)],
                font="visitor1.ttf", font_size=20)

        self.menu.ready()
        self.redraw = True
        res.playMusic("oneslymove.ogg")


    def handle_event(self, event):
        self.menu.handle_event(event)


    def draw(self, surface):
        if self.redraw:
            self.redraw = False
            if self.game:
                self.border.draw(surface, ((0,0), surface.get_size()))
            else:
                self.borderFilled.draw(surface, ((0,0), surface.get_size()))

        self.menu.draw(surface)


    def new_game(self):
        res.fadeoutMusic(1000)
        self.game = world.build()
        level = self.game.getChildByGUID(5001)
        sd.start(LevelState(level))


    def save_game(self):
        path = os.path.join("resources", "saves", "save")
        [ i.unload() for i in self.game.getChildren() ]
        self.game.save(path)
        self.continue_game()


    def load_game(self):
        try:
            path = os.path.join("resources", "saves", "save")
            self.game = loadObject(path)
        except IOError:
            return self.new_game()

        level = self.game.getChildByGUID(5001)
        sd.start(LevelState(level))


    def continue_game(self):
        res.fadeoutMusic(1000)
        level = self.game.getChildByGUID(5001)
        sd.start(LevelState(level))


    def show_intro(self):
        sd.start_restart(InstructionScreen())


    def savequit_game(self):
        if self.game:
            path = os.path.join("resources", "saves", "save")
            [ i.unload() for i in self.game.getChildren() ]
            self.game.save(path)
        self.quit_game()


    def quit_game(self):
        sd.done() 

