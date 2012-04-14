import res



def loadObject(name):
    """
    read this node from disk
    """

    import cPickle as pickle

    with open(name + "-index.txt") as fh:
        toc = pickle.load(fh)

    with open(name + "-data.txt") as fh:
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

    GameObjects support persistence through python's built in pickle module.

    When subclassing this class, keep in mind that some game resources cannot
    be pickled, such as pygame surfaces.

    Each object's "load()" function should be called when external resources
    are needed, but not nessisary to store in the pickle.  Obvious examples
    would be surfaces and sounds, but may also include external files for
    dialogs.

    """

    def __init__(self, parent=None):
        self.short_name = str(self.__class__)
        self.short_desc = ""
        self.long_desc  = ""
        self.name       = ""
        self.pushable   = False
        self.weight     = 1
        self._children  = []
        self._parent    = parent
        self._childrenGUID = []  # children of this object by guid !dont use
        self.guid = None


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


    def update(self, time):
        pass


    def getPosition(self, what=None):
        # override this for objects that can contain other types
        if what == None: what = self._parent
        return self._parent.getPosition(what)


    def getOrientation(self, what=None):
        # override this for objects that can contain other types
        if what == None: what = self._parent
        return self._parent.getOrientation(what)


    def getSize(self, what=None):
        # override this for objects that can contain other types
        if what == None: what = self._parent
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
        self._children.remove(other)


    def add(self, other):
        self._children.append(other)
        if other._parent:
            other._parent.remove(other)
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
        while not node._parent == None:
            node = node._parent
        return node


    def getChildByGUID(self, guid):
        """
        search the children of this object for an object
        with the matching guid
        """
       
        guid = int(guid) 
        for child in self.getChildren():
            if child.guid == guid: return child

        msg = "GUID ({}) not found."
        raise Exception, msg.format(guid)


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


    def destroy(self):
        """
        destroy the object and children.  the object will be removed from the
        game and references cleared.
        """

        for child in self._children:
            child._parent = None
            child.destroy()

        self._children = []


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

        toc = {}
        def handleWrite(obj, pickler):
            toc[obj.guid] = fh.tell()

        with open(name + "-data.txt", "w") as fh:
            pickler = pickle.Pickler(fh, -1)
            self.serialize(pickler, handleWrite)

        with open(name + "-index.txt", "w") as fh:
            pickler = pickle.Pickler(fh, -1)
            pickler.dump(toc)


class AvatarObject(GameObject):
    def __init__(self):
        GameObject.__init__(self)
        self._avatar = None


    def add(self, other):
        from avatar import Avatar

        if isinstance(other, Avatar):
            self._avatar = other

        GameObject.add(self, other)


    @property    
    def avatar(self):
        return self._avatar


    @avatar.setter
    def avatar(self, avatar):
        self._avatar = avatar
        self.add(avatar)


    def setAvatar(self, avatar):
        self._avatar = avatar
        self.add(avatar)

    
    def stop(self):
        pass
