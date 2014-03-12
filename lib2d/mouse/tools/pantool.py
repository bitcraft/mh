import pygame

from lib2d.ui import Element, VirtualMapElement, VirtualAvatarElement
from lib2d.ui import GraphicIcon, RoundMenu
from lib2d.image import Image, ImageTile
from lib2d.mouse.tools.mousetool import MouseTool
from lib2d import res


def buildActionMenu(element):
    actions = element.avatar.queryActions(None)
    if actions:
        icons = [GraphicIcon(element.frame, a.icon, None) for a in actions]
        menu = RoundMenu(element.frame, element)
        menu.setIcons(icons)
        return menu
    else:
        return None


class PanTool(MouseTool, Element):
    def __init__(self, frame):
        MouseTool.__init__(self)
        Element.__init__(self, frame)
        self.drag_origin = None
        self.openMenu = None
        self.focus_element = None
        self.element_icon = None


    def load(self):
        self.tool_image = res.loadImage("pantool.png")


    def onClick(self, element, point, button):

        if self.focus_element is None:
            if isinstance(element, VirtualMapElement):
                if self.openMenu: self.openMenu.close()

                self.openMenu = testMenu(element)
                self.openMenu.open(point)

            # CLICKED ON AN ENTITY ELEMENT
            elif isinstance(element, VirtualAvatarElement):
                if self.openMenu: self.openMenu.close()
                self.onSelectElement(element)
                menu = buildActionMenu(element)
                if menu:
                    self.openMenu = menu
                    self.openMenu.open(point)

            else:
                element.onClick(point, button)

        # THERE IS AN ENTITY FOCUSED
        else:
            if isinstance(element, VirtualMapElement):
                if self.openMenu: self.openMenu.close()

                self.openMenu = movementMenu(element, self.focus_element)
                self.openMenu.open(point)
                self.onSelectElement(None)  # clear the focus

            else:
                self.onSelectElement(None)  # clear the focus

    def onSelectElement(self, element=None):
        self.focus_element = element

        if self.element_icon:
            self.frame.removeElement(self.element_icon)
            self.element_icon = None

        if element:
            w, h = self.frame.rect.size
            icon = GraphicIcon(element.frame, element.avatar.faceImage, None)
            icon.rect = pygame.Rect(w - 32, 0, 32, 32)
            icon.load()
            element.frame.addElement(icon)
            self.element_icon = icon

    def onDrag(self, element, point, button, origin):
        if isinstance(element, VirtualMapElement):
            if not origin == self.drag_origin:
                self.drag_origin = origin
                self.drag_initial_center = element.camera.extent.center

            dx, dy = point - origin
            cx, cy = self.drag_initial_center
            element.camera.center((cx - dy, cy - dx, 0))


def movementMenu(element, target):
    def closer(icon):
        icon.frame.removeElement(icon)
        icon.unload()

    def func(menu):
        menu.close()

        camera = menu.element.camera
        body = camera.area.getBody(target.avatar)
        endpoint = camera.surfaceToWorld(menu.anchor)
        path = camera.area.pathfind(body.bbox.bottomcenter, endpoint)

        #s = area.MovementSentinal(body, path)
        #camera.area.add(s)

        image = Image("path.png")

        for node in path:
            y, x = node
            icon = GraphicIcon(element.frame, image, closer)
            icon.load()
            icon.rect = pygame.Rect(x * 16, y * 16, 16, 16)
            menu.frame.addElement(icon)

    image = ImageTile("spellicons.png", tile=(20, 3), tilesize=(32, 32))

    m = RoundMenu(element.frame, element)
    a = GraphicIcon(element.frame, image, func, [m])
    m.setIcons([a])
    return m


def testMenu(element):
    def func(menu):
        import lib.blacksmith as b

        menu.close()

        anvil = b.Anvil()
        anvil.loadAll()
        pos = menu.element.camera.surfaceToWorld(menu.anchor) - (16, 16, 0)
        menu.element.camera.area.add(anvil)
        menu.element.camera.area.setPosition(anvil, pos)

    image = Image("grasp.png")

    m = RoundMenu(element.frame, element)
    a = GraphicIcon(element.frame, image, func, [m])
    b = GraphicIcon(element.frame, image, func, [m])
    c = GraphicIcon(element.frame, image, func, [m])
    d = GraphicIcon(element.frame, image, func, [m])
    m.setIcons([a, b, c, d])
    return m
