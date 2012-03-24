from lib2d import GameState
from lib2d.banner import TextBanner



class LoadingScreen(GameState):
    """
    Class that displays a simple screen to let the player know the game is
    beling loaded in the background.
    """

    def __init__(self, parent):
        self.parent = parent
        self.activated = False


    def activate(self):
        self.blank = True


    def draw(self, surface):
        if blank:
            surface.fill((0,0,0))
            msg = TextBanner("Please wait...", (128, 128, 128), size=18)
            surface.blit(msg.render(alpha=True), (200,210))
            self.blank = False


    def update(self, time):
        self.parent.update(time)

