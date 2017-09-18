# -*- coding: utf-8 -*-

import os
import re
import io
import string
import google_spreadsheet as sheet_api
import pseudo_localization as pseudo

# ---------- const ----------

LANG_EN = 'EN'
LANG_TW = 'TW'
LANG_HK = 'HK'
LANG_CN = 'CN'
LANG_JP = 'JP'
LANG_KR = 'KR'
LANG_THAI = 'THAI'
LANG_BASE = LANG_EN

# ---------- utility ----------

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def is_mostly_ascii(s):
    return sum(ord(c) < 128 for c in s) >= (len(s) * 2 / 3)

def col_letter_to_index(letter):
    return string.ascii_uppercase.index(letter.upper())

def print_entries(entries):
    for index, entry in enumerate(entries):
        print(u"{0}. {1}".format(index+1, entry.key))
        for lang, value in entry.values.iteritems():
            print(u"[{0}]: {1}".format(lang, value))

def print_entries_key_only(entries):
    for index, entry in enumerate(entries):
        print(u"{0}. {1}".format(index+1, entry.key))

# ---------- manager / model ----------

class LanguageMapping(object):
    def __init__(self):
        self.language = None
        self.spreadsheet_key = None
        self.spreadsheet_value = None
        self.app_key = None
        self.app_value = None

class SpreadSheetEntry(object):
    def __init__(self):
        self.key = None
        self.values = dict()

class SpreadSheetManager(object):
    def __init__(self):
        self.spreadsheet_id = None
        self.sheet_name = None
        self.sheet_start_row = None
        self.sheet_last_row = None
        self.sheet_start_col = None
        self.sheet_last_col = None
        self.language_cols = None
        self.key_col = None
    
    @classmethod
    def default_manager(cls):
        manager = cls()
        manager.spreadsheet_id = '1LvdhIPABjW_zCMXyfXZiQbcYFPTYlmkb5K0KpXkRN9c'
        manager.sheet_name = u'「Round2-all」new'
        manager.sheet_start_row = 4
        manager.sheet_last_row = 800
        manager.sheet_start_col = 'A'
        manager.sheet_last_col = 'R'
        manager.language_cols = {LANG_EN:'K', 
                                 LANG_TW:'J',
                                 LANG_HK:'L',
                                 LANG_CN:'M',
                                 LANG_JP:'N',
                                 LANG_KR:'O',
                                 LANG_THAI:'P'}
        # convert cols from letter to index
        for key, val in manager.language_cols.iteritems():
            manager.language_cols[key] = col_letter_to_index(val)
        manager.key_col = manager.language_cols[LANG_TW]
        return manager
    
    def load_spreadsheet_entries(self):
        service = sheet_api.deal_with_auth_and_prepare_api_service()
        range_name = u'{0}!{1}{2}:{3}{4}'.format(self.sheet_name,
                                                 self.sheet_start_col, self.sheet_start_row,
                                                 self.sheet_last_col, self.sheet_last_row)
        values = sheet_api.read_spreadsheet_values(service, self.spreadsheet_id, range_name)
        entries = []
        if not values:
            print('No data found from reading google localization spreadsheet'
                  '\nSpreadsheet id: {0} sheet name: {1}'.format(self.spreadsheet_id, self.sheet_name))
            return entries
        for row in values:
            entry = SpreadSheetEntry()
            entry.key = row[self.key_col]
            for lang, col in self.language_cols.iteritems():
                value = row[col].strip('\n') if len(row) > col else ""
                entry.values[lang] = value
            entries.append(entry)
            # break
        return entries

class StringsEntry(object):
    def __init__(self):
        self.key = None
        self.values = dict()
            
class LocalizationStringsManager(object):
    def __init__(self):
        self.app_dir = None
        self.languages = None
        self.base_lang = None

    @classmethod
    def default_manager(cls):
        manager = cls()
        manager.app_dir = pseudo.ROOT_DIR
        manager.languages = {LANG_EN:pseudo.BASE_DIR, 
                             LANG_TW:pseudo.TW_DIR,
                             LANG_HK:pseudo.HK_DIR,
                             LANG_CN:pseudo.CN_DIR,
                             LANG_JP:pseudo.JP_DIR,
                             LANG_KR:pseudo.KR_DIR,
                             LANG_THAI:pseudo.THAI_DIR}
        manager.base_lang = LANG_EN
        return manager
    
    def load_strings_entries(self):
        entries = dict()
        p = re.compile(r'^(?!\/\/).*"(.*?[^\\])"[ ]*=[ ]*"(.*?[^\\])(".*)')
        for lang, lang_dir in self.languages.iteritems():
            dir_path = os.path.join(self.app_dir, lang_dir)
            strings_file_path = os.path.join(dir_path, 'Localizable.strings')
            # open and scan the file
            with io.open(strings_file_path, encoding='utf8') as reader:
                for line in reader:
                    matched = p.match(line)
                    if matched:
                        key = matched.group(1)
                        val = matched.group(2)
                        entry = entries.get(key)
                        if not entry:
                            entry = StringsEntry()
                            entry.key = key
                            entries[key] = entry
                        entry.values[lang] = val
        return entries.values()

# ---------- testing ----------

def test_load_spreadsheet_entries():
    print("---- test loading spreadsheet entries ----")
    manager = SpreadSheetManager.default_manager()
    entries = manager.load_spreadsheet_entries()
    print_entries(entries)

def test_load_strings_entries():
    print("---- test loading strings entries ----")
    manager = LocalizationStringsManager.default_manager()
    entries = manager.load_strings_entries()
    print_entries(entries)

# ---------- analysis ----------

def find_english_only_localization():
    print("---- find english only localization ----")
    manager = LocalizationStringsManager.default_manager()
    entries = manager.load_strings_entries()
    suspect = []
    for entry in entries:
        value = entry.values.get(LANG_TW)
        if is_ascii(value):
            suspect.append(entry)
    print_entries(suspect)

def find_not_translated_entries():
    print("---- find not translated entries in english ----")
    manager = LocalizationStringsManager.default_manager()
    entries = manager.load_strings_entries()
    suspect = []
    for entry in entries:
        value = entry.values.get(LANG_EN)
        if not is_mostly_ascii(value):
            suspect.append(entry)
    print_entries_key_only(suspect)

# ---------- main ----------

def main():
    # test_load_spreadsheet_entries()
    # test_load_strings_entries()
    # find_english_only_localization()
    find_not_translated_entries()

if __name__ == '__main__':
    main()