"""
מערכת Scraping - פנקס תובענות ייצוגיות
מתוך: https://www.court.gov.il/NGCS.Web.Site/HomePage.aspx
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os
from typing import List, Dict, Any
import logging

# הגדרת logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CaseScraper:
    """מחלקה לscraping של תובענות ייצוגיות"""
    
    def __init__(self, output_dir: str = "data"):
        """
        אתחול ה-scraper
        
        Args:
            output_dir: תיקייה לשמירת הנתונים
        """
        self.base_url = "https://www.court.gov.il/NGCS.Web.Site/HomePage.aspx"
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # יצירת תיקייה לפלט
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"תיקייה {output_dir} נוצרה בהצלחה")
    
    def fetch_page(self) -> str:
        """
        הורדת דף HTML
        
        Returns:
            str: תוכן ה-HTML
        """
        try:
            logger.info(f"הורדת דף מ-{self.base_url}")
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            logger.info(f"דף הורד בהצלחה. גודל: {len(response.text)} תווים")
            return response.text
        except requests.RequestException as e:
            logger.error(f"שגיאה בהורדת הדף: {e}")
            raise
    
    def extract_json_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        חילוץ נתוני JSON מה-HTML
        
        Args:
            html_content: תוכן HTML
            
        Returns:
            List[Dict]: רשימת התיקים
        """
        try:
            logger.info("חילוץ נתוני JSON מ-HTML...")
            
            # חיפוש ה-input עם ה-JSON
            pattern = r'id="RepresentativeRegistryGridArrayStore"\s+value=\'(.*?)\'\s+/>'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                logger.warning("לא נמצא input עם RepresentativeRegistryGridArrayStore")
                return []
            
            json_str = match.group(1)
            
            # ניסיון לחילוץ JSON
            try:
                cases_data = json.loads(json_str)
                logger.info(f"חולצו {len(cases_data)} תיקים")
                return cases_data
            except json.JSONDecodeError as e:
                logger.error(f"שגיאה בפענוח JSON: {e}")
                return []
                
        except Exception as e:
            logger.error(f"שגיאה בחילוץ נתונים: {e}")
            return []
    
    def process_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        עיבוד נתוני התיקים
        
        Args:
            cases: רשימת התיקים
            
        Returns:
            List[Dict]: רשימה מעובדת
        """
        processed_cases = []
        
        for case in cases:
            try:
                processed_case = {
                    'מספר_תיק': case.get('CaseDisplayIdentifier', ''),
                    'שם_תיק': case.get('CaseName', ''),
                    'תאריך_פתיחה': case.get('CaseOpenDate', ''),
                    'בית_משפט': case.get('CourtName', ''),
                    'קבוצה_תובעים': case.get('RepresentativeComplaintGroupName', ''),
                    'שאלה_משפטית': case.get('LegalQuestion', ''),
                    'סעד_מבוקש': case.get('RequestedAID', ''),
                    'סכום_תביעה': case.get('ClaimAmount', 0),
                    'מספר_תיק_id': case.get('CaseID', ''),
                    'תיק_ערעור': case.get('isAppealCase', '0'),
                    'מספר_מסמכים': len(case.get('Docs', []))
                }
                processed_cases.append(processed_case)
            except Exception as e:
                logger.error(f"שגיאה בעיבוד תיק: {e}")
                continue
        
        return processed_cases
    
    def save_to_csv(self, cases: List[Dict[str, Any]], filename: str = "cases.csv"):
        """
        שמירת נתונים ל-CSV
        
        Args:
            cases: רשימת התיקים
            filename: שם הקובץ
        """
        if not cases:
            logger.warning("אין תיקים לשמור")
            return
        
        try:
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=cases[0].keys())
                writer.writeheader()
                writer.writerows(cases)
            
            logger.info(f"נתונים שמורים ל-{filepath}")
        except Exception as e:
            logger.error(f"שגיאה בשמירה ל-CSV: {e}")
    
    def save_to_json(self, cases: List[Dict[str, Any]], filename: str = "cases.json"):
        """
        שמירת נתונים ל-JSON
        
        Args:
            cases: רשימת התיקים
            filename: שם הקובץ
        """
        if not cases:
            logger.warning("אין תיקים לשמור")
            return
        
        try:
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cases, f, ensure_ascii=False, indent=2)
            
            logger.info(f"נתונים שמורים ל-{filepath}")
        except Exception as e:
            logger.error(f"שגיאה בשמירה ל-JSON: {e}")
    
    def generate_report(self, cases: List[Dict[str, Any]]):
        """
        יצירת דוח סטטיסטי
        
        Args:
            cases: רשימת התיקים
        """
        if not cases:
            logger.warning("אין תיקים לדיווח")
            return
        
        report = {
            'סה"כ_תיקים': len(cases),
            'סכום_תביעה_כולל': sum(c.get('סכום_תביעה', 0) for c in cases),
            'בתי_משפט': list(set(c.get('בית_משפט', '') for c in cases)),
            'מס_בתי_משפט': len(set(c.get('בית_משפט', '') for c in cases)),
            'תיקי_ערעור': sum(1 for c in cases if c.get('תיק_ערעור') == '1'),
            'תאריך_סקרפינג': datetime.now().isoformat()
        }
        
        logger.info("\n" + "="*50)
        logger.info("דוח סטטיסטי")
        logger.info("="*50)
        for key, value in report.items():
            logger.info(f"{key}: {value}")
        logger.info("="*50 + "\n")
        
        # שמירת הדוח
        try:
            filepath = os.path.join(self.output_dir, "report.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"דוח שמור ל-{filepath}")
        except Exception as e:
            logger.error(f"שגיאה בשמירת הדוח: {e}")
    
    def run(self):
        """הרצת ה-scraper"""
        try:
            logger.info("התחלת scraping...")
            
            # הורדה
            html_content = self.fetch_page()
            
            # חילוץ
            cases = self.extract_json_data(html_content)
            
            if not cases:
                logger.warning("לא נמצאו תיקים")
                return
            
            # עיבוד
            processed_cases = self.process_cases(cases)
            
            # שמירה
            self.save_to_csv(processed_cases)
            self.save_to_json(processed_cases)
            
            # דוח
            self.generate_report(processed_cases)
            
            logger.info("סיום scraping בהצלחה!")
            
        except Exception as e:
            logger.error(f"שגיאה כללית: {e}")
            raise


if __name__ == "__main__":
    scraper = CaseScraper(output_dir="./data")
    scraper.run()
