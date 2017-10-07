# -*- coding: utf-8 -*-

import sys
import os
from difflib import Differ
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import localization_helper


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def remove_if_exist(filename):
    filename = filename.replace("~", os.path.expanduser('~'))
    try:
        os.remove(filename)
    except OSError:
        print("remove_if_exist[os error]: "+ filename)
        pass


# def two_file_is_same(filename1, filename2):

#     with open(filename1) as f1, open(filename2) as f2:
#         differ = Differ()

#         for line in differ.compare(f1.readlines(), f2.readlines()):
#             if line.startswith(" "):
#                 print(line[2:], end="")