from pygame.locals import *
from buttons import *
import pygame


"""
this provides an abstraction between pygame's input's and
input handling.  events will be translated into a format
that the game will handle.  this provides an way to deal
with multiple inputs and reconfiguring keys at runtime.

provides a couple nice features:
    input can be reconfigured during runtime, without chaning game code
    inputs can be changed during runtime: want a joystick, no problem
    input commands keep track of buttons being held, as well
"""



get_pressed = pygame.key.get_pressed


class PlayerInput:
    def getCommand(self, event):
        raise NotImplementedError

    def getHeld(self):
        pass


class KeyboardPlayerInput(PlayerInput):
    default_p1 = {
                  K_UP: P1_UP,
                  K_DOWN: P1_DOWN,
                  K_LEFT: P1_LEFT,
                  K_RIGHT: P1_RIGHT,
                  K_q: P1_ACTION1,
                  K_w: P1_ACTION2,
                  K_e: P1_ACTION3,
                  K_r: P1_ACTION4}
    
    default_p2 = {
                  K_w: P2_UP,
                  K_s: P2_DOWN,
                  K_a: P2_LEFT,
                  K_d: P2_RIGHT,
                  K_r: P2_ACTION1,
                  K_t: P2_ACTION2}
    
    def __init__(self, keymap=None):

        if keymap == None:
            self.keymap = KeyboardPlayerInput.default_p1
        self.rev_keymap = dict((v,k) for k, v in self.keymap.iteritems())
        self.held = []


    def getHeld(self):
        """
        return a list of keys that are being held down
        """

        return [ (self.__class__, key, BUTTONHELD) for key in self.held ]

    
    def getCommand(self, event):

        try:
            key = self.keymap[event.key]
        except (KeyError, AttributeError):
            return None

        if event.type == KEYDOWN:
            if event.key in self.held:
                state = BUTTONHELD
            else:
                state = BUTTONDOWN
                self.held.append(key)

        elif event.type == KEYUP:
            state = BUTTONUP
            try:
                self.held.remove(key)
            except:
                pass

            if ( key == P1_LEFT):
                if self.rev_keymap[P1_RIGHT] in self.held:
                    return self.__class__, P1_RIGHT, BUTTONDOWN
                
            if ( key == P1_RIGHT):
                if self.rev_keymap[P1_LEFT] in self.held:
                    return self.__class__, P1_LEFT, BUTTONDOWN
                    
            if ( key == P1_UP):
                if self.rev_keymap[P1_DOWN] in self.held:
                    return self.__class__, P1_DOWN, BUTTONDOWN   
      
            if ( key == P1_DOWN):
                if self.rev_keymap[P1_UP] in self.held:
                    return self.__class__, P1_UP, BUTTONDOWN
                        
        return self.__class__, key, state



class JoystickPlayerInput(PlayerInput):
    default_p1 = {
                  None: P1_UP,
                  None: P1_DOWN,
                  None: P1_LEFT,
                  None: P1_RIGHT,
                  13: P1_ACTION1,
                  14: P1_ACTION2}

    def __init__(self, keymap=None):
        # make sure pygame's joystick stuff is up
        pygame.joystick.init()
        self.jsNumber = 0
        self.js = pygame.joystick.Joystick(self.jsNumber)
        self.js.init()
        self.deadzone = float(0.12)
        
        if keymap == None:
            self.keymap = JoystickPlayerInput.default_p1
        
    def getCommand(self, event):
        try:
            if event.joy != self.jsNumber: return
        except AttributeError:
            return
        
        if event.type == JOYAXISMOTION:
            # left - right axis
            if event.axis == 0:
                if abs(event.value) > self.deadzone:
                    v = abs(event.value) + self.deadzone
                    if v > 1: v = 1.0

                    if event.value < 0:
                        return self.__class__, P1_LEFT, v
                    else:
                        return self.__class__, P1_RIGHT, v
                else:
                    return self.__class__, P1_LEFT, 0.0
                
            # up - down axis
            if event.axis == 1:
                if abs(event.value) > self.deadzone:
                    v = abs(event.value) + self.deadzone
                    if v > 1.0: v = 1.0
                    
                    if event.value < 0:
                        return self.__class__, P1_UP, v
                    else:
                        return self.__class__, P1_DOWN, v
                else:
                    return self.__class__, P1_UP, 0.0

        elif event.type == JOYBUTTONDOWN:
            try:
                return self.__class__, self.keymap[event.button], 1.0
            except KeyError:
                pass
            
        elif event.type == JOYBUTTONUP:
            try:
                return self.__class__, self.keymap[event.button], 0.0
            except KeyError:
                pass
            
