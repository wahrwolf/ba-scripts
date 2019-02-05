#!/usr/bin/env python3
from sys import argv, exit
from getopt import getopt, GetoptError
from xmltodict import parse, unparse

inputfile = argv[1]
outputdir = argv[2]

tu_per_file = int(argv[3])
buffer_file = None
tus_written = 0

current_prefix = 0

def writeTu(path, item):
    global tus_written, tu_per_file, buffer_file, outputdir, inputfile, current_prefix
    if tus_written < tu_per_file:
        unparse({"tu":item}, buffer_file, full_document=False)
        tus_written += 1
    else:
        buffer_file.close()
        current_prefix += 1
        tus_written = 0
        buffer_file = open(f"{outputdir}/{current_prefix}-{inputfile}", "w+")
        print(f"Opening: {outputdir}/{current_prefix}-{inputfile}")
        writeTu(path, item)

    return True

buffer_file = open(f"{outputdir}/{current_prefix}-{inputfile}", "w+")
print(f"Opening: {outputdir}/{current_prefix}-{inputfile}")

with open(inputfile) as tmx_file:
    trans_dict = parse(tmx_file.read(), item_depth=3, item_callback=writeTu)

