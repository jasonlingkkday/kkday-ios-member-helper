# -*- coding: utf-8 -*-

# note:
# need pip2 install unicodecsv

import os
import re
import io
import string
import json
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

def print_entries(entries, limit=0):
    for index, entry in enumerate(entries):
        print(u"{0}. {1}".format(index+1, entry.key))
        for lang, value in entry.values.iteritems():
            print(u"[{0}]: {1}".format(lang, value))
        if limit and index + 1 >= limit:
            break 

def print_entries_key_only(entries):
    for index, entry in enumerate(entries):
        print(u"{0}. {1}".format(index+1, entry.key))

def print_mappings(mappings, limit=0, print_key_only=False):
    for index, mapping in enumerate(mappings):
        print(u'key: {0}'.format(mapping.key))
        print(' - spreadsheet entry:')
        if print_key_only:
            print_entries_key_only(mapping.spreadsheet_entries)
        else:
            print_entries(mapping.spreadsheet_entries)
        print(' - strings entry:')
        if print_key_only:
            print_entries_key_only(mapping.strings_entries)
        else:
            print_entries(mapping.strings_entries)
        if limit and index + 1 >= limit:
            break

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
    
    @classmethod
    def default_manager(cls):
        manager = cls()
        manager.spreadsheet_id = '1LvdhIPABjW_zCMXyfXZiQbcYFPTYlmkb5K0KpXkRN9c'
        manager.sheet_name = u'「Round2-all」new'
        manager.sheet_start_row = 4
        manager.sheet_last_row = 800
        manager.sheet_start_col = 'A'
        manager.sheet_last_col = 'R'
        manager.language_cols = {LANG_EN:'L', 
                                 LANG_TW:'K',
                                 LANG_HK:'M',
                                 LANG_CN:'N',
                                 LANG_JP:'O',
                                 LANG_KR:'P',
                                 LANG_THAI:'Q'}
        # convert cols from letter to index
        for key, val in manager.language_cols.iteritems():
            manager.language_cols[key] = col_letter_to_index(val)
        return manager
    
    def load_spreadsheet_entries(self, lang_for_key=LANG_TW):
        service = sheet_api.deal_with_auth_and_prepare_api_service()
        range_name = u'{0}!{1}{2}:{3}{4}'.format(self.sheet_name,
                                                 self.sheet_start_col, self.sheet_start_row,
                                                 self.sheet_last_col, self.sheet_last_row)
        values = sheet_api.read_spreadsheet_values(service, self.spreadsheet_id, range_name)
        entries = []
        key_col = self.language_cols[lang_for_key]
        if not values:
            print('No data found from reading google localization spreadsheet'
                  '\nSpreadsheet id: {0} sheet name: {1}'.format(self.spreadsheet_id, self.sheet_name))
            return entries
        for row in values:
            entry = SpreadSheetEntry()
            entry.key = row[key_col]
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
        self.entry_pattern = re.compile(r'^(?!\/\/).*"(.*?[^\\])"[ ]*=[ ]*"(.*?[^\\])"\s*(;?)(.*)')

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
        for lang, lang_dir in self.languages.iteritems():
            for line in self.read_localization_strings_file(lang, lang_dir):
                matched = self.entry_pattern.match(line)
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
    
    def read_localization_strings_file(self, lang, lang_dir):
        dir_path = os.path.join(self.app_dir, lang_dir)
        strings_file_path = os.path.join(dir_path, 'Localizable.strings')
        with io.open(strings_file_path, encoding='utf8') as reader:
            for line in reader:
                yield line

class EntryMapping(object):
    def __init__(self):
        self.key = ''
        self.spreadsheet_entries = list()
        self.strings_entries = list()

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

def verify_localization_strings_syntax():
    print("---- check localization strings syntax integrity ----")
    manager = LocalizationStringsManager.default_manager()
    for lang, lang_dir in manager.languages.iteritems():
        print(" checking {0} localizable strings".format(lang))
        line_number = 1
        file_good = True
        for line in manager.read_localization_strings_file(lang, lang_dir):
            matched = manager.entry_pattern.match(line)
            if matched and matched.group(3) != ";":
                print (u'  {0}. {1}'.format(line_number, line))
                file_good = False
            line_number += 1
        if file_good:
            print(' - all good')

