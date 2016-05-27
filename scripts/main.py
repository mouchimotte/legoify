#!/usr/bin/env python3
# -*- Coding: utf-8 -*-


import sys
from PIL import Image

pieces = {
    'bar_1x4': 4,
    'bar_1x2': 2,
    'bar_1x16': 16,
    'pixel': 1
}

filename = "hi.png"

def divide_by_piece(nb_contigus):
    mapping = {}
    for key in sorted(pieces):
        while nb_contigus >= pieces[key]:
            if key not in mapping:
                mapping[key] = 0
            mapping[key] += 1
            nb_contigus -= pieces[key]
    return mapping

if __name__ == "__main__":
    img = Image.open(filename)
    print('Image information:\n', img.format, img.size, img.mode)
    pixels = img.load()
    mapping = []
    colors = {}

    #color stats
    for line in range(img.size[1]):
        for column in range(img.size[0]):
            if "{0}".format(pixels[column, line]) not in colors:
                colors["{0}".format(pixels[column, line])] = []
            colors["{0}".format(pixels[column, line])].append([column, line])
    print("Colors: ")
    for color in colors:
        pct = len(colors[color]) / (img.size[0] * img.size[1])
        print('{} > {:.2%} with {} pixels'.format(color, pct, len(colors[color])))

    #watching line by line
    for line in range(img.size[1]):
        #identify how many same colored pixels are contigus
        nb_contigus = 0
        mapping.append([])
        for column in range(img.size[0]):
            nb_contigus += 1
            color = pixels[column, line]
            if (column + 1) == img.size[0] \
               or color != pixels[column + 1, line]:
                mapping[line].append({'color': color,
                                      'conf': divide_by_piece(nb_contigus)})
                nb_contigus = 0
    #for line in range(len(mapping)):
    #    print("line {}> ".format(line + 1), mapping[line])

    #build the image with pieces
    img_dest = Image.new("RGB", (img.size[0] * 10, img.size[1] * 10))
    for line in range(len(mapping)):
        column = 0
        #work color block by color block
        for color_block in mapping[line]:
            #there are color and conf key to describe the block
            #print(color_block['color'], color_block['conf'])
            for piece in color_block['conf']:
                for piece_inc in range(color_block['conf'][piece]):
                    size = pieces[piece]
                    line_dest = line * 10
                    for line_inc in range(9):
                        column_dest = column * 10
                        for column_inc in range(size * 10 - 1):
                            img_dest.putpixel([column_dest, line_dest],
                                              color_block['color'])
                            column_dest += 1
                        line_dest += 1
                    column += size
        #quit()
    img_dest.save("legoify_" + filename);
