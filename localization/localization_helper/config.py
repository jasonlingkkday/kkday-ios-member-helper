# -*- coding: utf-8 -*-

import json

class Config(object):
    def __init__(self, file_path):
        self.config = dict()
        with open(file_path) as json_file:
            self.config = json.load(json_file)

    def get(self, path):
        tokens = path.split(".")
        if not tokens:
            return None
        val = self.config
        while tokens:
            key = tokens.pop(0)
            val = val.get(key)
            if val is None:
                break
        return val
