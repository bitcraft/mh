#!/usr/bin/env python

"""
Contains various games/testing modes for MH
"""

import pygame

from lib2d import res, gfx
from lib2d.game import Game


profile = 0

#gfx.set_screen((320, 240))
#gfx.set_screen((320, 240), 2, "scale2x")
#gfx.set_screen((640, 480), 2, "scale")
#gfx.set_screen((640, 480), 3, "scale")
#gfx.set_screen((640, 480))
#gfx.set_screen((800, 600))
#gfx.set_screen((1024, 768))


class CutsceneTest(Game):
    def start(self):
        from lib.cutscene import Cutscene

        gfx.set_screen((640, 480), 2, "scale")
        self.sd.reload_screen()
        self.sd.start(Cutscene(res.miscPath("intro.txt", "scripts")))
        self.sd.run()


class FullGame(Game):
    def start(self):
        gfx.set_screen((800, 600), 3, "scale")
        self.sd.reload_screen()

        from lib.titlescreen import TitleScreen

        self.sd.start(TitleScreen())
        try:
            self.sd.run()
        except:
            pygame.quit()
            raise


class WorldTest(Game):
    def start(self):
        from lib.worldstate import WorldState
        from lib2d.objects import loadObject
        import pygame

        gfx.set_screen((800, 600), 2, "scale")
        self.sd.reload_screen()

        uni = loadObject("mh")
        village = uni.getChildByGUID(1001)
        self.sd.start(WorldState(village))
        try:
            self.sd.run()
            uni.save("mh")
        except:
            pygame.quit()
            raise


if __name__ == "__main__":
    if profile:
        import cProfile
        import pstats

        game = FullGame()
        cProfile.run('game.start()', "results.prof")

        p = pstats.Stats("results.prof")
        p.strip_dirs()
        #p.sort_stats('time').print_stats(20, "^((?!pygame).)*$")
        #p.sort_stats('time').print_stats(20)

    else:
        import buildworld
        #FullGame().start()
        #CutsceneTest().start()
        WorldTest().start()



