# -*- coding: utf-8 -*-

# Button Constants

# movement
BUTTON_LEFT  = 64
BUTTON_RIGHT = 128
BUTTON_UP    = 256
BUTTON_DOWN  = 512

# for fighting style games
BUTTON_PUNCH     = 7		# don't assign controls to this -- for interal use
BUTTON_LOW_PUNCH = 1
BUTTON_MED_PUNCH = 2
BUTTON_HI_PUNCH  = 4

BUTTON_KICK 	 = 56		# don't assign controls to this -- for interal use
BUTTON_LOW_KICK  = 8
BUTTON_MED_KICK  = 16
BUTTON_HI_KICK   = 32

BUTTON_GUARD = 2048

# virutal
STATE_VIRTUAL = 1024
STATE_FINISHED = 1
FALL_DAMAGE   = 2048



# misc
BUTTON_NULL    = 0			# virtual button to handle state changes w/hold buttons
BUTTON_FORWARD = 4096
BUTTON_BACK    = 8192
BUTTON_PAUSE   = 1024
BUTTON_MENU    = 1024
BUTTON_SELECT  = 4096
MOUSEPOS       = 16384
CLICK1         = 16
CLICK2         = 32
CLICK3         = 64
CLICK4         = 128


BUTTONUP = 1                # after being released
BUTTONHELD = 2              # when button is down for more than one check
BUTTONDOWN = 4              # will only be this value on first check

P1_UP       = 1
P1_DOWN     = 2
P1_LEFT     = 4
P1_RIGHT    = 8
P1_ACTION1  = 16
P1_ACTION2  = 32
P1_ACTION3  = 64
P1_ACTION4  = 128
P1_X_RETURN = 256
P1_Y_RETURN = 512


P2_UP       = 1
P2_DOWN     = 2
P2_LEFT     = 4
P2_RIGHT    = 8
P2_ACTION1  = 16
P2_ACTION2  = 32


KEYNAMES = {1:"up", 2:"down", 4:"left", 8:"right", 16:"action0", 32:"action1"}
