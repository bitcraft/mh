"""
this module strives to NOT be a replacement for more fucntional gui toolkits.
this is a bare-bones simple gui toolkit for mouse use only.
"""

class UIElement(object):
    def __init__(self, parent):
        self.parent = parent
        self.enabled = False


    def getUI(self):
        parent = self.parent
        while not isinstance(parent, UserInterface):
            parent = parent.parent
        return parent


    def setParent(self, parent):
        self.parent = parent


    def handle_commandlist(self, cmdlist):
        pass


class Pane(object):
    """
    object capable of interacting with the mouse
    """
    pass


class MouseTool(object):
    toole_image = None
    cursor_image = None


    def onClick(self, pane, point, button):
        pass


    def onDrag(self, pane, point, button, origin):
        pass


    def onHover(self, pane, point):
        pass


class GraphicIcon(object):
    """
    Clickable Icon

    TODO: cache the image so it isn't duplicated in memory
    """

    def __init__(self, filename, func, arg=[], kwarg={}, uses=1):
        self.filename = filename
        self.func = (func, arg, kwarg)
        self.uses = uses
        self.image = None
        self.load()


    def load(self):
        if self.image == None:
            self.image = res.loadImage(self.filename)
            self.enabled = True

    def unload(self):
        self.image = None

    def onClick(self, point, button, origin):
        if self.uses > 0 and self.enabled:
            self.func[0](*self.func[1], **self.func[2])
            self.uses -= 1
            if self.uses == 0:
                self.unload()
                self.func = None

    def onDrag(self, point, button, origin):
        pass

    def onHover(self, point):
        pass

    def draw(self, surface, pos):
        surface.blit(self.image, pos)


class RoundMenu(UIElement):
    """
    menu that 'explodes' from a center point and presents a group of menu
    options as a circle of GraphicIcon objects
    """

    def __init__(self, items):
        self.items = []
        for i in items:
            i.load()
            i.enabled = False


    def open(self):
        """ start the animation of the menu """
        self.enabled = True
        for i in self.items:
            i.enabled = False
    
    def draw(self, surface, rect):
        for i, item in enumerate(self.items):
            x = i*32
            y = 10
            item.draw(surface, (x,y))


class PanTool(MouseTool, UIElement):
    def __init__(self, parent):
        MouseTool.__init__(self)
        UIElement.__init__(self, parent)
        self.drag_origin = None


    def load(self):
        self.tool_image = res.loadImage("pantool.png")


    def onClick(self, pane, point, button):
        self.drag_origin = None
        m = testMenu()
        self.getUI().addElement(m)
        self.getUI().setRect(m, (pos, (32, 32)))
        m.open()


    def onDrag(self, pane, point, button, origin):
        if isinstance(pane, ViewPort):
            if self.drag_origin == None:
                x, y = pane.rect.width / 2, pane.rect.height / 2
                self.drag_origin = pane.camera.surfaceToWorld((x, y))

            x, y, z = self.drag_origin
            dy, dx = point[0] - origin[0], point[1] - origin[1]
            pane.camera.center((x-dx, y-dy, z))


class UserInterface(object):
    pass


class StandardUI(UserInterface):
    """
    Standard UI controls mouse interaction, drawing the maps, and UI
    elements such as menus
    """

    height = 20
    color = pygame.Color(196, 207, 214)
    transparent = pygame.Color(1,2,3)

    background = (109, 109, 109)
    foreground = (0, 0, 0)


    def __init__(self):
        self.blank = True
        self.elements = []


    def addElement(self, other):
        other.setParent(self)
        self.elements.append(other)


    def buildInterface(self, rect):
        """
        pass the rect of the screen surface and the interface will be
        proportioned correctly.
        """

        self.msgFont = pygame.font.Font((res.fontPath("volter.ttf")), 9)
        self.border = gui.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = gui.GraphicBox("dialog2.png")
        self.paneManager = None

        x, y, w, h = rect
        w = x+int((w*.30))
        s = pygame.Surface((w, self.height))
        s.fill(self.transparent)
        s.set_colorkey(self.transparent, pygame.RLEACCEL)

        pygame.draw.circle(s, (128,128,128), (self.height, 1), self.height)
        pygame.draw.rect(s, (128, 128, 128), (self.height, 1, w, self.height))

        pygame.draw.circle(s, self.color, (self.height+1, 0), self.height)
        pygame.draw.rect(s, self.color, (self.height+1, 0, w-self.height, self.height))
        
        self.buttonbar = s


    def draw(self, surface):
        print self.elements
        for e in self.elements:
            e.draw(surface)


        if self.blank:
            self.paneManager = PaneManager(self)
            self.blank = False

        x, y, w, h = surface.get_rect()
        back_width = x+int((w*.70))
        self.buildInterface((x, y, w, h))
        surface.blit(self.buttonbar, (x+int(w*.70)+1,0))


    def handle_commandlist(self, cmdlist):
        for e in self.elements:
            e.handle_commandlist(cmdlist)


    def update(self, time):
        [ i.update(time) for i in self.elements ]


