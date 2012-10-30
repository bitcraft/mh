"""
Copyright 2009, 2010, 2011 Leif Theden

This file is part of Fighter Framework.

Fighter Framework (FF) is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

FF is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with FF.  If not, see <http://www.gnu.org/licenses/>.
"""

import autoblocker

from buttons import *
from fsa import FSA, LoggingFSA, STICKY
from pygame.locals import *

class IK_Guy(autoblocker.AutoBlocker):
    defeat_animations = ["fall backward"]

    # A CONTROLLED GAME OBJECT WITH HEALTH BARS, A FSM

    # called to do after things like avatar has been set up

    def reset(self):
        super(IK_Guy, self).reset()
        self.fsa.reset()

    def setup(self):
        super(IK_Guy, self).setup()

        fsa = LoggingFSA(self.avatar)

        # when evualting moves, they are searched in the order inserted

        # basic syntax is:
        # 
        # button            what button triggers the state
        # from state        the animation that is currently played
        # to state          the animation that will play
        # start frame       opt: the frame to begin the new animation
        # condition frame   opt: the frame that current animation must be
        # flags             opt: STICKY=play previous animation after new one

        # position and movement
        fsa.add_transition(BUTTON_FORWARD, "idle", "walk forward")
        fsa.add_transition(BUTTON_BACK, "idle", "walk backward")
        fsa.add_transition(BUTTON_DOWN, "idle", "crouch")

        # normal kicks
        fsa.add_transition(BUTTON_HI_KICK, "idle", "high kick")
        fsa.add_transition(BUTTON_MED_KICK, "idle", "medium kick")
        fsa.add_transition(BUTTON_LOW_KICK, "idle", "low kick")

        # punch
        fsa.add_transition(BUTTON_HI_PUNCH, "idle", "high punch")

        # block
        fsa.add_transition(BUTTON_LOW_PUNCH, "idle", "block")

        # from block cancels
        fsa.add_transition(BUTTON_HI_PUNCH, "block", "high punch")

        # to block cancels
        fsa.add_transition(BUTTON_LOW_PUNCH, "high punch", "block", flags=STICKY)

        # crouch cancels
        fsa.add_transition(BUTTON_DOWN, "low kick", "crouch")
        fsa.add_transition(BUTTON_DOWN, "medium kick", "crouch")
        fsa.add_transition(BUTTON_DOWN, "high kick", "crouch")
        fsa.add_transition(BUTTON_DOWN, "high punch", "crouch")
        fsa.add_transition(BUTTON_DOWN, "walk forward", "crouch")
        fsa.add_transition(BUTTON_DOWN, "walk backward", "crouch")

        # crouch to sweep
        fsa.add_transition(BUTTON_KICK, "crouch", "sweep")

        # sweep to crouch while still holding down
        fsa.add_transition(BUTTON_DOWN, "sweep", "crouch", flags=STICKY)

        # jump
        fsa.add_transition(BUTTON_UP, "idle", "jump")

        # high punch cancel
        fsa.add_transition(BUTTON_HI_PUNCH, "high punch", "high punch")

        # high kick cancel
        fsa.add_transition(BUTTON_HI_KICK, "medium kick", "high kick", 2)
        fsa.add_transition(BUTTON_HI_KICK, "low kick", "high kick", 2)
        # breaking this down into frames prevents "lightning presses"
        #fsa.add_transition(BUTTON_HI_KICK, "high kick", "high kick", 1, 2)
        #fsa.add_transition(BUTTON_HI_KICK, "high kick", "high kick", 3, 3)
        #fsa.add_transition(BUTTON_HI_KICK, "high kick", "high kick", 1, 4)
        fsa.add_transition(BUTTON_HI_KICK, "high kick", "high kick", 1)

        # forward flip to jump kick cancel =)
        fsa.add_transition(BUTTON_KICK, "forward flip", "jump kick", 0, 3)
        fsa.add_transition(BUTTON_KICK, "forward flip", "jump kick", 0, 4)

        # medium kick cancel
        fsa.add_transition(BUTTON_MED_KICK, "high kick", "medium kick", 1)
        fsa.add_transition(BUTTON_MED_KICK, "low kick", "medium kick", 1)
        # breaking this down into frames prevents "lightning presses"
        #fsa.add_transition(BUTTON_MED_KICK, "medium kick", "medium kick", 1, 1)

        #fsa.add_transition(BUTTON_MED_KICK, "medium kick", "medium kick", 2, 2)
        fsa.add_transition(BUTTON_MED_KICK, "medium kick", "medium kick", 1)

        # low kick cancel
        fsa.add_transition(BUTTON_LOW_KICK, "high kick", "low kick")
        fsa.add_transition(BUTTON_LOW_KICK, "medium kick", "low kick")
        fsa.add_transition(BUTTON_LOW_KICK, "low kick", "low kick")

        # jump to jump kick cancel
        fsa.add_transition(BUTTON_KICK, "jump", "jump kick")

        # walk forward for flip
        fsa.add_transition(BUTTON_UP, "walk forward", "forward flip", 1)

        # walk backward for flip
        fsa.add_transition(BUTTON_UP, "walk backward", "backward flip", 1)

        # roundhouse to medium kick cancel
        fsa.add_transition(BUTTON_MED_KICK, "roundhouse", "medium kick", 1, 5)
        fsa.add_transition(BUTTON_MED_KICK, "roundhouse", "medium kick", 1, 6)

        # roundhouse to high kick cancel
        #fsa.add_transition(BUTTON_HI_KICK, "roundhouse", "high kick", 1, 5)
        #fsa.add_transition(BUTTON_HI_KICK, "roundhouse", "high kick", 1, 6)

        # roundhouse combo
        fsa.add_combo("roundhouse", "low kick", "medium kick", "high kick", "high kick")

        # bash button combo
        fsa.add_button_combo("dash forward", 500, BUTTON_FORWARD, BUTTON_FORWARD)
        #fsa.add_button_combo("dash backward", 100, BUTTON_BACKWARD, BUTTON_BACK)

        # "Dash" cancel -- after an attack, allow a dash forward for close range
        fsa.add_transition(BUTTON_FORWARD, "low kick", "dash forward", 0, 2)
        fsa.add_transition(BUTTON_FORWARD, "medium kick", "dash forward", 0, 3)
        fsa.add_transition(BUTTON_FORWARD, "high kick", "dash forward", 0, 3)

        # CRAZY....just a test, not really a useful move
        #fsa.add_combo("crazy", "low kick", "medium kick", "high kick", "low kick")

        self.fsa = fsa
        self.avatar.set_fsa(fsa)

    # given a command, get the state, then play it
    def play_command(self, cmd, pressed):
        state = self.handle_command(cmd, pressed)
        if state != False:
            self.avatar.play(*state)

    # given a command, get the state, then return it without playing it
    def handle_command(self, cmd, pressed):

        # do a little preprocessing to simplfy direction changes
        if self.avatar.facing == 0:
            if cmd == BUTTON_LEFT:
                cmd = BUTTON_FORWARD
            elif cmd == BUTTON_RIGHT:
                cmd = BUTTON_BACK

        # do a little preprocessing to simplfy direction changes
        elif self.avatar.facing == 1:
            if cmd == BUTTON_LEFT:
                cmd = BUTTON_BACK
            elif cmd == BUTTON_RIGHT:
                cmd = BUTTON_FORWARD

        return self.fsa.process(cmd, pressed)
