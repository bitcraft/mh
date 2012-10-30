import res
import pygame, types, os


unsupported = [pygame.Surface, types.MethodType]


def loadObject(name):
    """
    read this node from disk
    """

    import cPickle as pickle

    with open(name + "-data.save") as fh:
        node = pickle.load(fh)

    return node


class GameObject(object):
    """
    the most basic object that can be stored in the game.
    the top level object should have _parent set to None.

    VERY IMPORTANT!
    if you are going to specially handle any object that will become a child of
    the object, YOU MUST HANDLE IT IN add().  failure to do so will cause
    difficult to track bugs.
    """

    population = []
    sounds = []
    gravity = True
    pushable = False
    time_update = False


    def __init__(self, parent=None):
        self.short_name = str(self.__class__)
        self.size       = (32, 32, 32)
        self._children  = []
        self._parent    = parent
        self._childrenGUID = []  # children of this object by guid !dont use
        self.guid = None

        if self.time_update:
            self.population.append(self)


    def __repr__(self):
        return "<{}: \"{}\">".format(self.__class__.__name__, id(self))
    

    def returnNew(self):
        """
        override this if the constructor requires any special arguments
        """

        try:
            return self.__class__()
        except TypeError:
            msg = "Class {} is not cabable of being copied."
            raise TypeError, msg.format(self.__class__)


    def copy(self):
        new = self.returnNew()

        new.__dict__.update(self.__dict__)
        new._parent = None
        new._children = []
        new._childrenGUID = []
        new.guid = None

        for child in self._children:
            new.add(child.copy())

        return new 


    def getPosition(self, what=None):
        # override this for objects that can contain other types
        if what is None: what = self._parent
        return self._parent.getPosition(what)
        #if what is None: what = self
        #return self._parent.getPosition(what)


    def getSize(self, what=None):
        # override this for objects that can contain other types
        if what is None: what = self._parent
        return self._parent.getSize(what)
        

    @property
    def parent(self):
        return self._parent


    def load(self):
        """
        override when object needs to load data from disk afer being loaded
        from the save

        so far, images, sounds
        """
        pass


    def loadAll(self):
        """
        load this and the children
        """
        self.load()
        [ child.load() for child in self.getChildren() ]


    def unload(self):
        """
        anything that could be removed from memory should be removed here.
        images, sounds go here
        """
        pass


    def setGUID(self, guid):
        try:
            self.guid = int(guid)
        except:
            raise ValueError, "GUID's must be an integer"


    def setName(self, name):
        self.name = name


    def remove(self, other):
        try:
            self._children.remove(other)
            other._parent = None
        except ValueError:
            msg = "Attempting to remove child ({}), but not in parent ({})"
            raise ValueError, msg.format(other, self)


    def add(self, other):
        self._children.append(other)
        try:
            if other._parent:
                other._parent.remove(other)
        except:
            print 'Error taking {} from parent.  Ignored'.format(other)
            pass

        other.setParent(self)


    def hasChild(self, child):
        for c in self.getChildren():
            if c == child: return True
        return False


    def getChildren(self):
        # should be a breadth-first search
        children = []
        openList = [self]
        while openList:
            parent = openList.pop()
            children = parent._children[:]
            while children:
                child = children.pop()
                openList.append(child)
                yield child


    def getRoot(self):
        node = self
        while node._parent is not None:
            node = node._parent
        return node


    def getChildByGUID(self, guid):
        """
        search the children of this object for an object
        with the matching guid
        """
      
        guid = int(guid) 
        if self.guid == guid: return self 
        for child in self.getChildren():
            if child.guid == guid: return child

        msg = "GUID ({}) not found."
        raise Exception, msg.format(guid)


    def getChildByName(self, name):
        for child in self.getChildren():
            if child.name == name: return child

        msg = "Object by name ({}) not found."
        raise Exception, msg.format(name)


    def get_flag(self):
        """
        flags are binary values that are attached to the object

        will return true or false for the given property
        """

        pass


    def set_flag(self):
        """
        flags are binary values that are attached to the object

        use to set a flag as true  or false
        other values will be evaluated as a bool according to python's rules
        """

        pass


    def serialize(self, pickler, callback=None):
        """
        pickle this object, and continue with the children
        """

        # last chance we have to make sure children can be accessed in another
        # life!
        self.childrenGUID = [ c.guid for c in self._children ]

        pickler.dump(self)

        if callback:
            callback(self, pickler)

        for child in self._children:
            child.serialize(pickler, callback)


    def get_image(self):
        """
        return an image suitable for drawing onto a surface.

        it is up to the drawing party to know where/how to draw it.  =)
        """

        return self.icon


    def destroy(self, parent=None):
        """
        destroy the object and children.  the object will be removed from the
        game and references cleared.
        """

        name = "DEAD-{}".format(self.name)
        if self._parent:
            self._parent.remove(self)
        for child in self._children:
            child.destroy()
        self._children = []
        self.unload()
        self.name = name


    def setParent(self, parent):
        # when setting the parent, make sure to remove self
        # the parent's children manually

        self._parent = parent


    def save(self, name):
        """
        write the state of this object and all of its children to disk.
        it will be a pair of files.
        """

        import cPickle as pickle
        import StringIO

        def testRun():
            for child in self.getChildren():
                for k, v in child.__dict__.items():
                    if type(v) in unsupported:
                        print "Object {} contains unpickleable attribute \"{}\" {} ({})".format(child, k, type(v), v)
                        raise ValueError

        # generate unique ID's for all the objects (if not already assigned)
        i = 0
        used = set([ child.guid for child in self.getChildren() ])
        used.add(self.guid)
        for child in self.getChildren():
            if child.guid: continue
            while i in used:
                i += 1
            child.setGUID(i)
            used.add(i)

        testRun()

        toc = {}
        def handleWrite(obj, pickler):
            toc[obj.guid] = fh.tell()

        with open(name + "-data.temp", "w") as fh:
            pickler = pickle.Pickler(fh, -1)
            self.serialize(pickler, handleWrite)

        os.rename(name + "-data.temp", name + "-data.save")

        #with open(name + "-index.txt", "w") as fh:
        #    pickler = pickle.Pickler(fh, -1)
        #    pickler.dump(toc)


class InteractiveObject(GameObject):
    """
    object that exists in the game world
    excludes things like animations and ui elements which are saved, but
    don't require things like physics simulation
    """

class AvatarObject(GameObject):
    def __init__(self, avatar):
        from avatar import Avatar

        GameObject.__init__(self)

        if isinstance(avatar, Avatar):
            self.add(avatar)
            self._avatar = avatar


    @property    
    def avatar(self):
        return self._avatar


class InteractiveObject(AvatarObject):
    def use(self, user=None):
        pass