def testMenu():
    def func():
        pass

    g = GraphicIcon("grasp.png", func) 
    m = RoundMenu([g, g, g, g])
    return m


class PaneManager(UIElement):
    """
    Handles panes and mouse tools
    """

    drag_sensitivity = 2


    def __init__(self, parent):
        UIElement.__init__(self, parent)
        self.panes = []
        self.areas = []
        self.rect = None

        self.tools = [ PanTool(self) ]

        for tool in self.tools:
            tool.load()

        self.mouse_tool = self.tools[0]

        #mouse hack
        self.drag_origin = None
        self.drag_vp = None


    def addArea(self, area):
        if area not in self.areas:
            self.areas.append(area)
            area.load()

            # load the children
            for child in area.getChildren():
                child.load()

            # load sounds from area
            for filename in area.soundFiles:
                SoundMan.loadSound(filename)

    def _resize(self, rect):
        """ resize the rects for the panes """

        self.rect = pygame.Rect(rect)

        if len(self.panes) == 1:
            self.panes[0].setRect(rect)

        elif len(self.panes) == 2:
            w, h = self.rect.size
            self.panes[0].setRect((0,0,w,h/2))
            self.panes[1].setRect((0,h/2,w,h/2))

        elif len(self.panes) == 3:
            w = self.rect.width / 2
            h = self.rect.height / 2
            rect = self.rect.copy()
            # WARNING!!!! 3 panes does not work

        elif len(self.panes) == 4:
            w = self.rect.width / 2
            h = self.rect.height / 2
            self.panes[0].setRect((0,0,w,h))
            self.panes[1].setRect((w,0,w,h))
            self.panes[2].setRect((0,h,w,h))
            self.panes[3].setRect((w,h,w,h))
 

    def new(self, area, follow=None):
        if area not in self.areas:
            self.addArea(area)

        vp = ViewPort(area)
        self.panes.append(vp)

        # this will cause the rects to be recalculated next draw
        self.rect = None


    def draw(self, surface):
        rect = surface.get_rect()
        if not self.rect == rect:
            self._resize(rect)

        dirty = []
        [ dirty.extend(pane.draw(surface, pane.rect)) for pane in self.panes ]

        #for rect in self.paneManager.getRects():
        #    self.border.draw(surface, rect.inflate(6,6))

        return dirty


    def getRects(self):
        """ return a list of rects that split the viewports """
        return [ pane.rect for pane in self.panes ]


    def update(self, time):
        [ vp.update(time) for vp in self.panes ]
        [ area.update(time) for area in self.areas ]
        

    def findViewport(self, point):
        for vp in self.panes:
            if vp.rect.collidepoint(point):
                return vp


    # handles all mouse interaction
    def handle_commandlist(self, cmdlist):
        for cls, cmd, arg in cmdlist:
            if cmd == CLICK1:
                state, pos = arg
                vp = self.findViewport(pos)
                if vp:
                    pos = Vec2d(pos[0] - vp.rect.left, pos[1] - vp.rect.top)
                    if state == BUTTONDOWN:
                        self.drag_origin = pos
                        self.drag_vp = vp
                        self.mouse_tool.onClick(vp, pos, 1)

                    elif state == BUTTONHELD:
                        d = abs(sum(pos - self.drag_origin))
                        if vp == self.drag_vp and d > self.drag_sensitivity:
                            self.mouse_tool.onDrag(vp, pos, 1, self.drag_origin)

            elif cmd == CLICK2:
                pass
            elif cmd == MOUSEPOS:
                vp = self.findViewport(arg)
                if vp:
                    pos = (arg[0] - vp.rect.left, arg[1] - vp.rect.top)
                    self.mouse_tool.onHover(vp, pos)


class ViewPort(Pane):
    """
    the ViewPort is a Pane that draws a the area to the screen (or other
    surface)
    """

    def __init__(self, area):
        self.area = area
        self.rect = None
        self.camera = None


    def setRect(self, rect):
        self._resize(rect)


    def _resize(self, rect):
        self.rect = pygame.Rect(rect)
        self.camera = LevelCamera(self.area, self.rect)


    def draw(self, surface, rect):
        if not self.rect == rect:
            self._resize(rect)
            self.camera.draw(surface, self.rect)
            return self.rect
            
        else:
            return self.camera.draw(surface, self.rect)


    def update(self, time):
        self.camera.update(time)


