"""
בדיקות עבור מערכת ה-Scraping
"""

import unittest
import json
import os
from main_scraper import CaseScraper


class TestCaseScraper(unittest.TestCase):
    """בדיקות כיתת ה-Scraper"""
    
    def setUp(self):
        """הכנה לכל בדיקה"""
        self.scraper = CaseScraper(output_dir="./test_data")
    
    def tearDown(self):
        """ניקוי לאחר כל בדיקה"""
        import shutil
        if os.path.exists("./test_data"):
            shutil.rmtree("./test_data")
    
    def test_scraper_initialization(self):
        """בדיקה: האתחול עובד"""
        self.assertIsNotNone(self.scraper)
        self.assertEqual(self.scraper.output_dir, "./test_data")
        self.assertTrue(os.path.exists("./test_data"))
    
    def test_json_extraction_with_sample_html(self):
        """בדיקה: חילוץ JSON מ-HTML לדוגמה"""
        sample_html = '''
        <input type="hidden" id="RepresentativeRegistryGridArrayStore" 
        value='[{"CaseDisplayIdentifier":"123","CaseName":"test case","CaseID":1}]' />
        '''
        
        cases = self.scraper.extract_json_data(sample_html)
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0]['CaseDisplayIdentifier'], '123')
    
    def test_case_processing(self):
        """בדיקה: עיבוד תיק עובד"""
        sample_cases = [
            {
                'CaseDisplayIdentifier': '123',
                'CaseName': 'תיק לדוגמה',
                'CaseOpenDate': '01/01/2025',
                'CourtName': 'אזורי',
                'ClaimAmount': 1000000,
                'CaseID': 1,
                'Docs': []
            }
        ]
        
        processed = self.scraper.process_cases(sample_cases)
        self.assertEqual(len(processed), 1)
        self.assertEqual(processed[0]['שם_תיק'], 'תיק לדוגמה')
        self.assertEqual(processed[0]['סכום_תביעה'], 1000000)
    
    def test_csv_export(self):
        """בדיקה: ייצוא CSV עובד"""
        sample_cases = [
            {
                'מספר_תיק': '123',
                'שם_תיק': 'לדוגמה',
                'סכום_תביעה': 1000
            }
        ]
        
        self.scraper.save_to_csv(sample_cases, "test.csv")
        self.assertTrue(os.path.exists("./test_data/test.csv"))
    
    def test_json_export(self):
        """בדיקה: ייצוא JSON עובד"""
        sample_cases = [
            {
                'מספר_תיק': '123',
                'שם_תיק': 'לדוגמה'
            }
        ]
        
        self.scraper.save_to_json(sample_cases, "test.json")
        
        # בדיקה שהקובץ קיים ותוכנו נכון
        self.assertTrue(os.path.exists("./test_data/test.json"))
        with open("./test_data/test.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['מספר_תיק'], '123')
    
    def test_empty_cases_handling(self):
        """בדיקה: טיפול בנתונים ריקים"""
        empty_cases = []
        processed = self.scraper.process_cases(empty_cases)
        self.assertEqual(len(processed), 0)


if __name__ == '__main__':
    unittest.main()
