"""
Modification of Bjorn Bergstrom's recursive shadowcasting in python.

Adapted from:
http://roguebasin.roguelikedevelopment.org/index.php/Python_shadowcasting_implementation

Leif
"""

# Multipliers for transforming coordinates to other octants:
mult = [
            [1,  0,  0, -1, -1,  0,  0,  1],
            [0,  1, -1,  0,  0, -1,  1,  0],
            [0,  1,  1,  0,  0, -1, -1,  0],
            [1,  0,  0,  1, -1,  0,  0, -1]
        ]


class BergstromFOV(object):
    """
    Helper class to determine light casting on a 2d map.

    Uses Bjorn Bergstrom's recursive shadowcasting.
    """

    def __init__(self, data):
        self.data = data
        self.height = len(data)
        self.width = len(data[0])


    def blocked(self, x, y):
        return (x < 0 or y < 0
                or x >= self.width or y >= self.height
                or not self.data[y][x] == 0)


    def calcFOV(self, (x, y), radius):
        """
        Calculate lit squares from the given location and radius
        """

        lit = []
        for oct in range(8):
            self._castLight(lit, x, y, 1, 1.0, 0.0, radius,
                             mult[0][oct], mult[1][oct],
                             mult[2][oct], mult[3][oct], 0)
        return lit


    def _castLight(self, lit, cx, cy, row, start, end, radius, xx, xy, yx, yy, id):
        """
        Recursive lightcasting function
        """

        if start < end:
            return
        radius_squared = radius*radius
        for j in range(row, radius+1):
            dx, dy = -j-1, -j
            blocked = False
            while dx <= 0:
                dx += 1
                # Translate the dx, dy coordinates into map coordinates:
                X, Y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy

                # l_slope and r_slope store the slopes of the left and right
                # extremities of the square we're considering:
                l_slope, r_slope = (dx-0.5)/(dy+0.5), (dx+0.5)/(dy-0.5)
                if start < r_slope:
                    continue
                elif end > l_slope:
                    break
                else:
                    # Our light beam is touching this square; light it:
                    if dx*dx + dy*dy < radius_squared:
                        lit.append((X, Y))
                    if blocked:
                        # we're scanning a row of blocked squares:
                        if self.blocked(X, Y):
                            new_start = r_slope
                            continue
                        else:
                            blocked = False
                            start = new_start
                    else:
                        if self.blocked(X, Y) and j < radius:
                            # This is a blocking square, start a child scan:
                            blocked = True
                            self._castLight(lit, cx, cy, j+1, start, l_slope,
                                             radius, xx, xy, yx, yy, id+1)
                            new_start = r_slope

            # Row is scanned; do next row unless last square was blocked:
            if blocked:
                break
        
