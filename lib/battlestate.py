"""

combat:
    every party member's spells are available to cast if their cooldown is met.
    when selected, they will have a countdown until the spell is cast
    during the cooldown, the opponent has an oportunity to block your spell

combat:
    each party gets a limited time to select action
    actions will be presented, give other party option to play a counter spell
    actions will be played out on a stack

so, it is turn based, but with some realtime elements
"""

from collections import defaultdict, deque

from pygame import Rect, Surface
import pygame.draw

from lib2d.gui import VisualTimer
from lib2d.gamestate import GameState
from lib2d.cmenu import cMenu
from lib2d.statedriver import driver as sd
from lib2d.banner import TextBanner
import lib2d.gfx as gfx
from mob import Monster
from rpg import Hero


class FadingText(object):
    """
    make a nice display for damage given, hp gained, etc
    """

    speed = .1
    lenght = 2000

    def __init__(self, text, pos, color = (255,255,255), icon = None):
        banner = TextBanner(text, color, 12)

        if icon == None:
            self.image = banner.image
        else:
            icon = pygame.transform.scale(icon, (32, 32))
            r = banner.image.get_rect()
            r.width += 32
            r.height = 32
            self.image = Surface(r.size)
            self.image.set_colorkey((0,0,0))
            self.image.blit(icon, (0,0))
            self.image.blit(banner.image, (32, 0))           
 
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.y = float(pos[1])
        self.time = 0
        self.alive = 1


    def update(self, time):
        if self.alive:
            self.time += time

            if self.time < self.lenght:
                self.y -= self.speed
                self.rect.top = self.y
            else:
                self.alive = 0


    def draw(self, surface):
        if self.alive:
            surface.blit(self.image, self.rect)


class BattleState(GameState):
    """
    This state is used to handle combat between the player and a CPU
    monster.

    The real work is handled by SelectState and StackState.
    """

    def __init__(self, party, enemies):
        GameState.__init__(self)

        self.bkg = gfx.load("misc/overpass.png")
        self.bkg = pygame.transform.scale(self.bkg, (sd.get_size()))

        self.actors = []
        self.glitter = []

        hero = lib2d.sheetloader.load_actor("hero", Hero)
        hero.avatar.play("walk")
        hero.face("north")
        self.actors.append(hero)

        m0 = Monster()
        m0.render()

        m0.rect.topleft = (170, 10)   # hack

        party = [hero]
        enemies = [m0]

        self.timer = VisualTimer(0, (10,30,100,16))
        self.player_area = Rect(160, 140, 160, 78)
        self.party = [party, enemies]
        self.member_focus = 0

        self.stale_spells = []

        # kinda a hack until [if] i properly implement a scheduler for
        # concurrent states
        self.states = []
        self.substate = None


    def win(self):
        """
        Called when the player wins
        """

        sd.replace(WinningState())


    def start(self, state):
        """
        hack!
        """

        self.states.append(state)
        self.substate = self.states[-1]
        self.substate.activate()   
 
    
    def done(self):
        """
        hack!
        """

        self.substate.deactivate()
        self.states.pop()
        self.substate = self.states[-1]
        self.substate.activate()


    def draw(self, surface):
        surface.fill((0,0,0))
        self.substate.draw(surface)
        self.timer.draw(surface)
        surface.blit(self.party[1][0].image, (170,10)) # draw the monster
        [ g.draw(surface) for g in self.glitter ]
        surface.fill((32,32,32), self.player_area)


    def handle_event(self, event):
        self.substate.handle_event(event)


    def activate(self):
        self.start(SelectState(self))


    def update(self, time):
        """
        if another state such as select state is here, make sure they are
        calling this update
        """

        [ i.update(time) for i in self.glitter ]
        [ a.avatar.update(time) for a in self.actors ]
        self.timer.update(time)
        self.glitter = [ i for i in self.glitter if i.alive ]
        self.substate.update(time)


