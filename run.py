from lib2d.client.game import Game
from lib2d.client import gfx
import pygame



class TestGame(Game):
    def start(self):
        from lib.titlescreen import TitleScreen
        gfx.set_screen((640, 480), 2, "scale")
        self.sd.reload_screen()
        self.sd.start(TitleScreen())
        self.sd.run()


if __name__ == "__main__":
    TestGame().start()
    pygame.quit()
