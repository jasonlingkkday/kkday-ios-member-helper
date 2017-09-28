# -*- coding: utf-8 -*-

# from localization_helper.spreadsheet_manager import SpreadSheetEntry, SpreadSheetManager
# from localization_helper.app_manager import AppManager, StringsEntry
from localization_helper.helper import write_as_json_file, load_json_file

class LocalizationMapping(object):
    def __init__(self, use_key_for_mapping, mapping_language):
        self.use_key_as_mapping = use_key_for_mapping
        self.mapping_languange = mapping_language

class LocalizationManager(object):
    def __init__(self):
        pass
        # self.sheet_manager = SpreadSheetManager()
        # self.app_manager = AppManager()
    
    def compare_entries(self, sheet_entry, app_entry, languages):
        diff = {}
        for lang in languages:
            sheet_val = sheet_entry.values.get(lang)
            app_val = app_entry.values.get(lang)
            if app_val != sheet_val:
                diff[lang] = {
                    'app': app_val,
                    'sheet': sheet_val
                }
        return diff
    
    def analyze_diff_between_app_and_spreadsheet(self, sheet_entries, app_entries, mapping, languages):
        if mapping.use_key_as_mapping:
            sheet_lookup = {entry.key : entry.value for entry in sheet_entries}
            app_lookup = {entry.key : entry.value for entry in app_entries}
        else:
            sheet_lookup = {entry.values[mapping.mapping_languange] : entry.value for entry in sheet_entries}
            app_lookup = {entry.values[mapping.mapping_languange] : entry.value for entry in app_entries}
        diff_entries = []
        for key, app_entry in app_lookup.iteritems():
            diff = self.compare_entries(sheet_entry=sheet_lookup[key], app_entry=app_entry, languages=languages)
            if diff:
                diff_entries.append({
                    'key': app_entry.key,
                    'diff': diff
                })
        app_only_entries = [entry for key, entry in app_lookup.iteritems() if key not in sheet_lookup]
        sheet_only_entries = [entry for key, entry in sheet_lookup.iteritems() if key not in app_lookup]
        return diff_entries, app_only_entries, sheet_only_entries

    def save_analyze_diff_to_disk(self, diff_entries, app_only_entries, sheet_only_entries, filename):
        data = {
            'diff': diff_entries,
            'app only': app_only_entries,
            'sheet only': sheet_only_entries
        }
        write_as_json_file(data=data, filename=filename)
    
    def load_analyze_diff_from_disk(self, filename):
        data = load_json_file(filename=filename)
        return data