class SelectState(GameState):
    """
    Allow the player to choose action for the battle.

    This game state should be be used with the normal StateDriver
    """

    select_delay = 10000     # how much time you have before you are skipped


    def __init__(self, parent):
        GameState.__init__(self)
        self.stack = deque()
        self.parent = parent
        self.history = defaultdict(int)
        self.last_selection = defaultdict(int)


    def update_spell_card(self, index):
        """
        update the selected spell information

        normally called as a callback from the menu
        """

        s = Surface((240,32))
        spell = self.items[index][2]
        self.render_spell_card(s, spell)
        self.selected_spell = s


    def select_spell(self):
        """
        allow the player to choose the target for a spell
        """

        spell = self.items[self.menu.selection][2]
        caller = self.parent.party[0][self.parent.member_focus]
        target = self.parent.party[1][0]
        self.stack.append((spell, caller, target))
        self.last_selection[caller] = self.menu.selection
        self.history[(caller, self.menu.selection)] += 1

        # HACK
        self.parent.start(StackState(self.parent, self.stack))

    def render_spell_card(self, surface, spell):
        """
        render a spell card on the screen
        """
       
        position = (0, 0) 
        icon = spell.icon
        surface.blit(icon, position)
        rect = icon.get_rect()
        text = TextBanner(spell.description, (255,255,255), size=14)
        text.render()
        position = (rect.width + 8, rect.height - text.rect.height)
        surface.blit(text.image, position)


    def activate(self):
        import spells

        def name(spell):
            if spell.uses >= 1:
                i = loaded_spells.index(spell)
                return "{0} ({1})".format(
                    spell.name,
                    spell.uses - self.history[(caller, i)])

            else:
                return spell.name

        caller = self.parent.party[0][self.parent.member_focus]

        loaded_spells = spells.load("all")

        self.items = [ (name(s), self.select_spell, s) for s in loaded_spells ]
        self.menu = cMenu(Rect((10,60),sd.get_size()),
            20, 0, 'vertical', 100,
            self.items,
            font="fonts/dpcomic.ttf", font_size=16,
            banner_style="normal")

        self.menu.callback = self.update_spell_card

        for i, spell in enumerate(loaded_spells):
            if spell.uses >= 1:
                if self.history[(caller, i)] >= spell.uses:
                    self.menu.disable(i)

        self.menu.ready(self.last_selection[caller])
        self.update_spell_card(self.menu.selection)
        self.parent.timer.set_alarm(self.select_delay)


    def update(self, time):
        if self.parent.timer.finished:
            self.parent.start(StackState(self.parent, self.stack))


    def handle_event(self, event):
        self.menu.handle_event(event)


    def draw(self, surface):

        if not self.selected_spell == None:
            surface.blit(self.selected_spell, (0,208))

        self.menu.draw(surface)


class StackState(GameState):
    """
    Simple state that shows the player spells on the stack
    and processes it

    This game state should be be used with the normal StateDriver
    """

    stack_delay = 1000


    def __init__(self, parent, stack):
        GameState.__init__(self)
        self.parent = parent
        self.stack = stack


    def activate(self):
        self.parent.timer.set_alarm(self.stack_delay)


    def update(self, time):
        if self.parent.timer.finished:
            self.parent.timer.reset()

            try:
                spell, caller, target = self.stack.popleft()
            except IndexError:
                pass
            else:

                spell.cast(caller, target)

                g = FadingText(
                    spell.text,
                    target.rect.center,
                    icon = spell.icon)

                self.parent.glitter.append(g)

                if target.hp <=0 :
                    target.isAlive = False

                if not spell.finished:
                    self.parent.stale_spells.append((spell, caller, target))

                if not [ e for e in self.parent.party[1] if e.isAlive ]:
                    self.parent.win()

            if len(self.stack) == 0:
                [ self.stack.append(i) for i in self.parent.stale_spells ] 
                self.parent.stale_spells = []
                self.parent.done()


class WinningState(GameState):
    """
    State for a win after a battle
    """

    def activate(self):
        sd.done() 
