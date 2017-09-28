# -*- coding: utf-8 -*-

import unittest

from .context import localization_helper

class AppManagerTestSuite(unittest.TestCase):
    
    def setUp(self):
        self.manager = localization_helper.AppManager()
    
    def tearDown(self):
        self.manager = None
    
    def test_read_localization_strings_file(self):
        filename = 'tests/data/Localizable.strings'
        results = self.manager.read_localization_strings_file(filename)
        key, val = results[6]
        self.assertTrue(key == u"%d 個" and val == u"%d")
        key, val = results[4]
        self.assertTrue(key == u"%d - %d day(s)" and val == u"%d - %d day(s)")
    
    def test_load_localizable_strings(self):
        languages = ["EN", "TW", "HK", "CN", "JP", "KR", "THAI"]
        language_dirs = {
            "EN": "Base.lproj",
            "TW": "zh-Hant-TW.lproj",
            "HK": "zh-Hant-HK.lproj",
            "CN": "zh-Hans.lproj",
            "JP": "ja.lproj",
            "KR": "ko.lproj",
            "THAI": "th.lproj"
        }
        project_dir = 'tests/data/kkday-ios-member'
        entries = self.manager.load_localizable_strings(languages=languages, 
                                                        language_dirs=language_dirs, 
                                                        project_dir=project_dir)
        entry = [e for e in entries if e.key == u'TourTitle0'][0]
        self.assertTrue(entry.key == u'TourTitle0' and entry.values['THAI'] == u'ระบบยืนยันการจองที่รวดเร็ว')
        entry = [e for e in entries if e.key == u'key that does not exist'] or None
        self.assertTrue(entry is None)
    
    def test_load_storyboard_strings(self):
        languages = ["EN", "TW", "HK", "CN", "JP", "KR", "THAI"]
        language_dirs = {
            "EN": "en.lproj",
            "TW": "zh-Hant-TW.lproj",
            "HK": "zh-Hant-HK.lproj",
            "CN": "zh-Hans.lproj",
            "JP": "ja.lproj",
            "KR": "ko.lproj",
            "THAI": "th.lproj"
        }
        project_dir = 'tests/data/kkday-ios-member'
        entries = self.manager.load_storyboard_strings(languages=languages, 
                                                       language_dirs=language_dirs, 
                                                       project_dir=project_dir)
        entry = [e for e in entries if e.key == u'VL8-qR-Fsi.title'][0]
        self.assertTrue(entry.values['HK'] == u'重選' and entry.values['KR'] == u'재선택')
    
    def test_read_write_json(self):
        languages = ["EN", "TW", "HK", "CN", "JP", "KR", "THAI"]
        language_dirs = {
            "EN": "en.lproj",
            "TW": "zh-Hant-TW.lproj",
            "HK": "zh-Hant-HK.lproj",
            "CN": "zh-Hans.lproj",
            "JP": "ja.lproj",
            "KR": "ko.lproj",
            "THAI": "th.lproj"
        }
        project_dir = 'tests/data/kkday-ios-member'
        entries = self.manager.load_storyboard_strings(languages=languages, 
                                                       language_dirs=language_dirs, 
                                                       project_dir=project_dir)
        filename = "workspace/tmp_entries.json"
        self.manager.save_entries_to_disk(entries=entries, filename=filename)
        read_entries = self.manager.load_entries_from_disk(filename)
        self.assertTrue(entries == read_entries)
        language_dirs = {
            "EN": "Base.lproj",
            "TW": "zh-Hant-TW.lproj",
            "HK": "zh-Hant-HK.lproj",
            "CN": "zh-Hans.lproj",
            "JP": "ja.lproj",
            "KR": "ko.lproj",
            "THAI": "th.lproj"
        }
        localizable_entries = self.manager.load_localizable_strings(languages=languages, 
                                                                    language_dirs=language_dirs, 
                                                                    project_dir=project_dir)
        self.assertFalse(read_entries == localizable_entries)
        

if __name__ == '__main__':
    unittest.main()