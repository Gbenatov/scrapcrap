#!/usr/bin/env python3
"""
Main entry point for the scraping system
Complete pipeline: Scrape -> Process -> Analyze -> Export
"""

import logging
import sys
from pathlib import Path

from main_scraper import CaseScraper
from data_analyzer import DataAnalyzer
from config import LOGGING_CONFIG, ensure_directories

# Setup logging
logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['log_file']),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main pipeline execution"""
    logger.info("=" * 60)
    logger.info("מערכת Scraping - פנקס תובענות ייצוגיות")
    logger.info("=" * 60)
    
    try:
        # Ensure directories exist
        ensure_directories()
        
        # Initialize scraper
        scraper = CaseScraper(output_dir="./data")
        
        # Run scraper
        logger.info("שלב 1: Scraping...")
        html_content = scraper.fetch_page()
        cases = scraper.extract_json_data(html_content)
        
        if not cases:
            logger.error("לא נמצאו תיקים")
            return 1
        
        # Process cases
        logger.info("שלב 2: עיבוד נתונים...")
        processed_cases = scraper.process_cases(cases)
        
        # Export data
        logger.info("שלב 3: ייצוא נתונים...")
        scraper.save_to_csv(processed_cases)
        scraper.save_to_json(processed_cases)
        
        # Analyze data
        logger.info("שלב 4: ניתוח נתונים...")
        analyzer = DataAnalyzer(processed_cases)
        report = analyzer.generate_full_report()
        
        # Save analysis report
        import json
        import os
        report_path = os.path.join(scraper.output_dir, "analysis_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"דוח ניתוח שמור ל-{report_path}")
        
        # Generate report
        logger.info("שלב 5: דוח סטטיסטי...")
        scraper.generate_report(processed_cases)
        
        logger.info("=" * 60)
        logger.info("✅ ההרצה הסתיימה בהצלחה!")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ שגיאה קריטית: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
