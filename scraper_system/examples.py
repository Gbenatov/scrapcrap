#!/usr/bin/env python3
"""
Quick Start Example - מעדכון בדוגמה פשוטה של מערכת
"""

import json
from main_scraper import CaseScraper
from data_analyzer import DataAnalyzer

print("=" * 60)
print("מערכת Scraping - פנקס תובענות ייצוגיות")
print("=" * 60)
print()

# דוגמה 1: Scraping פשוט
print("דוגמה 1: Download של נתונים")
print("-" * 40)

try:
    scraper = CaseScraper()
    print("✓ Scraper initialized")
    
    print("  הורדת דף...")
    # במקרה הזה נשתמש בHTML לדוגמה כי לא אנחנו רוצים להוריד כל פעם
    # בפועל: html = scraper.fetch_page()
    
    # דוגמה ל-HTML עם תיקים
    sample_html = '''
    <input type="hidden" id="RepresentativeRegistryGridArrayStore" 
    value='[
        {"CaseDisplayIdentifier":"8011-01-25","CaseName":"בז\'נוב נ\' אריסטון","CaseOpenDate":"03/12/2025","CourtName":"אזורי לעבודה חיפה","ClaimAmount":15000000,"CaseID":83300966,"isAppealCase":"0","RepresentativeComplaintGroupName":"עובדים","LegalQuestion":"זכויות עובדים","RequestedAID":"תגמול","Docs":[]},
        {"CaseDisplayIdentifier":"8012-01-25","CaseName":"דוגמה שניה נ\' נתבע","CaseOpenDate":"04/12/2025","CourtName":"מחוזי תל אביב","ClaimAmount":25000000,"CaseID":83300967,"isAppealCase":"1","RepresentativeComplaintGroupName":"צרכנים","LegalQuestion":"הגנת צרכן","RequestedAID":"פיצוי","Docs":[]}
    ]' />
    '''
    
    print("  חילוץ נתונים...")
    cases = scraper.extract_json_data(sample_html)
    print(f"✓ נחלצו {len(cases)} תיקים")
    
    print("  עיבוד נתונים...")
    processed = scraper.process_cases(cases)
    print(f"✓ נעובדו {len(processed)} תיקים")
    
except Exception as e:
    print(f"✗ שגיאה: {e}")

print()

# דוגמה 2: ניתוח
print("דוגמה 2: ניתוח נתונים")
print("-" * 40)

try:
    analyzer = DataAnalyzer(processed)
    
    print("  קבלת סטטיסטיקה...")
    stats = analyzer.get_statistics()
    print(f"✓ סה\"כ תיקים: {stats['סה\"כ_תיקים']}")
    print(f"  סכום כולל: ₪{stats['סה\"כ_סכומים']:,.0f}")
    print(f"  סכום ממוצע: ₪{stats['סכום_ממוצע']:,.0f}")
    
    print()
    print("  התפלגות בתי משפט:")
    courts = analyzer.get_courts_distribution()
    for court, count in list(courts.items())[:5]:
        print(f"    • {court}: {count}")
    
    print()
    print("  תיקי ערעור:")
    appeal_pct = analyzer.get_appeal_cases_percentage()
    print(f"    אחוז: {appeal_pct:.1f}%")
    
except Exception as e:
    print(f"✗ שגיאה: {e}")

print()

# דוגמה 3: Export
print("דוגמה 3: ייצוא נתונים")
print("-" * 40)

try:
    print("  שמירה ל-CSV...")
    scraper.save_to_csv(processed, "example_cases.csv")
    print("✓ שמור ל-data/example_cases.csv")
    
    print("  שמירה ל-JSON...")
    scraper.save_to_json(processed, "example_cases.json")
    print("✓ שמור ל-data/example_cases.json")
    
except Exception as e:
    print(f"✗ שגיאה: {e}")

print()

# דוגמה 4: דוח מלא
print("דוגמה 4: דוח ניתוח מלא")
print("-" * 40)

try:
    report = analyzer.generate_full_report()
    print("✓ נוצר דוח ניתוח")
    
    # הצגה בעברית
    print()
    print("תיקי ערך גבוה:")
    for case in report['תיקי_ערך_גבוה'][:3]:
        print(f"  • {case['שם_תיק']}")
        print(f"    סכום: ₪{case['סכום_תביעה']:,.0f}")
        print(f"    בית משפט: {case['בית_משפט']}")
    
except Exception as e:
    print(f"✗ שגיאה: {e}")

print()
print("=" * 60)
print("✅ דוגמאות הסתיימו בהצלחה!")
print("=" * 60)
print()
print("הצעדים הבאים:")
print("1. הרץ את: python run.py")
print("2. בדוק את הנתונים ב-data/")
print("3. קרא את USAGE.md לעם מידע נוסף")
