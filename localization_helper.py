# -*- coding: utf-8 -*-

from __future__ import print_function
import httplib2
import os
import re
import io
import glob
import string
import google_spreadsheet as sheet_api
import pseudo_localization as pseudo

LANG_EN = 'EN'
LANG_TW = 'TW'
LANG_HK = 'HK'
LANG_CN = 'CN'
LANG_JP = 'JP'
LANG_KR = 'KR'
LANG_THAI = 'THAI'
LANG_BASE = LANG_EN

SHEET_COL_INDEX_TW = 'D'
SHEET_COL_INDEX_ENG = 'J'
SHEET_COL_INDEX_HK = 'K'
SHEET_COL_INDEX_CHINA = 'L'
SHEET_COL_INDEX_JP = 'M'
SHEET_COL_INDEX_KR = 'N'
SHEET_COL_INDEX_THAI = 'O'

KKDAY_MASTER_SPREADSHEET_ID = '1LvdhIPABjW_zCMXyfXZiQbcYFPTYlmkb5K0KpXkRN9c'
TARGET_SHEET_IN_MASTER_SPREADSHEET_NAME = u'「Round2-all」new'
TARGET_SHEET_IN_MASTER_SPREADSHEET_ID = 1459690949
WORKPLACE_SPREADSHEET_ID = '1Lz1xyKtMSjRq-g9itthcl-kBXzPJzKzAjYo11ME7wTo'
TESTING_SPREADSHEET_ID = '19u7O-5x3ZsV2oD3ruxrfm6xERvULnFv_mKaQIL8V88w'

SHEET_STARTING_ROW = 4
SHEET_LAST_ROW = 800
SHEET_STARTING_COL = 'A'
SHEET_LAST_COL = 'R'

def copy_sheet(service, source_spreadsheet_id, source_sheet_id, destination_spreadsheet_id):
    result = service.spreadsheets().sheets().copyTo(spreadsheetId=source_spreadsheet_id, 
                                                    sheetId=source_sheet_id, 
                                                    body={"destinationSpreadsheetId": destination_spreadsheet_id}, 
                                                    x__xgafv=None).execute()
    return result

def make_master_sheet_copy_to_workplace(service):
    print("---- create a copy from master spreadsheet to workplace ----")
    result = copy_sheet(service, 
                        KKDAY_MASTER_SPREADSHEET_ID, 
                        TARGET_SHEET_IN_MASTER_SPREADSHEET_ID, 
                        WORKPLACE_SPREADSHEET_ID)
    print(u"copied sheet id: {0} title: {1}".format(result.get('sheetId', 'n/a'),
                                                   result.get('title', 'n/a')))
    print("---- copy completed ----")

def read_spreadsheet(service, spreadsheetId, range):
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, 
                                                 range=range).execute()
    values = result.get('values', [])
    return values

def col_letter_to_index(letter):
    return string.ascii_uppercase.index(letter.upper())

class LanguageKey(object):
    def __init__(self, key, col, dir):
        self.key = key
        self.spreadsheet_col = col
        self.spreadsheet_index = col_letter_to_index(col)
        self.app_dir = dir

    @classmethod
    def eng(cls):
        return cls(LANG_EN, SHEET_COL_INDEX_ENG, pseudo.BASE_DIR)
    
    @classmethod
    def tw(cls):
        return cls(LANG_TW, SHEET_COL_INDEX_TW, pseudo.TW_DIR)

    @classmethod
    def hk(cls):
        return cls(LANG_HK, SHEET_COL_INDEX_HK, pseudo.HK_DIR)

    @classmethod
    def china(cls):
        return cls(LANG_CN, SHEET_COL_INDEX_CHINA, pseudo.CN_DIR)

    @classmethod
    def jp(cls):
        return cls(LANG_JP, SHEET_COL_INDEX_JP, pseudo.JP_DIR)
    
    @classmethod
    def kr(cls):
        return cls(LANG_KR, SHEET_COL_INDEX_KR, pseudo.KR_DIR)

    @classmethod
    def thai(cls):
        return cls(LANG_THAI, SHEET_COL_INDEX_THAI, pseudo.THAI_DIR)

class SpreadSheetEntry(object):
    def __init__(self):
        self.key = ''
        self.values = dict()

