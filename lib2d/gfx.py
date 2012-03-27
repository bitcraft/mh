from pygame.transform import scale, scale2x
from pygame.display import flip
import pygame, os.path, pprint



"""
a few utilities for making retro looking games by scaling the screen
and providing a few functions for handling screen changes

"""

DEBUG = False

def debug(text):
    if DEBUG: sys.stdout.write(text)


pixelize = None
pix_scale = 1
screen_dim = None
buffer_dim = None
screen = None
screen_surface = None
update_display = None
double_buffer = False
hwsurface = False
surface_flags = 0



def hardware_checks():
    """
    TODO: Do some tests to see if we can reliably use hardware sprites
    """

    pass


def init():
    global screen_dim

    # determine if we can use hardware accelerated surfaces or not
    pygame.display.set_caption("RPG World Test")

# is it redundant to have a pygame buffer, and one for pixalization?  maybe...

def update_display_scaled2x(dirty):
    scale2x(screen, screen_surface)
    flip()

def update_display_scaled(dirty):
    scale(screen, screen_dim, screen_surface)
    flip()

def set_screen(dim, scale=1, transform=None):

    global pixelize, pix_scale, buffer_dim, screen, update_display, screen_surface, screen_dim

    screen_dim = dim

    if transform == "scale2x" or transform == "scale":
        set_scale(scale, transform)

    elif transform == None:
        pixelize = False
        pixel_buffer = None
        pix_scale = 1
        buffer_dim = None
        update_display = flip
        screen_surface = pygame.display.set_mode(screen_dim, surface_flags)
        screen = screen_surface

def set_scale(scale, transform="scale"):
    from pygame.surface import Surface

    global pixelize, pix_scale, buffer_dim, screen, update_display, screen_surface, screen_dim

    if transform == "scale2x":
        pix_scale = 2
        update_display = update_display_scaled2x
    elif transform == "scale":
        pix_scale = scale
        update_display = update_display_scaled

    pixelize = True
    buffer_dim = tuple([ int(i / pix_scale) for i in screen_dim ])
    screen_surface = pygame.display.set_mode(screen_dim, surface_flags)
    screen = Surface(buffer_dim, surface_flags)
    #screen_surface = pygame.display.set_mode(screen_dim)

