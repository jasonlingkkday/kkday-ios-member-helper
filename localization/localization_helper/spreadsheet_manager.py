# -*- coding: utf-8 -*-

import string
import localization_helper.google_spreadsheet as api
from .helper import write_as_json_file, load_json_file

class SpreadSheetEntry(object):
    def __init__(self):
        self.key = None
        self.values = dict()

class SpreadSheetManager(object):
    def __init__(self):
        pass

    def create_range(self, sheet_name, start_row, end_row, start_col, end_col):
        range_name = u'{0}!{1}{2}:{3}{4}'.format(sheet_name,
                                                 start_col, start_row,
                                                 end_col, end_row)
        return range_name
    
    def col_letter_to_index(self, letter):
        return string.ascii_uppercase.index(letter.upper())

    def convert_lang_col_mapping(self, lang_col_mapping):
        mapping = dict()
        for lang, col_letter in lang_col_mapping.iteritems():
            mapping[lang] = self.col_letter_to_index(col_letter)
        return mapping
    
    def download_spreadsheet(self, scopes, secret_file, spreadsheet_id, range):
        service = api.deal_with_auth_and_prepare_api_service(client_secret_file=secret_file, scopes=scopes)
        rows = api.read_spreadsheet_values(service=service, spreadsheet_id=spreadsheet_id, range=range)
        return rows

    def parse_spreadsheet(self, spreadsheet_rows, key_lang, lang_col_mapping):
        # convert col from letter to
        mapping = self.convert_lang_col_mapping(lang_col_mapping)
        key_col = mapping[key_lang]
        entries = []
        for row in spreadsheet_rows:
            entry = SpreadSheetEntry()
            entry.key = row[key_col]
            for lang, col in mapping.iteritems():
                value = row[col].strip('\n') if len(row) > col else ""
                entry.values[lang] = value
            entries.append(entry)
            # break
        return entries
    
    def save_entries_to_disk(self, entries, filename):
        write_as_json_file(data=entries, filename=filename)

    def load_entries_from_disk(self, filename):
        entries = load_json_file(filename=filename)
        return entries


        