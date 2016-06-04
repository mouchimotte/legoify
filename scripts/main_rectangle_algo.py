#!/usr/bin/env python3
# -*- Coding: utf-8 -*-


import sys
from PIL import Image
from pathlib import Path

bricks = {(255, 255, 255): [2, 16, 1],
          (139, 149, 169): [1, 4, 16],
          "all": [1, 4]}

def colors_stats(img, pixels):
    colors = {}
    for line in range(img.size[1]):
        for column in range(img.size[0]):
            if "{0}".format(pixels[column, line]) not in colors:
                colors["{0}".format(pixels[column, line])] = []
            colors["{0}".format(pixels[column, line])].append([column, line])
    print("\nColors:")
    for color in colors:
        pct = len(colors[color]) / (img.size[0] * img.size[1])
        print('{} > {:.2%} with {} pixels'.format(color, pct, len(colors[color])))

def bricks_stats(mapping):
    s = {'total_brick': 0,
         'by_color': {}}
    for rectangle in mapping:
        s['total_brick'] += len(rectangle['bricks'])
        if rectangle['color'] not in s['by_color']:
            s['by_color'][rectangle['color']] = {'total_brick': 0,
                                                 'by_length': {}}
        for brick in rectangle['bricks']:
            if brick['length'] not in s['by_color'][rectangle['color']]['by_length']:
                s['by_color'][rectangle['color']]['by_length'][brick['length']] = 0
            s['by_color'][rectangle['color']]['total_brick'] += 1
            s['by_color'][rectangle['color']]['by_length'][brick['length']] += 1
    print("\nBricks by colors:")
    import pprint
    pprint.pprint(s)

def add_horizontal(color, position, length):
    mapping = []
    pointer = 0

    #fill the line by bricks from the highter length to the smalest length
    for brick_length in sorted(bricks[color if color in bricks else "all"],
                               reverse=True):
        #while the size of brick can fit in the length
        while brick_length <= length:
            mapping.append({'position': (position[0] + pointer, position[1]),
                            'length': brick_length,
                            'way': 'horizontal'})
            pointer += brick_length
            length -= brick_length

    #returning the mapping
    return mapping, pointer

def add_vertical(color, position, length):
    mapping = []
    pointer = 0

    #fill the column by bricks from the highter length to the smalest length
    for brick_length in sorted(bricks[color if color in bricks else "all"],
                               reverse=True):
        #while the size of brick can fit in the length
        while brick_length <= length:
            mapping.append({'position': (position[0], position[1] + pointer),
                            'length': brick_length,
                            'way': 'vertical'})
            pointer += brick_length
            length -= brick_length

    #returning the mapping
    return mapping

def divide_by_brick(size, color):
    mapping = []
    used_pixels = {}
    column, line = 0, 0
    width, height = size

    while column < width and line < height:
        m, c = add_horizontal(color,
                              (column, line),
                              width if line + 1 == height else width - 1)
        mapping, column = mapping + m, column + c
        if column + 1 == width:
            mapping += add_vertical(color, (column, line), height - line)
            width -= 1

        #otherwise we do the same at the next line
        column = 0
        line += 1

    return mapping

def add_column(pixels, used_pixels, column, line, width, height, color):
    try:
        pixels[column + width, line]
    except IndexError:
        return False
    for h in range(height):
        if color != pixels[column + width, line + h] \
           or (column + width, line + h) in used_pixels:
            return False
    return True

def add_line(pixels, used_pixels, column, line, width, height, color):
    try:
        pixels[column, line + height]
    except IndexError:
        return False
    for w in range(width):
        if color != pixels[column + w, line + height] \
           or (column + w, line + height) in used_pixels:
            return False
    return True

def divide_by_rectangle(img, pixels):
    rectangles = []
    used_pixels = {}

    for line in range(img.size[1]):
        for column in range(img.size[0]):
            #cehck if this pixel is already rectangled
            if (column, line) in used_pixels:
                continue

            #so init
            color = pixels[column, line]
            width = 1
            height = 1

            #while we can, add a columns and lines
            try_column = True
            try_line = True
            while try_column or try_line:
                #if the precedent column was good,
                # and the next exists,
                # so we try to add the next one:
                if try_column and add_column(pixels, used_pixels,
                                             column, line, width, height,
                                             color):
                    width += 1
                else:
                    try_column = False

                #if the precedent line was good,
                # and the next exists,
                # so we try to add the next one:
                if try_line and add_line(pixels, used_pixels,
                                         column, line, width, height,
                                         color):
                    height += 1
                else:
                    try_line = False

            #we stock used pixels
            for w in range(width):
                for h in range(height):
                    used_pixels[column + w, line + h] = True

            #we stock rectangle information
            rectangles.append({'position': (column, line),
                               'size': (width, height),
                               'color': color})

            #small hack: we jump to the next area
            column += width
    return rectangles

def draw_mapping(img, mapping, filename):
    img_dest = Image.new("RGB", (img.size[0] * 10, img.size[1] * 10))
    pixels_dest = img_dest.load()
    for rectangle in mapping:
        for brick in rectangle['bricks']:
            if brick['way'] == 'vertical':
                width = 1
                height = brick['length']
            else:
                height = 1
                width = brick['length']

            for w in range(width * 10):
                for h in range(height * 10):
                    column = (rectangle['position'][0] + brick['position'][0]) * 10 + w
                    line = (rectangle['position'][1] + brick['position'][1]) * 10 + h
                    color = rectangle['color']
                    #border top and left in FUSHIA
                    if w == 0 or h == 0:
                        color = (255, 0, 255)
                    #border bottom and right in GREEN
                    if w == width * 10 - 1 \
                       or h == height * 10 - 1:
                        color = (0, 255, 0)
                    pixels_dest[column, line] = color
    img_dest.save("mapping_" + filename);
    print('\nImage with mapping is: "mapping_' + filename + '"')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('You have to provide a filename in argument')
        quit()

    filename = sys.argv[1]
    if not Path(filename).exists():
        print('You have to provide a REAL filename in argument')
        quit()

    try:
        img = Image.open(filename)
    except OSError as err:
        print('You have to provide an Image: ', err)
        quit()

    print('Processing with: "', filename, '"\n',
          img.format, img.size, img.mode)
    pixels = img.load()
    colors_stats(img, pixels)

    # divide by rectangles
    mapping = divide_by_rectangle(img, pixels)
    # divide rectangles by brick
    for rectangle in mapping:
        rectangle['bricks'] = divide_by_brick(rectangle['size'],
                                              rectangle['color'])

    #drawing an image with the mapping
    draw_mapping(img, mapping, filename)

    #bricks stats
    bricks_stats(mapping)
