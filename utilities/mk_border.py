"""
Chop up an image of a dialog box into tiles
resulting image is smaller that the original and easier to resize
"""

import pygame, os

# for pygame without a window (doesn't work on os x)
#os.environ["SDL_VIDEODRIVER"] = "dummy"



pygame.init()
screen = pygame.display.set_mode((160,80))


def chopIt(filename, tw, th):
    """
    return a list of tiles
    """

    image = pygame.image.load(filename)
    iw, ih = image.get_size()

    nw = pygame.Surface((tw, th))
    ne = pygame.Surface((tw, th))
    se = pygame.Surface((tw, th))
    sw = pygame.Surface((tw, th))
    n = pygame.Surface((tw, th))
    e = pygame.Surface((tw, th))
    s = pygame.Surface((tw, th))
    w = pygame.Surface((tw, th))
    c = pygame.Surface((tw, th))

    nw.blit(image, (0,0), (0,0,tw,th))        
    ne.blit(image, (0,0), (iw-tw,0,tw,th))        
    sw.blit(image, (0,0), (0,ih-th,tw,th))        
    se.blit(image, (0,0), (iw-tw,ih-th,tw,th))
    
    n.blit(image, (0,0), (iw/2-tw/2,0,tw,th))        
    w.blit(image, (0,0), (iw-tw,ih/2-th/2,tw,th))        
    s.blit(image, (0,0), (iw/2-tw/2,ih-th,tw,th))        
    e.blit(image, (0,0), (0,ih/2-th/2,tw,th))        
    
    c.blit(image, (0,0), (iw/2-tw/2, ih/2-th/2, tw,th))

    return [nw, ne, se, sw, n, e, s, w, c]


if __name__ == "__main__":
    import sys

    # make sure there are enough arguments:
    if len(sys.argv) != 5:
        print "USAGE:"
        print "chop.py input output tilewidth tileheight"
        print
        sys.exit()

    i, o, tw, th = sys.argv[1:]
    tw = int(tw)
    th = int(th)
    tiles = chopIt(i, tw, th)

    image = pygame.Surface((9*tw, th))
    for i, tile in enumerate(tiles):
        image.blit(tile, (i*tw, 0))

    pygame.image.save(image, o)
