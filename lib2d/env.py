from math import pi

from pygame import Rect

from . import res
from .objects import GameObject
from .bbox import BBox


cardinalDirs = {"north": pi * 1.5, "east": 0.0, "south": pi / 2, "west": pi}


class DummyQuadTree(object):
    """
    Used when level geometry is not specified
    """

    def hit(self, rect):
        return False


class Environment(GameObject):
    """
    A game world where objects exist.
    """

    def __init__(self):
        GameObject.__init__(self)


class Area(Environment):
    """
    3D environment for things to live in.
    think of this as a multilayered sprite group

    uses a quadtree for fast collision detection with level geometry.
    collisions are checked whenever an object is moved.  the return value of
    the two movement functions will let you know if the obj was able to be
    moved or not.

    objects can exits in layers, just like maps.  since the y values can
    vary, when testing for collisions the y value will be truncated and tested
    against the quadtree that is closest.  if there is no quadtree, no
    collision testing will be done.

    for speed, there are a few hacks to be aware of:
        objects move in 3d space, but level geometry is 2d space
        when using pygame rects, the y value maps to the z value in the area


    a word on the coordinate system:
        coordinates are 'right handed'
        x axis moves toward viewer
        y axis move left right
        z axis is height

    NOTE: some of the code is specific for maps from the tmxloader
    """


    def defaultPosition(self):
        return BBox(0, 0, 0, 1, 1, 1)

    def defaultSize(self):
        # TODO: this cannot be hardcoded!
        return (10, 8)


    def __init__(self):
        GameObject.__init__(self)
        self.exits = {}
        self.geometry = {}  # geometry (for collisions) of each layer
        self.objects = {}  # position and size of objects in 3d space
        self.orientations = {}  # records where the object is facing
        self.extent = None  # absolute boundries of the area
        self.joins = []
        self._oldPositions = {}  # used in collision handling

        self.messages = []

        self.time = 0

    def update(self, time):
        self.time += time
        [o.update(time) for o in self.objects]


    def join(self, obj1, obj2):
        """
        joins two objects together.
        if one object moves, the other one will move with it, if able
        """

        self.joins.append((obj1, obj2))


    def unjoin(self, obj1, obj2):
        """
        breaks a join between two objects
        """

        try:
            self.joins.remove((obj1, obj2))
            return True
        except:
            return False


    def setExtent(self, rect):
        """
        set the limits that things can move inside the area
        """

        self.extent = Rect(rect)


    def setLayerGeometry(self, layer, rects):
        """
        set the layer's geometry.  expects a list of rects.
        """

        from . import quadtree

        self.geometry[layer] = quadtree.FastQuadTree(rects)
        self.geoRect = rects


    def testCollideGeometry(self, bbox):
        """
        test if a bbox collides with the layer geometry

        the geometry layer will be calculated from the z value
        """

        # TODO: calc layer value
        layer = 4

        try:
            hit = self.geometry[layer].hit(self.toRect(bbox))
            return True if hit else False
        except KeyError:
            msg = "Area Layer {} does not have a collision layer"
            print(msg.format(layer))
            return False
            raise Exception


    def testCollideObjects(self, bbox):
        values = []
        keys = []

        for obj, b in self.objects.items():
            values.append(b)
            keys.append(obj)

        return [keys[i] for i in bbox.collidelistall(values)]


    def testCollideGeometryAll(self):
        # return list of all collisions between objects and level geometry
        pass


    def getBBox(self, obj):
        """ Return a bbox that represents this object in world """
        return self.objects[obj]


    def setBBox(self, obj, bbox):
        """ Attempt to set an objects bbox.  Returns True if able. """

        if not isinstance(bbox, BBox):
            bbox = BBox(bbox)

        if self.testCollide(bbox):
            return False
        else:
            self.objects[obj] = bbox
            self._oldPositions[obj] = bbox
            return True


    def testCollide(self, bbox):
        return False


    def getSize(self, obj):
        """ Return 3d size of the object """

        return self.objects[obj].size


    def getPositions(self):
        return [(o, b.origin) for (o, b) in self.objects.items()]


    def getOrientation(self, obj):
        """ Return the angle object is facing in radians """

        return self.orientations[obj]


    def setOrientation(self, obj, angle):
        """ Set the angle the object is facing.  Expects radians. """

        if isinstance(angle, str):
            try:
                angle = cardinalDirs[angle]
            except:
                raise
        self.orientations[obj] = angle


    def add(self, obj):
        Environment.add(self, obj)
        self.objects[obj] = self.defaultPosition()
        self.orientations[obj] = 0.0

    def setPosition(self, obj, coords):
        """
        Attempt to move object in 3d space.  Returns true if able.
        """
        x, y, z = coords

        size = self.objects[obj].size
        bbox = BBox((x, y, z), size)
        collide = self.testCollideGeometry(bbox)

        # object collides with something else, cannot set new position
        if collide:
            return False

        # object is within areas extent and doesn't collide, so set it
        elif self.extent.contains(self.toRect(bbox)):
            self._oldPositions[obj] = self.objects[obj]
            self.objects[obj] = bbox
            return True

        # object is outside bounds of area, can't move it
        else:
            return False


    def toRect(self, bbox):
        """
        Make a rect that represents the object's 'bottom plane'.
        This is not the same coordinate space as the world.
        """

        return Rect((bbox.left, bbox.back, bbox.width, bbox.depth))


    def getOldPosition(self, obj):
        return self._oldPositions[obj]


    def movePosition(self, obj, coords, push=False):
        """
        Attempt to move an object in 3d space.  Returns True if able.
        """
        x, y, z = coords

        bbox = self.objects[obj].move(x, y, z)

        # collides with level geometry, cannot move
        if self.testCollideGeometry(bbox):
            return False

        # test for collisions with other objects
        collide = self.testCollideObjects(bbox)
        try:
            collide.remove(obj)
        except:
            pass

        # find things we are joined to
        joins = [i[1] for i in self.joins if i[0] == obj]

        # if joined, then add it to collisions and treat it is if being pushed
        if joins:
            collide.extend(joins)
            push = True

        # handle collisions with objects
        if collide:

            # are we pushing something?
            if push and all([other.pushable for other in collide]):
                if self.extent.contains(self.toRect(bbox)):

                    # we are able to move 
                    self._oldPositions[obj] = self.objects[obj]
                    self.objects[obj] = bbox

                    # recursively push other objects
                    # if any of them cannot be push, just go back
                    for other in collide:
                        if not self.movePosition(other, (x, y, z), True):
                            self.objects[obj] = self._oldPositions[obj]
                            return False

                    return True

            # one of the objects cannot be pushed
            return False

        # no collisions, so move the object
        elif self.extent.contains(self.toRect(bbox)):
            self._oldPositions[obj] = self.objects[obj]
            self.objects[obj] = bbox

            self.messages.append("{} {} moves".format(self.time, obj.name))
            return True


    def getPosition(self, obj):
        return self.objects[obj].origin


    def setMap(self, mapname):
        """
        set the area to use the specified map

        map will be loaded and then all children of this area will be
        re-initialized.  You shouldn't have to do this more than once.

        This object must already be connected to the data tree, otherwise
        object loading will not work...and loading will fail.
        """
        import pytmx

        def toWorld(data, coords):
            """ translate tiled map coordinates to world coordinates """
            return coords[1] * data.tileheight, coords[0] * data.tilewidth, l

        self.mappath = res.mapPath(mapname)
        data = pytmx.tmxloader.load_tmx(self.mappath)

        # set the boundries (extent) of this map
        self.setExtent(((0, 0),
                      (data.width * data.tilewidth, data.height * data.tileheight)))

        props = data.get_tile_properties_by_layer(3)


        # load the level geometry and set it 
        rects = pytmx.build_rects(data, 4)
        self.setLayerGeometry(4, rects)

        # load the npc's and place them in the default positions 
        npcs = [p for p in props if p[1].get('group', None) == 'npc']

        for (gid, prop) in npcs:
            pos = data.getTileLocation(gid)
            if len(pos) > 1:
                msg = "control gid: {} is used in more than one locaton"
                print(msg.format(gid))
                raise Exception

            x, y, z = toWorld(data, pos[0])
            x += data.tileheight  # needed to position objects correctly
            y += data.tilewidth / 2  # needed to position objects correctly
            obj = self._parent.getChildByGUID(int(prop['guid']))

            self.add(obj)
            w, h, d = (10, 6, 8)
            bbox = BBox(x - d, y, z, d, w, h)
            self.setBBox(obj, bbox)
            self.setOrientation(obj, "south")

        # load the items and place them where they should go
        # items can have duplicate entries
        items = [p for p in props if p[1].get('group', None) == 'item']
        done = []

        for (gid, prop) in items:
            if gid in done: continue
            done.append(gid)

            locations = data.getTileLocation(gid)
            obj = self._parent.getChildByGUID(int(prop['guid']))
            copy = False

            for x, y, l in locations:
                x, y, z = toWorld(data, (x, y, l))
                x += data.tileheight  # needed to position objects correctly
                y += data.tilewidth / 2  # needed to position objects correctly

                # objects cannot exists in multiple locations, so a copy is
                # made for each
                if copy:
                    obj = obj.copy()

                self.add(obj)
                z = 0
                w, h, d = (10, 6, 8)
                bbox = BBox(x - d, y, z, d, w, h)
                self.setBBox(obj, bbox)
                self.setOrientation(obj, "south")
                copy = True

                # handle the exits
        # here only the exits and positions are saved
        # another class will have to finalize the exits by adding a ref to
        # guid of the other area
        exits = [p for p in props if p[1].get('group', None) == 'door']
        for gid, prop in exits:
            x, y, l = data.getTileLocation(gid)[0]
            y *= data.tilewidth
            x *= data.tileheight
            self.exits[prop['guid']] = ((x, y, l), None)


    def stick(self, obj):
        self.setPosition(obj, self._oldPositions[obj])


    def unstick(self, obj):
        pass