class SpreadSheetManager(object):
    def __init__(self, languages, key_language):
        self.lookup_table = dict()
        self.languages = languages
        self.key_language = key_language
    
    def load_localization_spreadsheet(self):
        service = sheet_api.deal_with_auth_and_prepare_api_service()
        spreadsheetId = KKDAY_MASTER_SPREADSHEET_ID
        rangeName = u'{0}!{1}{2}:{3}{4}'.format(TARGET_SHEET_IN_MASTER_SPREADSHEET_NAME,
                                                SHEET_STARTING_COL, SHEET_STARTING_ROW,
                                                SHEET_LAST_COL, SHEET_LAST_ROW)
        values = read_spreadsheet(service, spreadsheetId, rangeName)
        if not values:
            print('No data found from reading google localization spreadsheet')
            return
        for row in values:
            common_key = row[self.key_language.spreadsheet_index]
            entry = SpreadSheetEntry()
            entry.key = common_key
            self.lookup_table[common_key] = entry
            for lang in self.languages:
                entry.values[lang.key] = row[lang.spreadsheet_index].strip('\n')
    
    def print_spreadsheet(self):
        print('---- localization info in spreadsheet ----')
        for key, entry in self.lookup_table.iteritems():
            print(u'key: {0}'.format(key))
            for lang in self.languages:
                print(u'[{0}]: {1}'.format(lang.key, entry.values[lang.key]))

class LocalizationStringsEntry(object):
    def __init__(self):
        self.key = ''
        self.values = dict()

class LocalizationStringsManager(object):
    def __init__(self, languages):
        self.lookup_table = dict()
        self.languages = languages
    
    def scan_strings_files(self):
        for lang in self.languages:
            dir_path = os.path.join(pseudo.ROOT_DIR, lang.app_dir)
            strings_file_path = os.path.join(dir_path, 'Localizable.strings')
            # open and scan the file
            p = re.compile(r'.*"(.*?[^\\])"[ ]*=[ ]*"(.*?[^\\])(".*)')
            with io.open(strings_file_path, encoding='utf8') as reader:
                for line in reader:
                    matched = p.match(line)
                    if matched:
                        key = matched.group(1)
                        val = matched.group(2)
                        entry = self.lookup_table.get(key)
                        if not entry:
                            entry = LocalizationStringsEntry()
                            entry.key = key
                            self.lookup_table[key] = entry
                        entry.values[lang.key] = val
    
    def find_duplicate_in_localization_strings(self, lang):
        dir_path = os.path.join(pseudo.ROOT_DIR, lang.app_dir)
        strings_file_path = os.path.join(dir_path, 'Localizable.strings')
        # open and scan the file
        p = re.compile(r'.*"(.*?[^\\])"[ ]*=[ ]*"(.*?[^\\])(".*)')
        with io.open(strings_file_path, encoding='utf8') as reader:
            bookkeeper = dict()
            line_number = 0
            for line in reader:
                matched = p.match(line)
                if matched:
                    key = matched.group(1)
                    val = matched.group(2)
                    record = bookkeeper.get(key)
                    if not record:
                        record = []
                        bookkeeper[key] = record
                    record.append(line_number)
                line_number += 1
        print('----')
                    


    
    def update_strings_files(self, spreadsheet_manager):
        for lang in self.languages:
            dir_path = os.path.join(pseudo.ROOT_DIR, lang.app_dir)
            strings_file_path = os.path.join(dir_path, 'Localizable.strings')
            file_to_write = strings_file_path + '.tmp'
            # remove tmp file
            if os.path.exists(file_to_write):
                os.remove(file_to_write)
            # open and scan the file
            p = re.compile(r'.*"(.*?[^\\])"[ ]*=[ ]*"(.*?[^\\])(".*)')
            with io.open(strings_file_path, encoding='utf8') as reader:
                pattern = r'(.*=[ ]*")(.*?[^\\])(".*)'
                with io.open(file_to_write, mode='w', encoding='utf8') as writer:
                    for line in reader:
                        matched = p.match(line)
                        if matched:
                            key = matched.group(1)
                            val = matched.group(2)
                            # check value in spreadsheet manager
                            spreadsheet_entry = spreadsheet_manager.lookup_table.get(key)
                            spreadsheet_val = spreadsheet_entry.values.get(lang.key) if spreadsheet_entry else None
                            # process line change
                            def adjust_line(matchobj):
                                translation_value = spreadsheet_val or matchobj.group(2)
                                # append comment to end if needed
                                adjusted_line = ''.join([matchobj.group(1),
                                                         translation_value,
                                                         matchobj.group(3)])
                                if spreadsheet_val is None and not adjusted_line.endswith(u' //no match'):
                                    adjusted_line += ' //no match'
                                elif spreadsheet_val and adjusted_line.endswith(u' //no match'):
                                    adjusted_line = adjusted_line.replace(u' //no match', '')
                                return adjusted_line
                            modified = re.sub(pattern, adjust_line, line)
                            writer.write(modified)
                        else:
                            # doesn't contain localization entry, just write it as it is
                            writer.write(line)
            # replace original file with tmp file
            os.remove(strings_file_path)
            os.rename(file_to_write, strings_file_path)
    
    def print_localization_strings(self):
        print('---- localization info in app localization strings ----')
        for key, entry in self.lookup_table.iteritems():
            print(u'key: {0}'.format(key))
            for lang in self.languages:
                print(u'[{0}]: {1}'.format(lang.key, entry.values[lang.key]))


