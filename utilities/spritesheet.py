import itertools
import os.path
from PIL import Image



def modify(filename, ix=None, iy=None, row_mapping=None, rotate=True):
    sheet = Image.open(filename)
    sx, sy = sheet.size
    tx, ty = int(sx / ix), int(sy / iy)
    out = Image.new(sheet.mode, sheet.size)

    if rotate:
        for x, y in itertools.product(range(0, sx, tx), range(0, sy, ty)):
            tile = sheet.crop((x, y, x+tx, y+ty))
            row = row_mapping[int(x / tx)]*ty
            out.paste(tile, (y, row))

    out.save("{}-new{}".format(*os.path.splitext(filename)))


if __name__ == "__main__":
    import sys

    row_mapping = [2, 3, 0, 1]
    filenames = sys.argv[1:]

    if filenames:
        for fn in filenames:
            modify(fn, 4, 4, row_mapping, True)
    else:
        print("please specify a list of filenames")
