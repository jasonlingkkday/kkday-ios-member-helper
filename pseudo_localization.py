# steps:
# 1. specify the root folder
# 2. find the specifics folder that contain base localize strings
#     - localized strings files for storyboard and xib
#     - localized strings files
# 3. create mechanism for the following action
#     - perform pseudo localization test code changes
#     - revert the changes to original
# 4. perform pseudo localization test code changes
#     - make backup for each file changed
#     - parse each strings file
#         - parse each line, replace the value part with modified suffix and prefix modifier
# 5. revert changes to original
#     - look for original files with
#         - if exists
#             - remove current localized strings files
#             - renamed backup strings files to original names

import os
import codecs
import re
import io

ROOT_DIR = '/users/ryoukoken/desktop/projects/kkday-ios-member/Solution/kkday-ios-member/kkday-ios-member'
BASE_DIR = 'Base.lproj'
EN_DIR = 'en.lproj'
JP_DIR = 'ja.lproj'
KR_DIR = 'ko.lproj'
THAI_DIR = 'th.lproj'
TW_DIR = 'zh-Hant-TW.lproj'
HK_DIR = 'zh-Hant-HK.lproj'
CN_DIR = 'zh-Hans.lproj'
TARGET_FILE_EXT = '.strings'

MODIFIER_PREFIX = '!!@@---'
MODIFIER_POSTFIX = '---@@!!'

class StringFile(object):
    def __init__(self, dir, filename):
        self.dir = dir
        self.filename = filename
        self.full_path = os.path.join(dir, filename)
        self.tmp_path = os.path.join(dir, filename+'_tmp')
        self.backup_path = os.path.join(dir, filename+'_backup')
    
    def __str__(self):
        return self.full_path

def scan_for_files(dir_list):
    found = []
    for dir in dir_list:
        path = os.path.join(ROOT_DIR, dir)
        for file in os.listdir(path):
            if file.endswith(TARGET_FILE_EXT):
                str_file = StringFile(path, file)
                found.append(str_file)
    return found

def add_wrapper(matchobj):
    # print matchobj
    return ''.join([matchobj.group(1),
                    MODIFIER_PREFIX,
                    matchobj.group(2),
                    MODIFIER_POSTFIX,
                    matchobj.group(3)])

def file_parser(str_file):
    pattern = r'(.*=[ ]*")(.*?[^\\])(".*)'
    with io.open(str_file.full_path, encoding='utf8') as reader:
        with io.open(str_file.tmp_path, mode='w', encoding='utf8') as writer:
            for line in reader:
                before = line
                after = re.sub(pattern, add_wrapper, line)         
                print before + "\n===>" + after
                writer.write(after)
    print 'file read:{0}\n'.format(str_file.full_path)
    print 'file wrote: {0}\n'.format(str_file.tmp_path)


def commit_change(str_file):
    print 'will change file {0} to backup'.format(str_file.full_path)
    os.rename(str_file.full_path, str_file.backup_path)
    # change file
    print 'will change file {0} to current'.format(str_file.tmp_path)
    os.rename(str_file.tmp_path, str_file.full_path)
    # change file

def revert_change(str_file):
    if os.path.exists(str_file.backup_path):
        if os.path.exists(str_file.full_path):
            os.remove(str_file.full_path)
        os.rename(str_file.backup_path, str_file.full_path)

def test2():
    files = scan_for_files([BASE_DIR, EN_DIR])
    for file in files:
        revert_change(file)
        file_parser(file)
        commit_change(file)


if __name__ == "__main__":
    test2()
