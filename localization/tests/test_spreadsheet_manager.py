# -*- coding: utf-8 -*-

import unittest

from .context import localization_helper
from .context import remove_if_exist

class SpreadSheetManagerTestSuite(unittest.TestCase):
    
    def setUp(self):
        self.manager = localization_helper.SpreadSheetManager()
    
    def tearDown(self):
        self.manager = None

    def test_create_range_1(self):
        range_name = self.manager.create_range(sheet_name="blah", start_row=1, end_row=200, start_col="A", end_col="Z")
        self.assertTrue(range_name == u"blah!A1:Z200")
    
    def test_create_range_2(self):
        range_name = self.manager.create_range(sheet_name="noooo", start_row=1, end_row=200, start_col="A", end_col="Z")
        self.assertTrue(range_name != u"blah!A1:Z200")
    
    def test_col_letter_to_index(self):
        pass


if __name__ == '__main__':
    unittest.main()
