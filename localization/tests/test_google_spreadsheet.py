# -*- coding: utf-8 -*-

import unittest

from .context import localization_helper
from .context import remove_if_exist

class GoogleSpreadsheetTestSuite(unittest.TestCase):
    
    def setUp(self):
        self.config = localization_helper.Config(file_path='workspace/config.json')
        scope = self.config.get("spreadsheet.google.scope")
        secret = "workspace/" + self.config.get("spreadsheet.google.secret")
        self.api = localization_helper.spreadsheet_api.deal_with_auth_and_prepare_api_service(client_secret_file=secret, scopes=scope)
    
    def tearDown(self):
        self.config = None
        self.api = None

    def test_auth(self):
        # delete the auth
        remove_if_exist('~/.credentials/sheets.googleapis.localization.json')
        spreadsheet_id = self.config.get("spreadsheet.spreadsheetId")
        spreadsheet_range = self.config.get("spreadsheet.sheetName")
        results = localization_helper.spreadsheet_api.read_spreadsheet_values(service=self.api, spreadsheet_id=spreadsheet_id, range=spreadsheet_range)
        self.assertIsNotNone(results)
    

if __name__ == '__main__':
    unittest.main()