def compare_localizable_strings_with_spreadsheet():
    print("---- compare localization data from spreadsheet and app ----")
    key_lang = LANG_TW
    # load spreadsheet entry
    spreadsheet_manager = SpreadSheetManager.default_manager()
    spreadsheet_entries = spreadsheet_manager.load_spreadsheet_entries(key_lang)
    # load localizable.strings entry
    strings_manager = LocalizationStringsManager.default_manager()
    strings_entries = strings_manager.load_strings_entries()
    # map and link up the entry
    mappings = dict()
    # use value of english from both set of entries to build mapping
    #  pass one (spreadsheet)
    for entry in spreadsheet_entries:
        key = entry.values[key_lang]
        mapping = mappings.get(key)
        if not mapping:
            mapping = EntryMapping()
            mapping.key = key
            mappings[key] = mapping
        mapping.spreadsheet_entries.append(entry)
    #  pass two (strings)
    for entry in strings_entries:
        key = entry.values[key_lang]
        mapping = mappings.get(key)
        if not mapping:
            mapping = EntryMapping()
            mapping.key = key
            mappings[key] = mapping
        mapping.strings_entries.append(entry)
    # analyze the difference
    both = []
    spreadsheet_only = []
    strings_only = []
    for key, mapping in mappings.iteritems():
        if len(mapping.spreadsheet_entries) > 0 and len(mapping.strings_entries) > 0:
            both.append(mapping)
        elif len(mapping.spreadsheet_entries) > 0:
            spreadsheet_only.append(mapping)
        else:
            strings_only.append(mapping)
    # print the result
    print(' result:')
    print(' -- value changed:')
    index = 1
    diff_result = dict()
    for mapping in both:
        spreadsheet_entry = mapping.spreadsheet_entries[0]
        strings_entry = mapping.strings_entries[0]
        difference = dict()
        for lang, spreadsheet_value in spreadsheet_entry.values.iteritems():
            strings_value = strings_entry.values.get(lang)
            if spreadsheet_value != strings_value:
                difference[lang] = {"sheet": spreadsheet_value, "app": strings_value}
        if difference:
            print(u' {0}. ios key: {1}'.format(index, strings_entry.key))
            for lang, diff in difference.iteritems():
                print(u'  - [{0}]: {1} --> {2}'.format(lang, diff["app"], diff["sheet"]))
            diff_result[strings_entry.key] = difference
            index += 1
    file_name = 'diff_in_app_sheet.json'
    print('  write result to json: {0}'.format(file_name))
    with io.open(file_name, mode='w', encoding='utf8') as writer:
        to_write = json.dumps(diff_result, ensure_ascii=False)
        if isinstance(to_write, str):
            to_write = unicode(to_write, 'UTF-8')
        writer.write(to_write)
    print('  .....done!')

    # print('  - both: {0}'.format(len(both)))
    # print('  - spreadsheet only: {0}'.format(len(spreadsheet_only)))
    # print_mappings(spreadsheet_only, 10, True)
    # print('  - strings only: {0}'.format(len(strings_only)))
    # print_mappings(strings_only, 10, True)

def update_app_localizable_strings_base_on_diff_json():
    print("---- update localization.strings base on diff json ----")
    manager = LocalizationStringsManager.default_manager()
    # read the diff file
    diff_result = None
    with open('diff_in_app_sheet.json') as json_data:
        diff_result = json.load(json_data)
    if not diff_result:
        print('no diff_in_app_sheet.json found')
        return
    # going though each Localizable.strings files
    for lang, lang_dir in manager.languages.iteritems():
        print(" checking {0} localizable strings".format(lang))
        line_number = 1
        file_good = True
        # create a tmp file
        dir_path = os.path.join(manager.app_dir, lang_dir)
        strings_file_path = os.path.join(dir_path, 'Localizable.strings')
        file_to_write = os.path.join(dir_path, 'Localizable.strings.tmp')
        # remove tmp file
        if os.path.exists(file_to_write):
            os.remove(file_to_write)
        # write to tmp file
        with io.open(file_to_write, mode='w', encoding='utf8') as writer:
            print(u"writing to file: {0}".format(file_to_write))
            for line in manager.read_localization_strings_file(lang, lang_dir):
                line_to_write = line
                matched = manager.entry_pattern.match(line)
                if matched:
                    key = matched.group(1)
                    val = matched.group(2)
                    # bypass any entry with modifier, since updating entry with modifier is dangerous
                    if not "%" in val:
                        diff = diff_result.get(key)
                        if diff:
                            diff_value = diff.get(lang)
                            if diff_value:
                                # sanitize new value
                                new_value = diff_value["sheet"]
                                # special condition
                                if new_value == 'Luggage width is over 21"':
                                    new_value = 'Luggage width is over 21\"'
                                # "最多可自訂3個行程，至少輸入1個自訂行程" ==> "最多可自訂%d個行程，至少輸入1個自訂行程"
                                # in order to avoid overwrite key (when value and key happens to be the same)
                                # 어디로 갈까요? => 어디로 갈까요
                                # "抵達日期及時間" => "出發日期及時間" HK
                                # "女性" = "female" => "หญิง"
                                # % => ％
                                #
                                #
                                #
                                key_part, val_part = line_to_write.split("=")
                                line_to_write = key_part+"="+val_part.replace(diff_value["app"], new_value)
                                print(u"    {0} ==> {1}".format(line, line_to_write))
                writer.write(line_to_write)
        # replace original file with tmp file
        os.remove(strings_file_path)
        os.rename(file_to_write, strings_file_path)
    # remove diff file
    os.remove('diff_in_app_sheet.json')

# ---------- main ----------

def main():
    # test_load_spreadsheet_entries()
    # test_load_strings_entries()
    # find_english_only_localization()
    # find_not_translated_entries()
    # verify_localization_strings_syntax()
    compare_localizable_strings_with_spreadsheet()
    # update_app_localizable_strings_base_on_diff_json()

if __name__ == '__main__':
    main()