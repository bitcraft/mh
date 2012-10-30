"""
Copyright 2009, 2010, 2011 Leif Theden

This file is part of lib2d.

lib2d is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

lib2d is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with lib2d.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
modified state machine.  controls player input

output an animation if input is valid

usage:
    add states and transitions

when input is recv'd, call process with the input

check the avatar's state
determin if we can continue
return animation if ok, else return False

internal state should generally match the avatar.

lazy internal state.  ie: don't really spend too much trying to keep in sync
w/avatar.  just check it as needed.

state = (animation object, current frame)
"""

from lib2d.buttons import *
from collections import deque


# only have one child, an avatar.
class fsa(object):
    """
    Somewhat like a finite state machine.

    """

    def __init__(self, entity):
        self.entity = entity
        self.combos = {}
        self.button_combos = []
        self.state_transitions = {}

        self.move_history = []
        self.button_history = []
        self.time = 0
        self.holds = {}                 # keep track of state changes from holds

        self.stack = []


    def program(self):
        pass

    def primestack(self):
        pass


    def reset(self):
        self.time = 0
        self.stack = []
        self.holds = {}
        self.move_history = []


    # sticky means the avartar should finish the previous animation
    # used for stances, (crouch to sweep, block to punch, etc)
    def add_transition(self, trigger0, state0, state1, trigger1=None):
        """
        add new "transition".
        """

        self.state_transitions[(trigger0, state0)] = (state1, trigger1)
    at = add_transition


    def add_button_combo(self, animation, timeout, *buttons):
        """
        add a new button combo.

        button combos are executed when a series of buttons are pressed quickly.
        timeout specifies a limit on the time allowed between each button press
        """

        pass


    def add_combo(self, animation, *combo):
        """
        add a new animation combo.

        a combo is a list of animations.  if it matches the command history,
        then execute another animation.

        command history is cleared each time the fighter idles, so it is safe
        to assume that the command sequence starts from an idle
        """

        pass


    def set_default_transition(self, t):
        pass


    def get_transition(self, trigger, state):
        if state == None:
            raise Exception

        else:
            try:
                return self.state_transitions[(trigger, state)]
            except KeyError:
                return None


    def eject(self, cls):
        """
        remove any instances of cls in the stack
        """
        to_remove = [i for i in self.stack if isinstance(i, cls)]
        [self.stack.remove(i) for i in to_remove]
   
 
    def change_state(self, state, cmd=None):
        old_state = None
        if len(self.stack) > 0:
            if not self.stack[-1].flags & STICKY == STICKY:
                old_state = self.stack.pop()

        new_state = state(self, self.entity)

        [self.eject(unworthy) for unworthy in new_state.forbidden]

        self.stack.append(new_state)
        new_state.enter(cmd)

        if old_state:
            old_state.exit(cmd)


    def process(self, trigger):
        cls, cmd, arg = trigger

        state=self.get_transition((cmd, arg), self.stack[-1].__class__)
        if not state == None:
            self.change_state(state[0], (cmd, arg))
            if not state[1] == None:
                self.holds[state[1]] = (self.stack[-1], state, (cmd, arg))

        try:
            del self.holds[(cmd, arg)]
        except:
            pass


    @property
    def current_state(self):
        return self.stack[-1]


    def update(self, time):
        self.time += time
        [ i.update(time) for i in self.stack ]

        ok = True
        for trigger, candidate_state in self.holds.items():
            if candidate_state[0].__class__ in [i.__class__ for i in self.stack]:
                ok = False
                break

            for running_state in self.stack:
                if candidate_state[0].__class__ in running_state.forbidden:
                    ok = False
                    break

            if ok:
                self.change_state(candidate_state[1][0], candidate_state[2])
