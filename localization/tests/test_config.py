# -*- coding: utf-8 -*-

import unittest
import json

from .context import localization_helper
from .context import ordered

class ConfigTestSuite(unittest.TestCase):

    def setUp(self):
        self.config = localization_helper.Config(file_path='workspace/config.json')
    
    def tearDown(self):
        self.config = None

    def test_empty_config(self):
        with self.assertRaises(Exception):
            localization_helper.Config(file_path='')
    
    def test_relative_config(self):
        file_path = 'workspace/config.json'
        config = localization_helper.Config(file_path=file_path)
        with open(file_path) as json_file:
            data = json.load(json_file)
            self.assertTrue(ordered(config.config) == ordered(data))
  
    def test_get_valid_path_1(self):
        self.assertTrue(self.config.get("spreadsheet.google.secret") == 'client_secret.json')
   
    def test_get_valid_path_2(self):
        self.assertTrue(self.config.get("spreadsheet.google.secret") != 'client_open.json')
   
    def test_get_valid_path_3(self):
        self.assertTrue(self.config.get("spreadsheet.google33333.secret") is None)

if __name__ == '__main__':
    unittest.main()
