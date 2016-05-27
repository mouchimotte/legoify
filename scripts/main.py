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
    img = Image.open("hi.png")
    print('Image information:\n', img.format, img.size, img.mode)
    pixels = img.load()
    mapping = []
    colors = {}

    #color stats
    for line in range(img.size[1]):
        for column in range(img.size[0]):
            #debug print("ca > {0}".format(pixels[line, column]), "ca")
            if "{0}".format(pixels[column, line]) not in colors:
                colors["{0}".format(pixels[column, line])] = []
            colors["{0}".format(pixels[column, line])].append([column, line])
    #debug print(colors)
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
                mapping[line].append({color: divide_by_piece(nb_contigus)})
                nb_contigus = 0
    for line in range(len(mapping)):
        print("line {}> ".format(line + 1), mapping[line])
