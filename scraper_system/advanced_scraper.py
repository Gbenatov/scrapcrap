"""
Advanced Scraper עם Selenium - עבור אתרים דינמיים
(Selenium is optional - only for local use)
"""

import json
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

# Try importing Selenium, but don't fail if it's not available
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False
    logger.warning("Selenium not installed. AdvancedCaseScraper will not work.")


class AdvancedCaseScraper:
    """Scraper מתקדם עם Selenium לאתרים דינמיים (optional)"""
    
    def __init__(self):
        """אתחול"""
        if not HAS_SELENIUM:
            raise RuntimeError("Selenium is not installed. Install it with: pip install selenium")
        
        self.base_url = "https://www.court.gov.il/NGCS.Web.Site/HomePage.aspx"
        self.driver = None
    
    def setup_driver(self):
        """הגדרת ה-webdriver"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            # options.add_argument('--headless')  # אם רוצים headless mode
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("WebDriver initialized")
        except Exception as e:
            logger.error(f"שגיאה בהגדרת WebDriver: {e}")
            raise
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """המתנה לאלמנט"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            logger.error(f"שגיאה בהמתנה לאלמנט: {e}")
            return None
    
    def fetch_and_parse(self) -> List[Dict[str, Any]]:
        """הורדה וניתוח דינמי"""
        try:
            logger.info("ניווט לאתר...")
            self.driver.get(self.base_url)
            
            # המתנה לטבלה
            self.wait_for_element(
                By.ID, 
                "RepresentativeRegistryGridArrayStore"
            )
            
            # חילוץ ה-JSON
            input_element = self.driver.find_element(
                By.ID, 
                "RepresentativeRegistryGridArrayStore"
            )
            json_str = input_element.get_attribute("value")
            
            cases = json.loads(json_str)
            logger.info(f"חולצו {len(cases)} תיקים")
            return cases
            
        except Exception as e:
            logger.error(f"שגיאה בחילוץ: {e}")
            return []
        finally:
            self.close_driver()
    
    def close_driver(self):
        """סגירת ה-driver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")


# דוגמה לשימוש
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scraper = AdvancedCaseScraper()
    scraper.setup_driver()
    cases = scraper.fetch_and_parse()
    
    print(f"נחלצו {len(cases)} תיקים")
