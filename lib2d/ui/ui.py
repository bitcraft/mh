"""
the mouse api is generally as follows:

if the client has a onClick, onHover, or onDrag method, the
'point' argument will be relative to the rect of the object,
not the screen.  The point passed will be a vec.Vec2d object

"""

"""
this module strives to NOT be a replacement for more fucntional draw toolkits.
this is a bare-bones simple draw toolkit for mouse use only.
"""

from lib2d.ui.packer import GridPacker
from lib2d.ui import Element, Frame
from lib2d.buttons import *
from lib2d import res, draw, vec
import pygame, itertools



class GraphicIcon(Element):
    """
    Clickable Icon

    TODO: cache the image so it isn't duplicated in memory
    """

    def __init__(self, frame, image, func, arg=[], kwarg={}, uses=1):
        Element.__init__(self, frame)
        if arg == []: arg = [self]
        self.func = (func, arg, kwarg)
        self.uses = uses
        self._image = image
        self.image = None

    def load(self):
        surface = self._image.load()
        self.originalImage = pygame.transform.scale(surface, (16, 16))
        self.image = self.originalImage.copy()
        self.enabled = True

    def unload(self):
        self.image = None
        self.func = None
        self.enabled = False

    def onClick(self, point, button):
        if self.uses > 0 and self.enabled:
            self.func[0](*self.func[1], **self.func[2])
            self.uses -= 1
            if self.uses == 0:
                self.unload()

    def onDrag(self, point, button, origin):
        pass

    def onBeginHover(self, point):
        self.image.fill((96,96,96), special_flags=pygame.BLEND_ADD)

    def onEndHover(self, point):
        self.image = self.originalImage.copy()

    def draw(self, surface):
        if self.image is None:
            raise Exception, "Image is not loaded, cannot be drawn"
        return surface.blit(self.image, self.rect)


class RoundMenu(Element):
    """
    menu that 'explodes' from a center point and presents a group of menu
    options as a circle of GraphicIcon objects
    """

    def __init__(self, frame, element=None):
        Element.__init__(self, frame)
        self.element = element
        self.icons = []
        self.anchor = None

    def setIcons(self, icons):
        self.icons = icons
        for i in icons:
            i.load()

    def open(self, point):
        """ start the animation of the menu """
        self.enabled = True
        self.anchor = point + self.element.rect.topleft
        tw, th = self.icons[0].image.get_size()
        w = tw * len(self.icons)
        rect = pygame.Rect(self.anchor-(w/2,8), (tw, th))
        for i, icon in enumerate(self.icons):
            icon.rect = rect.move(tw*i, 0)
            self.frame.addElement(icon)

    def close(self):
        self.enabled = False
        for i in self.icons:
            i.unload()
            self.frame.removeElement(i)


