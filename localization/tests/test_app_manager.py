# -*- coding: utf-8 -*-

import unittest
import os

from .context import localization_helper

class AppManagerTestSuite(unittest.TestCase):

    def setUp(self):
        self.manager = localization_helper.AppManager()

    def tearDown(self):
        self.manager = None

    def test_read_localization_strings_file(self):
        filename = 'tests/data/test_data_Localizable.strings'
        results = self.manager.read_localization_strings_file(filename)
        key, val, _ = results[16]
        self.assertTrue(key == u"%d 個" and val == u"%d")
        key, val, _ = results[14]
        self.assertTrue(key == u"%d - %d day(s)" and val == u"%d - %d day(s)")
        key, val, line = results[6]
        self.assertTrue(key is None and val is None and line == "*/\n")

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

    def test_create_strings_file_entry_with_new_val(self):
        line = u'"%@ 項搜尋結果" = "%@ Results"; //no match'
        val = u'%@ Results'
        new_val = u'eeedededaaaa項搜尋結果'
        expected = u'"%@ 項搜尋結果" = "eeedededaaaa項搜尋結果"; //no match'
        result = self.manager.create_strings_file_entry_with_new_val(key=u'%@ 項搜尋結果', value=val, new_value=new_val, line=line)
        self.assertTrue(result == expected)

    def test_update_localization_strings_file(self):
        filename = 'tests/data/test_data_Localizable.strings'
        updated_filename = 'tests/data/updated_Localizable.strings_tmp'
        def update_callback(key, val, line):
            new_val = None
            if key == u'KKday官網':
                new_val = self.manager.create_strings_file_entry_with_new_val(key=key, value=val, new_value="abc.com", line=line)
            return new_val
        updated = self.manager.update_localization_strings_file(filename=filename, update_callback=update_callback)
        localization_helper.write_file(updated_filename, updated)
        # test load
        original_file_entries = self.manager.read_localization_strings_file(filename)
        updated_file_entries = self.manager.read_localization_strings_file(updated_filename)
        original_diff_updated = list(set(original_file_entries) - set(updated_file_entries))
        updated_diff_original = list(set(updated_file_entries) - set(original_file_entries))
        self.assertTrue(len(original_diff_updated) == 1)
        self.assertTrue(len(updated_diff_original) == 1)
        original_key, original_val, _ = original_diff_updated[0]
        updated_key, updated_val, _ = updated_diff_original[0]
        self.assertTrue(original_key == updated_key)
        self.assertTrue(original_val == "KKday.com")
        self.assertTrue(updated_val == "abc.com")
    
    def test_update_localizable_strings(self):
        languages = ["EN"]
        language_dirs = {
            "EN": "Base.lproj",
        }
        project_dir = 'tests/data/kkday-ios-member'
        def update_val_callback(lang, key, val, line):
            if lang == "EN":
                if key == u"KKday官網":
                    return u"www.google.com"
            return None
        def end_of_file_callback(lang, edited_lines, dir_path, filename, full_path):
            updated_filename = os.path.join(dir_path, filename+"_updated")
            localization_helper.write_file(updated_filename, edited_lines)
            # verify
            updated_file_entries = self.manager.read_localization_strings_file(updated_filename)
            only_one_diff = [(key, val) for key, val, line in updated_file_entries if key == u"KKday官網"]
            self.assertTrue(len(only_one_diff) == 1)
            key, val = only_one_diff[0]
            self.assertTrue(val == u"www.google.com")
        self.manager.update_localizable_strings(languages=languages, 
                                                language_dirs=language_dirs, 
                                                project_dir=project_dir, 
                                                update_val_callback=update_val_callback, 
                                                end_of_file_callback=end_of_file_callback)

if __name__ == '__main__':
    unittest.main()
