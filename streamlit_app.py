"""
Streamlit App - Wrapper for Streamlit Cloud Deployment
מערכת Scraping - פנקס תובענות ייצוגיות
"""

import sys
import os

# הוסף את scraper_system לPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper_system'))

# עכשיו טען את app.py מ-scraper_system
exec(open(os.path.join(os.path.dirname(__file__), 'scraper_system', 'app.py')).read())
