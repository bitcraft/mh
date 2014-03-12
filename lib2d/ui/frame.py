from lib2d.ui.element import Element


class Frame(Element):
    def __init__(self, frame, packer):
        Element.__init__(self, frame)
        self.packer = packer


    def setPacker(self, packer):
        self.packer = packer


    def addElement(self, other, rect=None):
        self.packer.add(other, rect)


    def removeElement(self, other):
        self.packer.remove(other)


    def resize(self):
        Element.resize(self)
        self.packer.rect = self.rect


    def draw(self, surface):
        return [e.draw(surface) for e in self.packer.elements]
