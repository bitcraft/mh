import gfx
from signals import *
from playerinput import KeyboardPlayerInput

import pygame
from collections import deque
from itertools import cycle, islice
from pygame.locals import *


"""
player's input doesn't get checked every loop.  it is checked
every 15ms and then handled.  this prevents the game logic
from dealing with input too often and slowing down rendering.
"""


inputs = []
inputs.append(KeyboardPlayerInput())


def flush_cmds(cmds):
    pass


class StatePlaceholder(object):
    """
    holds a ref to a state

    when found in the queue, will be instanced
    """

    def __init__(self, klass):
        self.klass = klass

    def activate(self):
        pass

    def deactivate(self):
        pass


class StateDriver(object):
    """
    A state driver controls what is displayed and where input goes.

    A state is a logical way to break up "modes" of use for a game.
    For example, a title screen, options screen, normal play, pause,
    etc.
    """

    def __init__(self, parent=None):
        self.parent = parent
        self._states = deque()

        if parent != None:
            self.reload_screen()


    def get_size(self):
        """
        Return the size of the surface that is being drawn on.

        * This may differ from the size of the window or screen if the display
        is set to scale.
        """

        return self.parent.get_screen().get_size()


    def get_screen(self):
        """
        Return the surface that is being drawn to.

        * This may not be the pygame display surface
        """

        return self.parent.get_screen()


    def reload_screen(self):
        """
        Called when the display changes mode.
        """

        self._screen = self.parent.get_screen()


    def set_parent(self, parent):
        self.parent = parent
        self.reload_screen()


    def done(self):
        """
        deactivate the current state and activate the next state, if any
        """

        self.getCurrentState().deactivate()
        self._states.pop()
        state = self.getCurrentState()

        if isinstance(state, StatePlaceholder):
            self.replace(state.klass())
           
        elif not state == None:
            if state.activated:
                state.reactivate()
            else:
                state.activate()

    def getCurrentState(self):
        try:
            return self._states[-1]
        except:
            return None


    def replace(self, state):
        """
        start a new state and deactivate the current one
        """

        self.getCurrentState().deactivate()
        self._states.pop()
        self.start(state)


    def start(self, state):
        """
        start a new state and hold the current state.

        when the new state finishes, the previous one will continue
        where it was left off.

        idea: the old state could be pickled and stored to disk.
        """

        self._states.append(state)
        self.getCurrentState().activate()
        self.getCurrentState().activated = True


    def start_restart(self, state):
        """
        start a new state and hold the current state.

        the current state will be terminated and a placeholder will be
        placed on the stack.  when the new state finishes, the previous
        state will be re-instanced.  this can be used to conserve memory.
        """

        prev = self.getCurrentState()
        prev.deactivate()
        self._states.pop()
        self._states.append(StatePlaceholder(prev.__class__))
        self.start(state)


    def push(self, state):
        self._states.appendleft(state)


    def roundrobin(*iterables):
        """
        create a new schedule for concurrent states
        roundrobin('ABC', 'D', 'EF') --> A D E B F C

        Recipe credited to George Sakkis
        """

        pending = len(iterables)
        nexts = cycle(iter(it).next for it in iterables)
        while pending:
            try:
                for next in nexts:
                    yield next()
            except StopIteration:
                pending -= 1
                nexts = cycle(islice(nexts, pending))


    def tick(self, time):
        """
        send a tick to the game world
        send the amount of time to simulate
        """

        timeSignal.send(sender=self, time=time)


    def run(self):
        """
        run the state driver.
        """

        # deref for speed
        event_poll = pygame.event.poll
        event_pump = pygame.event.pump
        current_state = self.getCurrentState
        clock = pygame.time.Clock()

        # streamline event processing by filtering out stuff we won't use
        pygame.event.set_allowed(None)
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

        # set an event to flush out commands
        event_flush = pygame.USEREVENT
        pygame.time.set_timer(pygame.USEREVENT, 30)

        # make sure our custom events will be triggered
        pygame.event.set_allowed([event_flush])

        # some stuff to handle the command queue
        rawcmds = 0
        cmdlist = []
        checkedcmds = []
        
        currentState = current_state()
        while currentState:
            time = clock.tick(20)

            event = event_poll()
            while event:

                # check each input for something interesting
                for cmd in [ c.getCommand(event) for c in inputs ]:
                    rawcmds += 1
                    if (cmd != None) and (cmd[:2] not in checkedcmds):
                        checkedcmds.append(cmd[:2])
                        cmdlist.append(cmd)

                # we should quit
                if event.type == QUIT:
                    currentState = None
                    break

                # do we flush input now?
                elif event.type == pygame.USEREVENT:
                    currentState.handle_commandlist(cmdlist)
                    [ currentState.handle_commandlist(i.getHeld())
                    for i in inputs ]
                    rawcmds = 0
                    checkedcmds = []
                    cmdlist = []

                # back out of this state, or send event to the state
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.done()
                        break
                    else:
                        currentState.handle_event(event)
                else:
                    currentState.handle_event(event)

                event = event_poll()

            originalState = current_state()
            currentState = originalState

            if currentState:
                time = time / 4.0

                self.tick(time)
                currentState = current_state()
                if not currentState == originalState: continue

                self.tick(time)
                currentState = current_state()
                if not currentState == originalState: continue

                self.tick(time)
                currentState = current_state()
                if not currentState == originalState: continue

                self.tick(time)
                currentState = current_state()
                if not currentState == originalState: continue

                dirty = currentState.draw(self._screen)
                gfx.update_display(dirty)


# singleton type object
# use this instead of instancing your own State Driver.
driver = StateDriver()