def test_reading_speadsheet():
    supporting_langs = [LanguageKey.china(),
                        LanguageKey.eng(),
                        LanguageKey.hk(),
                        LanguageKey.jp(),
                        LanguageKey.kr(),
                        LanguageKey.thai(),
                        LanguageKey.tw()]
    key_lang = LanguageKey.tw()
    spreadsheet_manager = SpreadSheetManager(supporting_langs, key_lang)
    spreadsheet_manager.load_localization_spreadsheet()
    spreadsheet_manager.print_spreadsheet()

def test_reading_localization_strings():
    supporting_langs = [LanguageKey.china(),
                        LanguageKey.eng(),
                        LanguageKey.hk(),
                        LanguageKey.jp(),
                        LanguageKey.kr(),
                        LanguageKey.thai(),
                        LanguageKey.tw()]
    localization_strings_manager = LocalizationStringsManager(supporting_langs)
    localization_strings_manager.scan_strings_files()
    localization_strings_manager.print_localization_strings()

def compare_localization_strings_with_spreadsheet():
    # languages to compare
    supporting_langs = [LanguageKey.china(),
                        LanguageKey.eng(),
                        LanguageKey.hk(),
                        LanguageKey.jp(),
                        LanguageKey.kr(),
                        LanguageKey.thai(),
                        LanguageKey.tw()]
    # read spreadsheet
    key_lang = LanguageKey.tw()
    spreadsheet_manager = SpreadSheetManager(supporting_langs, key_lang)
    spreadsheet_manager.load_localization_spreadsheet()
    # read localization strings
    localization_strings_manager = LocalizationStringsManager(supporting_langs)
    localization_strings_manager.scan_strings_files()
    # make change
    print('---- make change ----')
    localization_strings_manager.update_strings_files(spreadsheet_manager)
    print('---- done make change ----')
    # compare
    print('---- compare localization strings with spreadsheet strings ----')
    stats_missing_in_spreadsheet = []
    stats_completely_matched = []
    stats_partial_matched = []
    for key, entry in localization_strings_manager.lookup_table.iteritems():
        print(u'-- key: {0}'.format(key))
        spreadsheet_entry = spreadsheet_manager.lookup_table.get(key)
        if not spreadsheet_entry:
            stats_missing_in_spreadsheet.append(key)
        match_counter = 0
        for lang in supporting_langs:
            strings_val = entry.values.get(lang.key, 'missing')
            spreadsheet_val = None
            if spreadsheet_entry:
                spreadsheet_val = spreadsheet_entry.values.get(lang.key, 'missing')
            if strings_val == spreadsheet_val:
                print(u'[{0}][matched]: {1}'.format(lang.key, strings_val))
                match_counter += 1
            else:
                print(u'[{0}]: {1} --> {2}'.format(lang.key, strings_val, spreadsheet_val))
        if match_counter == len(supporting_langs):
            stats_completely_matched.append(key)
        elif match_counter > 1:
            stats_partial_matched.append(key)
    print('---- stats ----')
    print('missing translation in spreadsheet: {0}'.format(len(stats_missing_in_spreadsheet)))
    print('complete matched: {0}'.format(len(stats_completely_matched)))
    print('partial match: {0}'.format(len(stats_partial_matched)))
    print('---- missing translation ----')
    for index, key in enumerate(stats_missing_in_spreadsheet):
        print(u'{0}.---- {1} ----'.format(index+1, key))
        # entry = localization_strings_manager.lookup_table.get(key)
        # for lang in supporting_langs:
        #     strings_val = entry.values.get(lang.key)
        #     print(u'[{0}]: {1}'.format(lang.key, strings_val))
    print('---- partial translation ----')
    for index, key in enumerate(stats_partial_matched):
        print(u'{0}.---- {1} ----'.format(index+1, key))
        entry = localization_strings_manager.lookup_table.get(key)
        spreadsheet_entry = spreadsheet_manager.lookup_table.get(key)
        for lang in supporting_langs:
            strings_val = entry.values.get(lang.key)
            spreadsheet_val = spreadsheet_entry.values.get(lang.key)
            if strings_val == spreadsheet_val:
                print(u'[{0}][matched]'.format(lang.key))
            else:
                print(u'[{0}]: {1} --> {2}'.format(lang.key, strings_val, spreadsheet_val))

