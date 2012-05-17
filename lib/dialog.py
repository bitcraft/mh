from lib2d.client.buttons import *
from lib2d.client.gamestate import GameState
from lib2d.client.statedriver import driver as sd
from lib2d.client import gui
from lib2d.common import res

from pygame.locals import *
from pygame.surface import Surface
import pygame.draw as draw
import pygame

from textwrap import wrap


class TextDialog(GameState):
    """
    State that takes focus and waits for player to press a key
    after displaying some some text.
    """

    # works well for the defualt font and size 
    wrap_width = 44 
 
    wait_sound = res.loadSound("select0.wav")
    wait_sound.set_volume(0.40)


    def __init__(self, text, title=None):
        GameState.__init__(self)
        self.font = "dpcomic.ttf"
        self.text = text
        self.title = title
        self.blank = True


    # when given focus for first time
    def activate(self):
        from lib2d.gui import GraphicBox
        self.border = GraphicBox("dialog2.png")


    def draw(self, surface):
        if self.blank:
            self.blank = False

            sw, sh = surface.get_size()
            fontSize = int(0.0667 * sh)

            # draw the border
            x, y = 0.0313 * sw, 0.6667 * sh
            w, h = 0.9375 * sw, 0.2917 * sh
            self.border.draw(surface, (x, y, w, h))
           
            fullpath = res.fontPath("dpcomic.ttf")
            font = pygame.font.Font(fullpath, fontSize)

            # adjust the margins of text if there is a title
            if self.title:
                x = 0.0625 * sw
                y = 0.7 * sh

            gui.drawText(surface, self.text, (0,0,0), (x+10,y+8,w-18,h-12),
                         font, aa=1, bkg=self.border.background)
            
            # print the title
            if self.title != None:
                banner = OutlineTextBanner(self.title, (200,200,200),
                                           int(fontSize*1.25), font=self.font)
                title_image = banner.render()
                x, y = 0.4688 * sw, 0.625 * sh
                surface.blit(title_image, (x, y))

            # show arrow
            #x, y = 0.0625 * sw, 0.9167 * sh
            #arrow = res.loadImage("wait_arrow.png", colorkey=1)
            #surface.blit(arrow, (x, y))

            # play a nice sound 
            self.wait_sound.stop()
            self.wait_sound.play()


    def handle_commandlist(self, cmdlist):
        for cls, cmd, arg in cmdlist:
            if arg == BUTTONDOWN and cmd == P1_ACTION1 and not self.blank:
                sd.done()   


class ChoiceDialog(GameState):
    #wrap_width = 58 # font 12
    
    text_size = 14
    wrap_width = 46 
 
    background = (128, 128, 128)

    wait_sound = res.loadSound("select0.wav")
    wait_sound.set_volume(0.20)

    def __init__(self, text, choices, title=None):
        GameState.__init__(self)
        self.text = text
        self.state = 0
        self.counter = 0
        self.title = title
        self.choices = choices

    # when given focus for first time
    def activate(self):
        xsize = 300
        ysize = 70
        bkg = Surface((xsize, ysize))
        bkg.lock()
        bkg.fill((128,128,128))
        for i in range(1, 4):
            draw.rect(bkg,(i*32,i*32,i*32),(4-i,4-i,xsize+(i-4)*2,ysize+(i-4)*2),3)

        corner = (64,64,64)
        bkg.set_at((0,0), corner)
        bkg.set_at((xsize,0), corner)
        bkg.set_at((xsize,ysize), corner)
        bkg.set_at((0,ysize), corner)

        bkg.unlock()

        bkg.set_alpha(64)

        self.bkg = bkg

        if self.title != None:
            banner = OutlineTextBanner(self.title, (200,200,200), 20)
            self.title_image = banner.render()
            self.title_image.set_alpha(96)

        self.arrow = res.loadImage("wait_arrow.png", colorkey=1)

    # when focus is given again
    def reactivate(self):
        pass

    # when losing focus
    def deactivate(self):
        pass

    def draw(self, surface):
        # fade in the dialog box background
        if self.state == 0:
            surface.blit(self.bkg, (10,160))
            self.counter += 1
            if self.counter == 6:
                self.bkg.set_alpha(0)
                self.bkg = self.bkg.convert()
            elif self.counter == 7:
                surface.fill((128,128,128), (14, 146, self.bkg.get_size()))
                print "fill"
                self.counter = 0
                self.state = 1
                self.bkg = None

        # fade in the title, if any
        elif self.state == 1:
            if self.title != None:
                surface.blit(self.title_image, (15,150))
                self.counter += 1
                if self.counter == 3:
                    self.state = 2
                    self.counter = 0
                    self.title_image = None
            else:
                self.state = 2

        # quickly write the text
        elif self.state == 2:
            x = 20

            if self.title != None:
                y = 168
            else:
                y = 167

            for line in wrap(self.text, self.wrap_width):
                banner = TextBanner(line, size=self.text_size)
                surface.blit(banner.render(self.background), (x,y))
                y += banner.font.size(line)[1]

            self.menu = cMenu(Rect((25,210),(280, 30)),
                5, 5, 'horizontal', 10,
                [('Yes', self.yes),
                ('No', self.no)],
                font="fonts/dpcomic.ttf", font_size=16)

            self.menu.ready()
            self.wait_sound.stop()
            self.wait_sound.play()
            self.state = 3

        elif self.state == 3:
            self.menu.draw(surface)

    def handle_event(self, event):
        if self.state > 2:
            self.menu.handle_event(event)

    def handle_commandlist(self, cmdlist):
        for cls, cmd, arg in cmdlist:
            if (cmd == P1_ACTION1) and arg:
                sd.done()   

    def update(self, time):
        pass

    def choice0(self): pass
    def choice1(self): pass
    def choice2(self): pass
    def choice3(self): pass

    def yes(self): sd.done()
    def no(self): sd.done()
