import pygame



class Element(object):
    """
    an element must be attached to a frame
    """

    def __init__(self, frame=None):
        self.frame = frame
        self.enabled = False
        self._rect = None

        from lib2d import ui
        if not isinstance(frame, ui.Frame) and frame is not None:
            print self, frame
            raise Exception, "element does not have a frame set"


    @property
    def rect(self):
        if self._rect is not None:
            return self._rect
        msg = "Element: {0} does not have it's rect set.  Crashing."
        raise AttributeError, msg.format(self)


    @rect.setter
    def rect(self, rect):
        self._rect = pygame.Rect(rect)
        self.resize()


    def draw(self, surface):
        print "DEBUG: {} has no draw()".format(self.__class__.__name__)


    def resize(self):
        """ call this in case the class does stuff to resize """
        #print "DEBUG: resizing {0}".format(self)
        pass


    def getUI(self):
        parent = self.parent
        while not isinstance(parent, UserInterface):
            parent = parent.parent
        return parent


    def handle_commandlist(self, cmdlist):
        pass


    def onClick(self, point, button):
        pass


    def onBeginHover(self, point):
        pass


    def onEndHover(self, point):
        pass

