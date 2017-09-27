# -*- coding: utf-8 -*-

import sys
import os
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