def find_unused_localization_string():
    # search all swift file for list of strings thats no match in 
    # firstly read the base.strings to get list of localization key value pairs
    print('---- load localization strings ----')
    base_lang = LanguageKey.eng()
    localization_strings_manager = LocalizationStringsManager([base_lang])
    localization_strings_manager.scan_strings_files()
    # next to search all the swift file
    localization_key_usage = dict()
    root_dir = '/Users/jason/Desktop/projects/kkday-ios-member/Solution/kkday-ios-member'
    list_dir = ['kkday-ios-member','Library','ValueTypesFramework', 'WebAPI']
    print('---- start scanning swift files ----')
    for dir in list_dir:
        for file in glob.glob('{0}/{1}/*.swift'.format(root_dir, dir)):
            print(file)
            with io.open(file, encoding='utf8') as f:
                contents = f.read()
                # print(u'content: {0}'.format(contents))
                for key, val in localization_strings_manager.lookup_table.iteritems():
                    search_term = u'"{0}".'.format(key)
                    counter = localization_key_usage.get(key)
                    if not counter:
                        localization_key_usage[key] = 0
                    # print(u'searching...{0}'.format(search_term))
                    if search_term in contents:
                        localization_key_usage[key] += 1
    print('---- scan result ----')
    print('key not used by code')
    index = 1
    for key, val in localization_key_usage.iteritems():
        if val == 0:
            print(u'{0}. {1}'.format(index, key))
            index += 1

def analyze_no_match_with_unused_localization_strings():
    # read unusued
    unusued_store = set()
    pattern = re.compile(r'^\d+\.\s*(.*)')
    with io.open('tmp/localization_not_use_by_app.txt', encoding='utf8') as reader:
        for line in reader:
            matched = pattern.match(line)
            if matched:
                key = matched.group(1)
                unusued_store.add(key)
    # read no match
    no_match = set()
    pattern = re.compile(r'^\d+\.---- (.*) ----')
    with io.open('tmp/no_match_localization.txt', encoding='utf8') as reader:
        for line in reader:
            matched = pattern.match(line)
            if matched:
                key = matched.group(1)
                no_match.add(key)
    # compare
    print('---- spreadsheet 找不到的翻譯(但程式碼也沒有用到, 可忽略) ----')
    no_match_and_unused = no_match.intersection(unusued_store)
    for index, key in enumerate(no_match_and_unused):
        print(u'{0}. {1}'.format(index+1, key))
    print('---- spreadsheet 找不到的翻譯(但程式碼有用到) ----')
    no_match_but_used_localization = no_match.difference(unusued_store)
    for index, key in enumerate(no_match_but_used_localization):
        print(u'{0}. {1}'.format(index+1, key))
    

if __name__ == '__main__':
    # test_reading_speadsheet()
    # test_reading_localization_strings()
    # compare_localization_strings_with_spreadsheet()
    # find_unused_localization_string()
    analyze_no_match_with_unused_localization_strings()