class UserInterface(Frame):
    """
    Standard UI controls mouse interaction, drawing the maps, and UI
    elements such as menus
    """

    height = 20
    color = pygame.Color(196, 207, 214)
    transparent = pygame.Color(1,2,3)

    background = (109, 109, 109)
    foreground = (0, 0, 0)

    drag_sensitivity = 2

    def __init__(self):
        from lib2d.mouse.tools import PanTool

        self.blank = True
        self.packer = GridPacker()

        self.tools = [ PanTool(self) ]
        for tool in self.tools:
            tool.load()

        self.mouseTool = self.tools[0]

        #mouse hack
        self.drag_origin = None
        self.drag_element = None
        self.hovered = None


    def buildInterface(self, rect):
        """
        pass the rect of the screen surface and the interface will be
        proportioned correctly.
        """

        self.msgFont = pygame.font.Font((res.fontPath("volter.ttf")), 9)
        self.border = draw.GraphicBox("dialog2-h.png", hollow=True)
        self.borderFilled = draw.GraphicBox("dialog2.png")
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
        Frame.draw(self, surface)

        return

        x, y, w, h = self.rect
        back_width = x+int((w*.70))
        self.buildInterface((x, y, w, h))
        surface.blit(self.buttonbar, (x+int(w*.70)+1,0))


    def handle_commandlist(self, cmdlist):
        for e in self.packer.getElements():
            e.handle_commandlist(cmdlist)


    def findElement(self, point):
        """
        return a clicked element, ignoring frames
        """

        def searchPacker(packer):
            layout = list(packer.elements)
            while layout:
                element = layout.pop()
                if element.rect.collidepoint(point):
                    if isinstance(element, Frame):
                        layout.extend(element.packer.elements)
                    else:
                        return element

            return None


        element = searchPacker(self.packer)
        if element:
            return element
        else:
            return None


    # handles all mouse interaction
    def handle_commandlist(self, cmdlist):
        for cls, cmd, arg in cmdlist:
            if cmd == CLICK1:
                state, pos = arg
                if pos is None: return
                el = self.findElement(pos)
                if el:
                    pos = vec.Vec2d((pos[0] - el.rect.left, pos[1] - el.rect.top))
                    if state == BUTTONDOWN:
                        self.drag_origin = pos
                        self.drag_element = el

                    elif state == BUTTONUP:
                        d = abs(sum(pos - self.drag_origin))
                        if d < self.drag_sensitivity:
                            self.mouseTool.onClick(el, pos, 1)

                    elif state == BUTTONHELD:
                        d = abs(sum(pos - self.drag_origin))
                        if el == self.drag_element and d > self.drag_sensitivity:
                            self.mouseTool.onDrag(el, pos, 1, self.drag_origin)

            elif cmd == CLICK2:
                pass

            elif cmd == MOUSEPOS:
                el = self.findElement(arg)
                if el and not self.hovered:
                    pos = vec.Vec2d((arg[0] - el.rect.left, arg[1] - el.rect.top))
                    self.mouseTool.onBeginHover(el, pos)
                    self.hovered = el

                if (not el == self.hovered) and (el is not None):
                    pos = vec.Vec2d((arg[0] - el.rect.left, arg[1] - el.rect.top))
                    self.hovered.onEndHover(pos)
                    self.hovered = None


class VirtualAvatarElement(Element):
    def __init__(self, frame, avatar):
        Element.__init__(self, frame)
        self.avatar = avatar

    def draw(self, surface):
        #pygame.draw.rect(surface, (0,255,0,64), self.rect, 1)
        pass

    def onClick(self, point, button):
        print "clicked", self.avatar


class VirtualMapElement(Element):
    def __init__(self, frame, camera):
        Element.__init__(self, frame)
        self.camera = camera
        self.oldExtent = camera.extent.copy()
        self.virtualElements = {}


    def draw(self, surface):
        if not self.camera.extent == self.oldExtent:
            dy = self.camera.extent.left - self.oldExtent.left
            dx = self.camera.extent.top - self.oldExtent.top
            self.shift((-dx, -dy))
            self.oldExtent = self.camera.extent.copy()
                
        self.camera.draw(surface, self.rect)


    def onClick(self, point, button):
        print "clicked", self.viewport
        

    def shift(self, (x, y)):
        self.frame.shift((x, y))


class ScrollingGridPacker(GridPacker):
    def shift(self, (x, y)):
        for element in self.elements:
            if not isinstance(element, VirtualMapElement):
                element.rect = element.rect.move(x, y)


class ViewPort(Frame):
    """
    the ViewPort is a Frame that draws an area to the screen (or other surface)
    
    Elements can be added to the pane and expect to be loacated in world
    coordinates (so elements move with the map when scrolled)
    """

    loadedAreas = []


    def __init__(self, frame, area):
        Frame.__init__(self, frame, ScrollingGridPacker())
        self.area = area
        self.map_element = None

        if area not in self.loadedAreas:
            self.loadedAreas.append(area)
            area.loadAll()

            # load sounds from area
            #for filename in element.area.soundFiles:
            #    SoundMan.loadSound(filename)


    def shift(self, (x, y)):
        self.packer.shift((x, y))


    def resize(self):
        Frame.resize(self)

        from lib.renderer import LevelCamera

        camera = LevelCamera(self, self.area, self.rect)

        if self.map_element is not None:
            self.packer.remove(self.map_element)

        self.map_element = VirtualMapElement(self, camera)
        self.map_element.rect = self.rect
        self.packer.add(self.map_element)

        self.camera = camera
