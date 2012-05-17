from lib2d.client.gamestate import GameState
from lib2d.client.banner import TextBanner
from lib2d.client.statedriver import driver as sd



class WaitScreen(GameState):
    """
    Use this state when you have a task to complete in the background that
    could take a long time to finish.  When task is finished, the state will
    finish and and return to the previous state.  This will block during the
    update method until the task is finished.
    """

    def __init__(self, func, arg=[], kwarg={}):
        GameState.__init__(self)
        self.func = func
        self.arg = arg
        self.kwarg = kwarg
        self.redraw = True
        self.drawn = False


    def update(self, time):
        if self.drawn:
            self.func(*self.arg, **self.kwarg)
            sd.done()


    def draw(self, surface):
        if self.redraw:
            surface.fill((0,0,0))
            msg = TextBanner("Please wait...", (128, 128, 128), size=10)
            surface.blit(msg.render(alpha=True), (140,140))
            self.drawn = True


