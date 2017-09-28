# -*- coding: utf-8 -*-

import unittest

from .context import localization_helper

class SpreadSheetManagerTestSuite(unittest.TestCase):
    
    def setUp(self):
        self.manager = localization_helper.SpreadSheetManager()
    
    def tearDown(self):
        self.manager = None

    def test_create_range_1(self):
        range_name = self.manager.create_range(sheet_name="blah", start_row=1, end_row=200, start_col="A", end_col="Z")
        self.assertTrue(range_name == u"blah!A1:Z200")
    
    def test_create_range_2(self):
        range_name = self.manager.create_range(sheet_name="noooo", start_row=1, end_row=200, start_col="A", end_col="Z")
        self.assertTrue(range_name != u"blah!A1:Z200")
    
    def test_col_letter_to_index_1(self):
        idx = self.manager.col_letter_to_index('a')
        self.assertTrue(idx == 0)
    
    def test_col_letter_to_index_2(self):
        idx = self.manager.col_letter_to_index('Z')
        self.assertTrue(idx == 25)
    
    def test_download_spreadsheet(self):
        scopes = 'https://www.googleapis.com/auth/spreadsheets.readonly'
        secret_file = './workspace/client_secret.json'
        spreadsheet_id = '12HzYXwi6c-DyCsHS3UhwmMvHjG_VGSRmeMCpcFA_vwQ'
        range_name = u'傑森!B5:E7'
        rows = self.manager.download_spreadsheet(scopes=scopes, 
                                                 secret_file=secret_file, 
                                                 spreadsheet_id=spreadsheet_id, 
                                                 range_name=range_name)
        self.assertTrue(rows[0][0] == 'test')
        self.assertTrue(rows[0][1] == 'your')
        self.assertTrue(rows[1][2] == 'swift')
        self.assertTrue(rows[2][3] == 'skills')
    
    def test_parse_spreadsheet(self):
        rows = [[u'更多體驗',u'Suggestions for you',u'為你推薦',u'为你推荐',u'オススメの商品',u'추천 상품',u'เราแนะนำสำหรับคุณ'],
                [u'精選城市',u'Top destinations',u'精選城市',u'精选城市',u'人気スポット',u'인기 여행지',u'แหล่งท่องเที่ยวแนะนำ'],
                [u'更多',u'More',u'更多',u'更多',u'もっと探そう',u'더 읽기',u'เพิ่มเติม'],
                [u'熱門體驗',u'Popular experiences',u'熱門體驗',u'热门体验',u'人気商品',u'인기 액티비티',u'ประสบการณ์ยอดนิยม']]
        lang_mapping = {
            "EN": "b",
            "TW": "a",
            "HK": "c",
            "CN": "d",
            "JP": "e",
            "KR": "f",
            "THAI": "g"
        }
        key_lang = "TW"
        entries = self.manager.parse_spreadsheet(spreadsheet_rows=rows, 
                                                 key_lang=key_lang, 
                                                 lang_col_mapping=lang_mapping)
        self.assertTrue(entries[0].key == u'更多體驗')
        self.assertTrue(entries[3].values["THAI"] == u'ประสบการณ์ยอดนิยม')
    
    def test_read_write_json(self):
        entry1 = localization_helper.SpreadSheetEntry()
        entry1.key = u'熱門體驗'
        entry1.values = {
            "EN": u"Popular experiences",
            "TW": u"熱門體驗",
            "HK": u"熱門體驗",
            "CN": u"热门体验",
            "JP": u"もっと探そう",
            "KR": u"인기 액티비티",
            "THAI": u"ประสบการณ์ยอดนิยม"
        }
        entry2 = localization_helper.SpreadSheetEntry()
        entry2.key = u'更多'
        entry2.values = {
            "EN": u"More",
            "TW": u"更多",
            "HK": u"更多",
            "CN": u"更多",
            "JP": u"もっと探そう",
            "KR": u"더 읽기",
            "THAI": u"เพิ่มเติม"
        }
        entry3 =  localization_helper.SpreadSheetEntry()
        entry3.key = u'精選城市'
        entry3.values = {
            "EN": u"Top destinations",
            "TW": u"精選城市",
            "HK": u"精選城市",
            "CN": u"精选城市",
            "JP": u"人気スポット",
            "KR": u"인기 여행지",
            "THAI": u"แหล่งท่องเที่ยวแนะนำ"
        }
        entries = [entry1, entry2]
        filename = "./workspace/tmp_entries.json"
        self.manager.save_entries_to_disk(entries=entries, filename=filename)
        read_entries = self.manager.load_entries_from_disk(filename)
        self.assertTrue(entries == read_entries)
        self.assertFalse(read_entries == [entry1, entry3])

if __name__ == '__main__':
    unittest.main()
