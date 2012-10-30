class MouseTool(object):
    toole_image = None
    cursor_image = None


    def onClick(self, element, point, button):
        pass


    def onDrag(self, element, point, button, origin):
        pass


    def onBeginHover(self, element, point):
        element.onBeginHover(point)


    def onEndHover(self, element, point):
        element.onEndHover(point)
