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
            sheet_lookup = {entry.values[mapping.mapping_languange] : entry for entry in sheet_entries}
            app_lookup = {entry.values[mapping.mapping_languange] : entry for entry in app_entries}
        diff_entries = []
        for key, app_entry in app_lookup.iteritems():
            sheet_entry = sheet_lookup.get(key)
            if sheet_entry:
                diff = self.compare_entries(sheet_entry=sheet_lookup[key], app_entry=app_entry, languages=languages)
                if diff:
                    diff_entries.append({
                        'key': app_entry.key,
                        'diff': diff
                    })
        app_only_entries = [entry for key, entry in app_lookup.iteritems() if key not in sheet_lookup]
        sheet_only_entries = [entry for key, entry in sheet_lookup.iteritems() if key not in app_lookup]
        return diff_entries, app_only_entries, sheet_only_entries

    def save_analyze_diff_to_disk(self, diff_type, result, filename):
        data = {}
        if diff_type == 'diff':
            data['diff'] = result
        if diff_type == 'app only':
            data['app only'] = [entry.to_json() for entry in result]
        if diff_type == 'sheet only':
            data['sheet only'] = [entry.to_json() for entry in result]
        write_as_json_file(data=data, filename=filename)
    
    def load_analyze_diff_from_disk(self, diff_type, filename):
        data = load_json_file(filename=filename)
        return data.get(diff_type)
    
    def apply_whitelist_to_analyze_diff(self, whitelist_filename, diff_entries, languages):
        whitelist = load_json_file(filename=whitelist_filename)
        # apply specific rules
        diff_dict = {entry["key"]: entry["diff"] for entry in diff_entries}
        for key, options in whitelist["specifics"].iteritems():
            if options.get("skip"):
                del diff_dict[key]
            else:
                for lang in languages:
                    if options.get(lang) and options.get(lang).get("skip"):
                        del diff_dict[key][lang]
        # apply general rules
        trim_white_space = whitelist["general"].get("trim_white_space", False)
        for key, diff in diff_dict.iteritems():
            for lang in languages:
                entry = diff.get(lang)
                if entry:
                    if trim_white_space:
                        entry["sheet"] = entry["sheet"].strip()
        # clean up
        whitelisted_diff_entries = []
        for key, diff in diff_dict.iteritems():
            for lang in languages:
                entry = diff.get(lang)
                if entry:
                    if entry["sheet"] == entry["app"]:
                        del diff[lang]
            if diff_dict[key]:
                whitelisted_diff_entries.append({'key':key, 'diff':diff })
        return whitelisted_diff_entries
    
    def create_action_plan(self, diff_entries, languages, filename):
        plan = dict()
        for entry in diff_entries:
            key = entry["key"]
            plan_detail = dict()
            for lang in languages:
                item = entry['diff'].get(lang)
                if item:
                    plan_detail[lang] = {
                        "from": item["app"],
                        "to": item["sheet"]
                    }
            plan[key] = plan_detail
        write_as_json_file(data=plan, filename=filename)
        return plan
    
    def load_action_plan(self, filename):
        return load_json_file(filename=filename)
    
    def execute_action_plan(self, action_plan):
        """
        1. iterate target files (localizable strings or storyboard strings)
            - for each file
                - create a tmp file
                - write each line in file to tmp file
                    - whe line contain key from action plan
                        - update the line with value from action plan
            - rename the file with backup
            - change tmp file to file name
        """
        

        



            





