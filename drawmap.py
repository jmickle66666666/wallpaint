from omg import *
from PIL import Image, ImageDraw


def drawmap(wad, name, width, height):
    xsize = width - 8
    ysize = height - 8

    edit = MapEditor(wad.maps[name])
    xmin = ymin = 32767
    xmax = ymax = -32768
    for v in edit.vertexes:
        xmin = min(xmin, v.x)
        xmax = max(xmax, v.x)
        ymin = min(ymin, -v.y)
        ymax = max(ymax, -v.y)

    if xsize / float(xmax - xmin) < ysize / float(ymax - ymin):
        scale = xsize / float(xmax - xmin)
    else:
        scale = ysize / float(ymax - ymin)

    xmax = int(xmax * scale)
    xmin = int(xmin * scale)
    ymax = int(ymax * scale)
    ymin = int(ymin * scale)

    for v in edit.vertexes:
        v.x = v.x * scale
        v.y = -v.y * scale

    im = Image.new('RGB', ((xmax - xmin) + 8, (ymax - ymin) + 8), (0,0,0))
    draw = ImageDraw.Draw(im)

    edit.linedefs.sort(key=lambda a: not a.two_sided)

    for line in edit.linedefs:
         p1x = edit.vertexes[line.vx_a].x - xmin + 4
         p1y = edit.vertexes[line.vx_a].y - ymin + 4
         p2x = edit.vertexes[line.vx_b].x - xmin + 4
         p2y = edit.vertexes[line.vx_b].y - ymin + 4

         color = (220, 220, 220)
         if line.two_sided:
             color = (144, 144, 144)
         if line.action:
             color = (220, 130, 50)

         draw.line((p1x, p1y, p2x, p2y), fill=color)
         # draw.line((p1x+1, p1y, p2x+1, p2y), fill=color)
         # draw.line((p1x-1, p1y, p2x-1, p2y), fill=color)
         # draw.line((p1x, p1y+1, p2x, p2y+1), fill=color)
         # draw.line((p1x, p1y-1, p2x, p2y-1), fill=color)

    del draw

    return im
