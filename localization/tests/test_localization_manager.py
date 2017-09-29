# -*- coding: utf-8 -*-

import unittest

from .context import localization_helper

class LocalizationManagerTestSuite(unittest.TestCase):
    
    def setUp(self):
        self.manager = localization_helper.LocalizationManager()
    
    def tearDown(self):
        self.manager = None
    
    def test_compare_entry(self):
        languages = ["EN", "TW", "HK", "CN", "JP", "KR", "THAI"]
        sheet_entry = localization_helper.SpreadSheetEntry()
        sheet_entry.key = u'ok'
        sheet_entry.values = {
            "EN": u"More",
            "TW": u"更多",
            "HK": u"更多",
            "CN": u"更多",
            "JP": u"もっと探そう",
            "KR": u"더 읽기",
            "THAI": u"เพิ่มเติม"
        }
        app_entry = localization_helper.StringsEntry()
        app_entry.key = u'key diff doesnt matter'
        app_entry.values = {
            "EN": u"More",
            "TW": u"更多",
            "HK": u"更多",
            "CN": u"更多",
            "JP": u"もっと探そう",
            "KR": u"더 읽기",
            "THAI": u"เพิ่มเติม"
        }
        diff = self.manager.compare_entries(sheet_entry=sheet_entry, app_entry=app_entry, languages=languages)
        self.assertFalse(bool(diff))
        sheet_entry.values = {
            "EN": u"更多",
            "TW": u"沒了",
            "HK": u"更多",
            "CN": u"更多",
            "JP": u"もっと探そう",
            "KR": u"더 읽기",
            "THAI": u"เพิ่มเติม"
        }
        diff = self.manager.compare_entries(sheet_entry=sheet_entry, app_entry=app_entry, languages=languages)
        expected = {
            "EN": {
                'app': u"More",
                'sheet': u"更多"
            },
            "TW": {
                'app': u"更多",
                'sheet': u"沒了"
            }
        }
        self.assertTrue(diff == expected)
    
    def test_analyze_diff_between_app_and_spreadsheet(self):
        # load data
        sheet_manager = localization_helper.SpreadSheetManager()
        sheet_entries = sheet_manager.load_entries_from_disk(filename='tests/data/test_data_sheet.json')
        app_manager = localization_helper.AppManager()
        app_localizable_entries = app_manager.load_entries_from_disk(filename='tests/data/test_data_localizable.json')
        app_storyboard_entries = app_manager.load_entries_from_disk(filename='tests/data/test_data_storyboard.json')
        # analyze diff
        languages = ["EN", "TW", "HK", "CN", "JP", "KR", "THAI"]
        mapping = localization_helper.LocalizationMapping(use_key_for_mapping=False, mapping_language="TW")
        diff_entries, app_only_entries, sheet_only_entries = self.manager.analyze_diff_between_app_and_spreadsheet(sheet_entries=sheet_entries,
                                                                      app_entries=app_localizable_entries + app_storyboard_entries, 
                                                                      mapping=mapping, 
                                                                      languages=languages)
        self.manager.save_analyze_diff_to_disk(diff_type='diff', result=diff_entries, filename='tests/data/test_data_analyze_diff.json')
        self.manager.save_analyze_diff_to_disk(diff_type='app only', result=app_only_entries, filename='tests/data/test_data_analyze_app_only.json')
        self.manager.save_analyze_diff_to_disk(diff_type='sheet only', result=sheet_only_entries, filename='tests/data/test_data_analyze_sheet_only.json')
        self.assertTrue(diff_entries)
    
    def test_apply_whitelist_to_anlyze_diff(self):
        # load data
        diff_entries = self.manager.load_analyze_diff_from_disk(diff_type='diff', filename='tests/data/test_data_analyze_diff.json')
        languages = ["EN", "TW", "HK", "CN", "JP", "KR", "THAI"]
        # apply white list
        adjusted_diff_entries = self.manager.apply_whitelist_to_analyze_diff(whitelist_filename='tests/data/test_data_whitelist.json', 
                                                                             diff_entries=diff_entries, 
                                                                             languages=languages)
        # save
        self.manager.save_analyze_diff_to_disk(diff_type='diff', result=adjusted_diff_entries, filename='tests/data/test_data_whitelisted_analyze_diff.json')
        self.assertTrue(adjusted_diff_entries)

if __name__ == '__main__':
    unittest.main()




        # sheet_manager = localization_helper.SpreadSheetManager()
        # # download spreadsheet
        # scopes = 'https://www.googleapis.com/auth/spreadsheets.readonly'
        # secret_file = './workspace/client_secret.json'
        # spreadsheet_id = '1LvdhIPABjW_zCMXyfXZiQbcYFPTYlmkb5K0KpXkRN9c'
        # range_name = u'「Round2-all」new!A4:R800'
        # rows = sheet_manager.download_spreadsheet(scopes=scopes, 
        #                                           secret_file=secret_file, 
        #                                           spreadsheet_id=spreadsheet_id, 
        #                                           range_name=range_name)
        # # parse spreadsheet
        # lang_mapping = {
        #     "EN": "L",
        #     "TW": "K",
        #     "HK": "M",
        #     "CN": "N",
        #     "JP": "O",
        #     "KR": "P",
        #     "THAI": "Q"
        # }
        # key_lang = "TW"
        # entries = sheet_manager.parse_spreadsheet(spreadsheet_rows=rows, 
        #                                           key_lang=key_lang, 
        #                                           lang_col_mapping=lang_mapping)
        # # save result to disk
        # sheet_manager.save_entries_to_disk(entries=entries, filename='test_data_sheet.json')

        # load localizable strings
        # app_manager = localization_helper.AppManager()
        # languages = ["EN", "TW", "HK", "CN", "JP", "KR", "THAI"]
        # language_dirs = {
        #     "EN": "Base.lproj",
        #     "TW": "zh-Hant-TW.lproj",
        #     "HK": "zh-Hant-HK.lproj",
        #     "CN": "zh-Hans.lproj",
        #     "JP": "ja.lproj",
        #     "KR": "ko.lproj",
        #     "THAI": "th.lproj"
        # }
        # project_dir = 'tests/data/kkday-ios-member'
        # entries = app_manager.load_localizable_strings(languages=languages, 
        #                                                language_dirs=language_dirs, 
        #                                                project_dir=project_dir)
        # app_manager.save_entries_to_disk(entries=entries, filename='tests/data/test_data_localizable.json')
        # self.assertTrue(len(entries))
        # # load storyboard strings
        # language_dirs = {
        #     "EN": "en.lproj",
        #     "TW": "zh-Hant-TW.lproj",
        #     "HK": "zh-Hant-HK.lproj",
        #     "CN": "zh-Hans.lproj",
        #     "JP": "ja.lproj",
        #     "KR": "ko.lproj",
        #     "THAI": "th.lproj"
        # }
        # entries = app_manager.load_storyboard_strings(languages=languages, 
        #                                               language_dirs=language_dirs, 
        #                                               project_dir=project_dir)
        # app_manager.save_entries_to_disk(entries=entries, filename='tests/data/test_data_storyboard.json')
        # self.assertTrue(len(entries))
        # save to disk