import timeit
import itertools
import copy


flags = 0
use_pygame = 1


if use_pygame:
    import pygame
    pygame.init()
    pygame.display.init()
    screen = pygame.display.set_mode((640,480))

"""
various benchmarks for pygame
"""

def random_image():
    surface = pygame


# faster
def scroll_test(tests=100):
    surface = pygame.surface.Surface((640, 480), flags)
    for i in range(0, tests):
        surface.fill((0,0,0))
        dx = dy = i % 2 + 1
        surface.scroll(dx,dy)

def blit_test(tests=100):
    surface = pygame.surface.Surface((640, 480), flags)
    for i in range(0, tests):
        surface.fill((0,0,0))
        dx = dy = i % 2 + 1
        surface.blit(surface, (dx, dy))


# about 10x slower than non-colorkey blitting
def colorkeyblit_test(tests=100):
    surface = pygame.surface.Surface((640, 480), flags)
    surface.fill((128,128,128))
    #pygame.draw.rect(surface, (0,0,320,320))
    surface.set_colorkey((128,128,127))
    for i in range(0, tests):
        surface.fill((128,128,128))
        #surface.blit(alpha, (0,0))
        screen.blit(surface, (0,0))

# about 3x faster that colorkey blits
def RLEblit_test(tests=100):
    surface = pygame.surface.Surface((640, 480), flags)
    surface.fill((128,128,128))
    #pygame.draw.rect(surface, (0,0,320,320))
    surface.set_colorkey((128,128,128), pygame.RLEACCEL)
    for i in range(0, tests):
        surface.fill((128,128,127))
        #surface.blit(alpha, (0,0))
        screen.blit(surface, (0,0))


# faster
def not_test(tests=10000):
    [ i for i in range(0, 10000) if not i ]

def false_test(tests=10000):
    [ i for i in range(0, 10000) if i == False ]


# faster
def not_equal_test(tests=10000):
    [ i for i in range(0, 10000) if not i == None ]

def ne_equal_test(tests=10000):
    [ i for i in range(0, 10000) if i != None ]


def flat_array_test(tests=10000):
    l = [0] * 10000
    l2d = [0] * 100
    f = lambda x: [ (x[0], i, x[i]) for i in range(len(x)) ]
    t = []

    for x in range(0, 100):
        l2d[x] = [0] * 100

    for x in range(0, 100):
        for y in range(0, 100):
            if l[x+y*100] == 0: t.append((x, y, l[x+y*100]))

def multi_array_test(tests=10000):
    l = [0] * 10000
    l2d = [0] * 100
    f = lambda x: [ (x[0], i, x[i]) for i in range(len(x)) ]
    t = []

    for x in range(0, 100):
        l2d[x] = [0] * 100

    for x in range(0, 100):
        for y in range(0, 100):
            if l2d[x][y] == 0: t.append((x, y, l2d[x][y]))

# faster
def lambda_array_test(tests=10000):
    l = [0] * 10000
    l2d = [0] * 100
    f = lambda x: [ (x[0], i, x[i]) for i in range(len(x)) ]
    t = []

    for x in range(0, 100):
        l2d[x] = [0] * 100

    t = [ f(y) for y in l2d ]

# faster
def create_product_test(tests=10000):
    p = itertools.product(range(0, 100), range(0, 100))

pro = itertools.product(range(0, 100), range(0, 100))
def copy_product_test(tests=10000):
    copy.copy(pro)


print timeit.Timer("colorkeyblit_test()", "from __main__ import colorkeyblit_test").timeit(100)
print timeit.Timer("RLEblit_test()", "from __main__ import RLEblit_test").timeit(100)

#print timeit.Timer("scroll_test()", "from __main__ import scroll_test").timeit(100)
#print timeit.Timer("blit_test()", "from __main__ import blit_test").timeit(100)

#print timeit.Timer("not_test()", "from __main__ import not_test").timeit(5000)
#print timeit.Timer("false_test()", "from __main__ import false_test").timeit(5000)

#print timeit.Timer("not_equal_test()", "from __main__ import not_equal_test").timeit(5000)
#print timeit.Timer("ne_equal_test()", "from __main__ import ne_equal_test").timeit(5000)

#print timeit.Timer("flat_array_test()", "from __main__ import flat_array_test").timeit(5000)
#print timeit.Timer("multi_array_test()", "from __main__ import multi_array_test").timeit(5000)
#print timeit.Timer("lambda_array_test()", "from __main__ import lambda_array_test").timeit(5000)


#print timeit.Timer("create_product_test()", "from __main__ import create_product_test").timeit(5000)
#print timeit.Timer("copy_product_test()", "from __main__ import copy_product_test").timeit(5000)



