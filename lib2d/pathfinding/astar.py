from heapq import heappush, heappop, heappushpop, heapify
from collections import defaultdict

class Astar(object):
    pass


class Node(object):
    __slots__ = ['parent', 'x', 'y', 'g', 'h', 'f', 'is_closed']

    def __init__(self, pos=(0,0)):
        self.x, self.y = pos
        self.parent = None
        self.g = 0
        self.h = 0
        self.is_closed = 0


def getSurrounding(node):
    return ((node.x-1, node.y-1), (node.x, node.y-1), (node.x+1, node.y-1), \
            (node.x-1, node.y),   (node.x+1, node.y), \
            (node.x-1, node.y+1), (node.x, node.y+1), (node.x+1, node.y+1))

def dist(start, finish):
    return abs(finish.x - start.x) + abs(finish.y - start.y)

def calcG(node):
    score=0
    score += node.g
    while not node.parent == None:
        node = node.parent
        score += node.g
    return score


def calcH(node, finish):
    return 0
    return dist(node, finish)


def search(start, finish, factory):
    """perform basic a* search on a 2d map.
   
    Args:
        start:      tuple that defines the starting position
        finish:     tuple that defined the finish
        factory:    function that will return a Node object from a position

    Factory can return None, which means the area is not passable.
 
    """

    # used to locate nodes in the heap and modify their f scores
    heapIndex = {}

    success  = False
    nodeHash = {}
    finish = Node(finish)
    start = Node(start)
    start.h = dist(start, finish) 
    openlist = [(start.g + start.h, start)]

    while openlist:
        f, keyNode = heappop(openlist)
        try:
            while keyNode == None:
                f, keyNode = heappop(openlist)
        except:
            break

        if keyNode.x == finish.x and keyNode.y == finish.y:
            success = True
            break

        keyNode.is_closed = 1

        for neighbor in getSurrounding(keyNode):
            try:
                node = nodeHash[neighbor]
            except KeyError:
                node = factory(neighbor)
                if node:
                    score = keyNode.g + dist(keyNode, node)
                    node.parent = keyNode
                    node.g = score
                    node.h = calcH(node, finish)
                    entry = [node.g + node.h, node]
                    heapIndex[node] = entry
                    heappush(openlist, entry)
                continue

            if not node.is_closed:
                score = keyNode.g + dist(keyNode, node)
                if score < node.g:
                    node.parent = keyNode
                    node.g = score
                    entry = heapIndex.pop(node)
                    entry[-1] = None
                    entry = [node.g + node.h, node]
                    heapIndex[node] = entry
                    heappush(openlist, entry)

    if success:
        path = [(keyNode.x, keyNode.y)]
        while not keyNode.parent == None:
            keyNode = keyNode.parent
            path.append((keyNode.x, keyNode.y))
        return True, path

    else:
        return False, []



if __name__ == "__main__":
    def print_point(point):
        print "=====", point,"====="
        for y in range(10):
            for x in range(10):
                if (x, y) == point:
                    print "=",
                else:
                    print ".",
            print ""
        print ""


    def print_path(area, path):
        for y in range(10):
            for x in range(10):
                if not area[y][x] == 0:
                    print "X",

                elif (x,y) in path:
                    print "=",
                else:
                    print ".",

            print ""

    m=\
""".X........
.X........
.X........
..........
X.........
..........
....X.....
..........
..........
.X........"""


    area = []
    for y in range(10):
        area.append([0] * 10)

    for y,line in enumerate(m.split()):
        for x in range(10):
            if line[x] != ".":
                area[y][x] = 1

    def factory((x, y)):
        if x < 0 or y < 0:
            return None

        try:
            if area[y][x] == 0:
                node = Node((x, y))
                return node
            else:
                return None
        except IndexError:
            return None

    v, path = search((0,0), (5,9), factory)
    path.reverse()

    print v, path

    for p in path:
        print_point(p)

    print_path(area, path)
