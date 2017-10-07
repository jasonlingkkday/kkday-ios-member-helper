# -*- coding: utf-8 -*-

import re
import os

from localization_helper.helper import read_file, write_as_json_file, load_json_file

class StringsEntry(object):
    def __init__(self):
        self.key = None
        self.values = dict()
    
    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__
    
    def to_json(self):
        return {
            "key": self.key,
            "values": self.values
        }
    
    def from_json(self, json_dict):
        self.key = json_dict["key"]
        self.values = json_dict["values"]
    
    @classmethod
    def init_json(cls, json_dict):
        entry = cls()
        entry.from_json(json_dict)
        return entry

class AppManager(object):
    def __init__(self):
        pass
    
    def read_localization_strings_file(self, filename):
        entry_pattern = re.compile(r'^(?!\/\/).*"(.*?[^\\])"[ ]*=[ ]*"(.*?[^\\])"\s*(;?)(.*)')
        lines = read_file(filename)
        results = []
        for line in lines:
            matched = entry_pattern.match(line)
            key = None
            val = None
            if matched:
                key = matched.group(1)
                val = matched.group(2)
            results.append((key, val, line))
        return results

    def load_localizable_strings(self, languages, language_dirs, project_dir):
        entries = dict()
        for lang in languages:
            dir_path = os.path.join(project_dir, language_dirs[lang])
            filename = os.path.join(dir_path, 'Localizable.strings')
            results = self.read_localization_strings_file(filename)
            for (key, val, _) in results:
                if key:
                    entry  = entries.get(key)
                    if not entry:
                        entry = StringsEntry()
                        entry.key = key
                        entries[key] = entry
                    entry.values[lang] = val
        return entries.values()

    def load_storyboard_strings(self, languages, language_dirs, project_dir):
        entries = dict()
        for lang in languages:
            dir_path = os.path.join(project_dir, language_dirs[lang])
            filenames = [os.path.join(dir_path, filename) for filename in os.listdir(dir_path) 
                                                          if filename.endswith(".strings") and filename != 'Localizable.strings']
            for filename in filenames:
                results = self.read_localization_strings_file(filename=filename)
                for (key, val, _) in results:
                    if key:
                        entry  = entries.get(key)
                        if not entry:
                            entry = StringsEntry()
                            entry.key = key
                            entries[key] = entry
                        entry.values[lang] = val
        return entries.values()
    
    def save_entries_to_disk(self, entries, filename):
        data = [entry.to_json() for entry in entries]
        write_as_json_file(data=data, filename=filename)

    def load_entries_from_disk(self, filename):
        data = load_json_file(filename=filename)
        entries = [StringsEntry.init_json(row) for row in data]
        return entries

    def gather_localizable_strings_file_path(self, languages, language_dirs, project_dir):
        filenames = []
        for lang in languages:
            dir_path = os.path.join(project_dir, language_dirs[lang])
            filename = os.path.join(dir_path, 'Localizable.strings')
            filenames.append(filename)
        return filenames

    def gather_storyboard_strings_file_path(self, languages, language_dirs, project_dir):
        filenames = []
        for lang in languages:
            dir_path = os.path.join(project_dir, language_dirs[lang])
            filenames = [os.path.join(dir_path, filename) for filename in os.listdir(dir_path) 
                                                          if filename.endswith(".strings") and filename != 'Localizable.strings']
        return filenames
    
    def create_strings_file_entry_with_new_val(self, key, value, new_value, line):
        return new_value.join(line.rsplit(value, 1))

    def update_localization_strings_file(self, filename, update_callback):
        results = self.read_localization_strings_file(filename)
        edited_lines = []
        for (key, val, line) in results:
            to_write = line
            if key:
                new_val = update_callback(key, val, line)
                if new_val:
                    to_write = new_val
            edited_lines.append(to_write)
        return edited_lines

    def update_localizable_strings(self, languages, language_dirs, project_dir, update_val_callback, end_of_file_callback):
        for lang in languages:
            dir_path = os.path.join(project_dir, language_dirs[lang])
            filename = 'Localizable.strings'
            full_path = os.path.join(dir_path, filename)
            def callback(key, val, line):
                new_val = update_val_callback(lang, key, val, line)
                if new_val:
                    return self.create_strings_file_entry_with_new_val(key=key, value=val, new_value=new_val, line=line)
                return None
            edited_lines = self.update_localization_strings_file(filename=full_path, update_callback=callback)
            end_of_file_callback(lang, edited_lines, dir_path, filename, full_path)
