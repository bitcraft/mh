from lib2d.common import res
from lib2d.common.objects import GameObject
from lib2d.common.quadtree import FastQuadTree, FrozenRect
from lib2d.common.bbox import BBox
from lib2d.common.vec import Vec2d
from lib2d.pathfinding import astar

from pygame import Rect
import math

cardinalDirs = {"north": math.pi*1.5, "east": 0.0, "south": math.pi/2, "west": math.pi}


class CollisionError(Exception):
    pass


class ExitTile(FrozenRect):
    def __init__(self, rect, exit):
        FrozenRect.__init__(self, rect)
        self._value = exit

    def __repr__(self):
        return "<ExitTile ({}, {}, {}, {}): {}>".format(
            self._left,
            self._top,
            self._width,
            self._height,
            self._value)


class Body(object):
    def __init__(self, bbox, acc, vel, o, parent=None):
        self.parent = parent
        self.bbox = bbox
        self.oldbbox = bbox
        self.acc = acc
        self.vel = vel
        self.o = o
        self._isFalling = False

    def __repr__(self):
        if self.parent:
            return "<Body: {}>".format(self.parent.name)
        else:
            return "<Body: {}>".format(self.parent)

    @property
    def gravity(self):
        return self.parent.gravity


    @property
    def pushable(self):
        try:
            return self.parent.pushable
        except AttributeError:
            return True


    @property
    def isFalling(self):
        return self._isFalling


    @isFalling.setter
    def isFalling(self, value):
        self._isFalling = value
        try:
            self.parent.isFalling = value
        except AttributeError:
            pass


class AbstractArea(GameObject):
    pass


class Sound(object):
    """
    Class that manages how sounds are played and emitted from the area
    """

    def __init__(self, filename, ttl):
        self.filename = filename
        self.ttl = ttl
        self._done = 0
        self.timer = 0

    def update(self, time):
        if self.timer >= self.ttl:
            self._done = 1
        else:
            self.timer += time

    @property
    def done(self):
        return self._done



