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
"""

from lib2d.buttons import *
from flags import *
from collections import deque, namedtuple


DEBUG = False

def debug(message):
    if DEBUG: print message

class Stack(list):
    def eject(self, cls):
        """
        remove any instances of cls in the stack
        """
        to_remove = [i for i in self if isinstance(i, cls)]
        [self.remove(i) for i in to_remove]


Trigger = namedtuple('Trigger', 'owner, cmd, arg')
Condition = namedtuple('Condition', 'trigger, state')
Transition = namedtuple('Transition', 'func, alt_trigger, flags')
#Event = namedtuple('Event', 'command, arg')


# only have one child, an avatar.
class fsa(object):
    """
    Somewhat like a finite state machine.
    each 'state' is actually a stack
    there is a stack of stacks
    allows for concurency
    """

    def __init__(self, entity):
        self.entity = entity

        self.state_transitions = {}
        self.combos = {}
        self.button_combos = []
        self.move_history = []
        self.button_history = []
        self.holds = {}         # keep track of state changes from holds
        self.hold = 0           # keep track of buttons held down
        self.time = 0
        self.all_stacks = [[]]


    def setup(self):
        pass


    def add_transition(self, trigger, state, func, alt_trigger=None, flags=0):
        """
        add new "transition".
        """

        c = Condition(trigger, state)
        t = Transition(func, alt_trigger, flags)

        self.state_transitions[c] = t

    # shorthand for adding transitions
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


    # remove a state instance from the current stack
    def eject(self, state, cmd=None, terminate=True):
        if terminate:
            state.terminate(cmd)

        changed = False
        to_remove = None
        for stack in self.all_stacks:
            try:
                stack.remove(state)
            except ValueError:
                pass
            else:
                changed = True
                if len(stack) == 0:
                    to_remove = stack
                break

        if changed:
            self.all_stacks.remove(to_remove)
            self.current_state.enter(cmd)


    def get_transition(self, trigger, state=None):
        if state == None:
            state = self.current_state.__class__

        #print trigger
        #print self.state_transitions.keys()

        try:
            return self.state_transitions[(trigger, state)]
        except KeyError:
            return None


    def new_stack(self):
        self.all_stacks.append([])


    def push_state(self, new_state, cmd=None, queue=False):
        debug("pushing {} {} {}".format(self, new_state, cmd))

        old_state = None
        if len(self.current_stack) > 0:
            old_state = self.current_stack[-1]

        #[self.stack.eject(unworthy) for unworthy in new_state.forbidden]

        if queue:
            self.all_stacks.insert(-1, [new_state])
        else:
            if not len(self.current_stack) == 0:
                self.new_stack()
            self.current_stack.append(new_state)

        new_state.enter(cmd)

        if old_state:
            old_state.exit(cmd)

        return new_state


    def process(self, trigger):
        transition = self.get_transition(trigger)

        debug("=========== processing {} {}".format(trigger, transition))

        if transition is not None:
            new_state = transition.func(self, self.entity)

            if new_state is not None:
                # allow for state 'self canceling':
                # state can be stopped and replaced with new instance
                #existing = [stack for stack in self.all_stacks
                #            if new_state.__class__ in [i.__class__ for i in stack]]

                # BREAK flag cancels the current state and ignores of transitions
                if transition.flags & BREAK == BREAK:
                    self.eject(self.current_state, terminate=False)

                if transition.flags & STUBBORN == STUBBORN:
                    self.current_state.enter(trigger)

                else:

                    # queued transitions are placed before the current state
                    self.push_state(new_state, trigger,
                        queue=transition.flags & QUEUED == QUEUED)

                    # support 'toggled' transitions
                    if transition.alt_trigger is not None:
                        self.holds[transition.alt_trigger] = (new_state, transition, trigger)

        self.remove_holds(trigger)

        debug("\nSTACKS: {}".format(self.all_stacks))
        #print "\nSTACKS: {}".format(self.all_stacks)


    def remove_holds(self, trigger):
        try:
            state = self.holds[trigger][0]
        except:
            pass
        else:
            del self.holds[trigger]
            self.eject(state)


    @property
    def current_stack(self):
        return self.all_stacks[-1]

    @property
    def current_state(self):
        return self.current_stack[-1]


    def update(self, time):
        self.time += time
        [ i.update(time) for i in self.current_stack ]