class Area(AbstractArea):
    """3D environment for things to live in.
    Includes basic pathfinding, collision detection, among other things.

    uses a quadtree for fast collision testing with level geometry.

    bodies can exits in layers, just like maps.  since the y values can
    vary, when testing for collisions the y value will be truncated and tested
    against the quadtree that is closest.  if there is no quadtree, no
    collision testing will be done.

    there are a few hacks to be aware of:
        bodies move in 3d space, but level geometry is 2d space
        when using pygame rects, the y value maps to the z value in the area

    a word on the coordinate system:
        coordinates are 'right handed'
        x axis moves toward viewer
        y axis move left right
        z axis is height

    Expects to load a specially formatted TMX map created with Tiled.
    Layers:
        Control Tiles
        Upper Partial Tiles
        Lower Partial Tiles
        Lower Full Tiles

    Contains a very basic discrete collision system.

    The control layer is where objects and boundries are placed.  It will not
    be rendered.  Your map must not have any spaces that are open.  Each space
    must have a tile in it.  Blank spaces will not be rendered properly and
    will leave annoying trails on the screen.

    The control layer must be created with the utility included with lib2d.  It
    contains metadata that lib2d can use to layout and position objects
    correctly.

    REWRITE: FUNCTIONS HERE SHOULD NOT CHANGE STATE

    NOTE: some of the code is specific for maps from the tmxloader
    """


    def defaultPosition(self):
        return BBox(0,0,0,1,1,1)

    def defaultSize(self):
        # TODO: this cannot be hardcoded!
        return (10, 8)


    def __init__(self):
        AbstractArea.__init__(self)
        self.exits    = {}
        self.geometry = {}       # geometry (for collisions) of each layer
        self.bodies = {}         # hack
        self.extent = None       # absolute boundries of the area
        self.joins = []          # records simple joins between bodies
        self.messages = []
        self.time = 0
        self.tmxdata = None
        self.mappath = None
        self.sounds = []
        self.soundFiles = []
        self.inUpdate = False
        self._addQueue = []
        self._removeQueue = []
        self._addQueue = []
        self.drawables = []      # HAAAAKCCCCKCK
        self.changedAvatars = True #hack
        self._grounded = {}
        self.music_pos = 0

        self.flashes = []
        self.inUpdate = False
        self._removeQueue = []


    def flash(self, position):
        self.flashes.append(position)


    def load(self):
        """Load the data from a TMX file that is required for this map

        This must be done when using the object in the game!
        """
      
        from pytmx import tmxloader
 
        self.tmxdata = tmxloader.load_pygame(
                       self.mappath, force_colorkey=(128,128,0))

        # quadtree for handling collisions with exit tiles
        rects = []
        for guid, param in self.exits.items():
            try:
                x, y, l = param[0]
            except:
                continue

            rects.append(ExitTile((x,y,
                self.tmxdata.tilewidth, self.tmxdata.tileheight), guid))

        # get sounds from tiles
        for i, layer in enumerate(self.tmxdata.tilelayers):
            props = self.tmxdata.getTilePropertiesByLayer(i)
            for gid, tileProp in props:
                for key, value in tileProp.items():
                    if key[4:].lower() == "sound":
                        self.soundFiles.append(value)

        # get sounds from objects
        for i in [ i for i in self.getChildren() if i.sounds ]:
            self.soundFiles.extend(i.sounds)

        #self.exitQT = QuadTree(rects)


    def add(self, thing, pos=None):
        if pos == None:
            pos = self.defaultPosition().origin

        body = Body(BBox(pos, thing.size), Vec2d(0,0), Vec2d(0,0), 0.0, \
                    parent=thing)
        self.bodies[thing] = body
        AbstractArea.add(self, thing)
        #AbstractArea.add(self, body)
        self.changedAvatars = True


    def remove(self, thing):
        if self.inUpdate:
            self._removeQueue.append(thing)
            return

        AbstractArea.remove(self, thing)
        del self.bodies[thing]
        self.changedAvatars = True

        # hack
        try:
            self.drawables.remove(thing)
        except (ValueError, IndexError):
            pass


    def movePosition(self, body, (x, y, z), push=True, caller=None, \
                     suppress_warp=False, clip=True):

        """Attempt to move a body in 3d space.

        Args:
            body: (body): body to move
            (x, y, z): difference of position to move
        
        Kwargs:
            push: if True, then any colliding objects will be moved as well
            caller: part of callback for object that created request to move

        Returns:
            None

        Raises:
            CollisionError  


        You should catch the exception if body cannot move.
        This function will emit a bodyRelMove event if successful. 
        """

        if not isinstance(body, Body):
            raise ValueError, "must supply a body"

        movable = 0
        originalbbox = body.bbox
        newbbox = originalbbox.move(x, y, z)

        # collides with level geometry, cannot move
        if self.testCollideGeometry(newbbox) and clip:
            return False

        # test for collisions with other bodies
        collide = self.testCollideObjects(newbbox)
        try:
            collide.remove(body)
        except:
            pass

        # find things we are joined to
        joins = [ i[1] for i in self.joins if i[0] == body ]

        # if joined, then add it to collisions and treat it is if being pushed
        if joins:
            collide.extend(b for b in joins if not b == body)
            push = True

        # handle collisions with bodies
        if collide:

            # are we pushing something?
            if push and all([ other.pushable for other in collide ]):

                # we are able to move
                body.oldbbox = body.bbox
                body.bbox = newbbox

                # recursively push other bodies
                for other in collide:
                    if not self.movePosition(other, (x, y, z), push=True):
                        # we collided, so just go back to old position
                        body.oldbbox = originalbbox
                        body.bbox = originalbbox
                        return False

            else:
                if clip: return False

        body.oldbbox = body.bbox
        body.bbox = newbbox

        self._sendBodyMove(body, caller=caller)

        bbox2 = newbbox.move(0,0,32)
        tilePos = self.worldToTile(bbox2.topcenter)
        try:
            # emit sounds from bodies walking on them
            prop = self.tmxdata.getTileProperties(tilePos)
        except:
            pass

        else:
            if not prop == None:
                name = prop.get('walkSound', False)
                if name:
                    self.emitSound(name, newbbox.bottomcenter, ttl=600)

        try:
            # test for collisions with exits
            exits = self.exitQT.hit(self.toRect(newbbox))
        except AttributeError:
            exits = []


        if exits and not suppress_warp:
            # warp the player
            exit = exits.pop()

            # get the position and guid of the exit tile of the other map
            fromExit, guid = self.exits[exit.value]
            if not guid == None: 
                # used to correctly align sprites
                fromTileBBox = BBox(fromExit, (16,16,1))
                tx, ty, tz = fromTileBBox.origin
            
                # get the GUID of the map we are warping to
                dest = self.getRoot().getChildByGUID(guid)
                toExit, otherExit = dest.exits[exit.value]

                bx, by, bz = newbbox.origin
                ox, oy, oz = originalbbox.origin
                bz = 0

                # determine wich direction we are traveling through the exit
                angle = math.atan2(oy-by, ox-bx)

                # get the position of the tile in out new area
                newx, newy, newz = toExit

                # create a a bbox to position the object in the new area
                dx = 16 / 2 - newbbox.depth / 2
                dy = 16 / 2 - newbbox.width / 2
                dz = 0

                exitbbox = BBox((newx+dx, newy+dy, newz+dz), newbbox.size)
                face = self.getOrientation(body)
                dest.add(body)
                dest.setBBox(body, exitbbox)
                dest.setOrientation(body, face)
                
                # when changing the destination, we do a bunch of moves first
                # to push objects out of the way from the door...if possible
                dx = round(math.cos(angle))
                dy = round(math.sin(angle))
                dz = 0
                dest.movePosition(body, (dx*20, dy*20, dz*20), False, \
                                  suppress_warp=True, clip=False)

                for x in range(40):
                    dest.movePosition(body, (-dx, -dy, -dz), True, \
                                      suppress_warp=True, clip=False)

                # send a signal that this body is warping
                bodyWarp.send(sender=self, body=body, destination=dest,
                              caller=caller)

        return True 


    def getBody(self, thing):
        return self.bodies[thing]


    def setOrientation(self, thing, angle):
        """ Set the angle the object is facing.  Expects radians. """

        if isinstance(angle, str):
            try:
                angle = cardinalDirs[angle]
            except:
                raise

        self.getBody(thing).o = angle


    def setLayerGeometry(self, layer, rects):
        """
        set the layer's geometry.  expects a list of rects.
        """

        self.geometry[layer] = FastQuadTree(rects)
        self.geoRect = rects


    def pathfind(self, obj, destination):
        """Pathfinding for the world.  Destinations are 'snapped' to tiles.
        """

        def NodeFactory((x, y, l)):
            try:
                if self.tmxdata.getTileGID(x, y, l) == 0:
                    node = Node((x, y))
                else:
                    return None
            except:
                return None
            else:
                return node


        start = self.worldToTile(self.bboxes[obj].bottomcenter)
        finish = self._worldToTile((destination[0], destination[1], 0))
        path = astar.search(start, finish, factory)


    #def tileToWorld(self, (x, y, z)):
    #    xx = int(x) * self.tmxdata.tileheight
    #    yy = int(y) * self.tmxdata.tilewidth
    #    return xx, yy, z


    # platformer
    def worldToTile(self, (x, y, z)):
        xx = int(y) / self.tmxdata.tilewidth
        yy = int(z) / self.tmxdata.tileheight
        zz = 0
        return xx, yy, zz

    def pixelToWorld(self, (x, y, z)):
        return (y, x, z)

    def _worldToTile(self, (x, y)):
        return int(y)/self.tmxdata.tileheight, int(x)/self.tmxdata.tilewidth


    def emitText(self, text, pos=None, thing=None):
        if pos==thing==None:
            raise ValueError, "emitText requires a position or thing"

        if thing:
            pos = self.bodies[thing].bbox.center
        emitText.send(sender=self, text=text, position=pos)
        self.messages.append(text)


    def emitSound(self, filename, pos=None, thing=None, ttl=350):
        if pos==thing==None:
            raise ValueError, "emitSound requires a position or thing"

        self.sounds = [ s for s in self.sounds if not s.done ]
        if filename not in [ s.filename for s in self.sounds ]:
            if thing:
                pos = self.bodies[thing].bbox.center
            emitSound.send(sender=self, filename=filename, position=pos)
            self.sounds.append(Sound(filename, ttl))


    def update(self, time):
        self.inUpdate = True
        self.time += time

        [ sound.update(time) for sound in self.sounds ]

        for thing, body in self.bodies.items():
            self.updatePhysics(body, time)
            thing.update(time)

        # awkward looping allowing objects to be added/removed during update
        self.inUpdate = False
        [ self.add(thing) for thing in self._addQueue ] 
        self._addQueue = []
        [ self.remove(thing) for thing in self._removeQueue ] 
        self._removeQueue = []


    # 2d physics only
    def updatePhysics(self, body, time):
        """
        basic physics
        """
     
        time = time / 100

        if body.gravity:
            body.acc += Vec2d((0, 9.8)) * time
    
        body.vel = body.acc * time
        y, z = body.vel

        if not y==0:
            self.movePosition(body, (0, y, 0))

        if z > 0: 
            falling = self.movePosition(body, (0, 0, z))
            if falling:
                body.isFalling = True
                self._grounded[body] = False
            else:
                if body.isFalling:
                    body.parent.fallDamage(body.vel.y)
                body.isFalling = False
                self._grounded[body] = True
                if int(body.vel.y) >= 1:
                    body.acc.y = -body.acc.y * .2
                else:
                    body.acc.y = 0
        elif z < 0:
            flying = self.movePosition(body, (0, 0, z))
            if flying:
                self._grounded[body] = False
                body.isFalling = True


    # platformer
    def grounded(self, body):
        try:
            return self._grounded[body]
        except:
            return False


    def setExtent(self, rect):
        self.extent = Rect(rect)


    def testCollideGeometry(self, bbox):
        """
        test if a bbox collides with the layer geometry

        the geometry layer will be calculated from the z value
        """

        # TODO: calc layer value
        layer = 0


        try:
            rect = self.toRect(bbox)
            hit = self.geometry[layer].hit(rect)
            con = self.extent.contains(rect)
            return bool(hit) or not bool(con)

        except KeyError:
            msg = "Area Layer {} does not have a collision layer"
            print msg.format(layer)
            return False

            raise Exception, msg.format(layer)


    def testCollideObjects(self, bbox, skip=[]):
        bboxes = []
        bodies = []

        for body in self.bodies.values():
            if not body in skip:
                bboxes.append(body.bbox)
                bodies.append(body)

        return [ bodies[i] for i in bbox.collidelistall(bboxes) ]


    def testCollideGeometryAll(self):
        # return list of all collisions between bodies and level geometry
        pass


    def getPositions(self):
        return [ (o, b.origin) for (o, b) in self.bboxes.items() ]


    # for platformers
    def toRect(self, bbox):
        return Rect((bbox.y, bbox.z+bbox.height, bbox.width, bbox.height))


    def getOldPosition(self, body):
        return self._oldbboxes[body]


    def _sendBodyMove(self, body, caller, force=None):
        position = body.bbox.origin
        bodyAbsMove.send(sender=self, body=body, position=position, caller=caller, force=force)

    
    def warpBody(self):
        """
        move a body to another area using an exit tile.
        objects on or around the tile will be push out of the way
        if objects cannot be pushed, then the warp will fail
        """
        pass



    #  CLIENT API  --------------

    def join(self, body0, body1):
        self.joins.append((body0, body1))


    def unjoin(self, body0, body1):
        self.joins.remove((body0, body1))


    def getRect(self, thing):
        return self.toRect(self.bodies[thing].bbox)


    def isGrounded(self, thing):
        return self.grounded(self.bodies[thing])


    def getBBox(self, thing):
        return self.bodies[thing].bbox


    def setBBox(self, thing, bbox):
        """ Attempt to set a bodies bbox.  Returns True if able. """

        if not isinstance(bbox, BBox):
            bbox = BBox(bbox)

        body = self.getBody(thing)
        body.oldbbox = body.bbox
        body.bbox = bbox


    # for platformers
    def applyForce(self, body, (x, y, z)):
        body.acc += Vec2d(y, z)


    def setForce(self, body, (x, y, z)):
        body.acc = Vec2d(y, z)


    def getOrientation(self, thing):
        """ Return the angle thing is facing in radians """
        return self.bodies[thing].o


    def setPosition(self, thing, origin):
        body = self.bodies[thing]
        body.bbox = BBox(origin, body.bbox.size)


    def getSize(self, thing):
        """ Return 3d size of the object """
        return self.bodies[thing].bbox.size


    def getPosition(self, thing):
        """ for clients to find position in world of things, not bodies """
        return self.bodies[thing].bbox.origin


    def getBody(self, thing):
        return self.bodies[thing]


    def stick(self, body):
        pass


    def unstick(self, body):
        pass
