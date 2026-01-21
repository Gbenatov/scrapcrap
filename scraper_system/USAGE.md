# תיעוד שימוש - מערכת Scraping פנקס תובענות ייצוגיות

## 📋 תוכן העניינים
1. [התקנה](#התקנה)
2. [שימוש בסיסי](#שימוש-בסיסי)
3. [תכונות](#תכונות)
4. [דוגמאות](#דוגמאות)
5. [בעיות נפוצות](#בעיות-נפוצות)
6. [API Reference](#api-reference)

## 🔧 התקנה

### דרישות מקדימות
- Python 3.8+
- pip

### שלבי התקנה
```bash
cd scraper_system

# יצירת virtual environment (אופציונלי אך מומלץ)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# התקנת dependencies
pip install -r requirements.txt

# עריכת .env (אופציונלי)
cp .env.example .env
```

## 🚀 שימוש בסיסי

### דרך מהירה (one-liner)
```bash
python run.py
```

זה יעשה:
1. ✅ Download של דף HTML מהאתר
2. ✅ Parsing וחילוץ JSON
3. ✅ עיבוד נתונים
4. ✅ ייצוא ל-CSV ו-JSON
5. ✅ יצירת דוח ניתוח

### שימוש Advanced
```python
from main_scraper import CaseScraper
from data_analyzer import DataAnalyzer

# יצירת Scraper
scraper = CaseScraper(output_dir="./data")

# הרצה
html = scraper.fetch_page()
cases = scraper.extract_json_data(html)
processed = scraper.process_cases(cases)

# Export
scraper.save_to_csv(processed)
scraper.save_to_json(processed)

# Analysis
analyzer = DataAnalyzer(processed)
stats = analyzer.get_statistics()
print(stats)
```

## ✨ תכונות

### 1. Scraping דינמי
```python
scraper = CaseScraper()
cases = scraper.extract_json_data(html_content)
```

### 2. עיבוד נתונים
```python
processed = scraper.process_cases(raw_cases)
# תרגום לשמות עברים וניקיון נתונים
```

### 3. Export מרובה
```python
scraper.save_to_csv(cases)    # CSV
scraper.save_to_json(cases)   # JSON
```

### 4. ניתוח חכם
```python
analyzer = DataAnalyzer(cases)
analyzer.get_statistics()           # סטטיסטיקה בסיסית
analyzer.get_courts_distribution()  # חלוקה לפי בתי משפט
analyzer.get_high_value_cases()     # תיקים בסכום גבוה
```

## 📊 דוגמאות

### דוגמה 1: סקרפינג פשוט
```python
from main_scraper import CaseScraper

scraper = CaseScraper()
html = scraper.fetch_page()
cases = scraper.extract_json_data(html)
scraper.save_to_json(cases)
```

### דוגמה 2: ניתוח מלא
```python
from main_scraper import CaseScraper
from data_analyzer import DataAnalyzer
import json

scraper = CaseScraper()
html = scraper.fetch_page()
cases = scraper.extract_json_data(html)
processed = scraper.process_cases(cases)

analyzer = DataAnalyzer(processed)
report = analyzer.generate_full_report()

with open('report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
```

### דוגמה 3: סנון תיקי עלות גבוהה
```python
from main_scraper import CaseScraper
from data_analyzer import DataAnalyzer

scraper = CaseScraper()
html = scraper.fetch_page()
cases = scraper.extract_json_data(html)
processed = scraper.process_cases(cases)

analyzer = DataAnalyzer(processed)
high_value = analyzer.get_high_value_cases(threshold=20000000)

print(f"נמצאו {len(high_value)} תיקים בעלות גבוהה")
for case in high_value[:5]:
    print(f"  {case['שם_תיק']}: {case['סכום_תביעה']:,.0f}")
```

### דוגמה 4: Scraping Selenium (דינמי)
```python
from advanced_scraper import AdvancedCaseScraper

scraper = AdvancedCaseScraper()
scraper.setup_driver()
cases = scraper.fetch_and_parse()
print(f"Extracted {len(cases)} cases")
```

## 🐛 בעיות נפוצות

### בעיה: Connection Timeout
```
ConnectionError: HTTPConnectionPool... Max retries exceeded
```

**פתרון:**
```python
scraper.session.timeout = 20  # הגדל זמן
# או
import requests
requests.packages.urllib3.util.retry.Retry(
    total=5,
    backoff_factor=0.5
)
```

### בעיה: Encoding שגוי
```
UnicodeDecodeError: 'utf-8' codec can't decode
```

**פתרון:**
```python
response.encoding = 'utf-8'  # מוגדר כברירת מחדל
```

### בעיה: JSON לא נמצא
```
Warning: לא נמצא input עם RepresentativeRegistryGridArrayStore
```

**פתרון:**
- האתר אולי שונה
- נסה Selenium (advanced_scraper.py)
- בדוק שהאתר תמיד זמין

### בעיה: בעיות בתוך Selenium
```
chromedriver version mismatch
```

**פתרון:**
```bash
pip install webdriver-manager
# ואז שנה ב-advanced_scraper.py:
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
```

## 📚 API Reference

### CaseScraper

#### `__init__(output_dir: str = "data")`
יצירת Scraper חדש

#### `fetch_page() -> str`
הורדת דף HTML

#### `extract_json_data(html_content: str) -> List[Dict]`
חילוץ נתוני JSON

#### `process_cases(cases: List[Dict]) -> List[Dict]`
עיבוד וניקיון נתונים

#### `save_to_csv(cases, filename)`
ייצוא ל-CSV

#### `save_to_json(cases, filename)`
ייצוא ל-JSON

### DataAnalyzer

#### `get_statistics() -> Dict`
סטטיסטיקה בסיסית

#### `get_courts_distribution() -> Dict`
התפלגות בתי משפט

#### `get_plaintiff_groups_distribution() -> Dict`
התפלגות קבוצות תובעים

#### `get_appeal_cases_percentage() -> float`
אחוז תיקי ערעור

#### `get_high_value_cases(threshold) -> List`
תיקים בעלות גבוהה

#### `generate_full_report() -> Dict`
דוח מלא

## 📁 מבנה פלט

```
data/
├── cases.csv              # CSV של כל התיקים
├── cases.json             # JSON של כל התיקים
├── report.json            # דוח סטטיסטי
└── analysis_report.json   # דוח ניתוח מתקדם

logs/
└── scraper.log            # Log של כל ההרצות
```

## 🔍 שדות הנתונים

כל תיק מכיל:

| שדה | תיאור |
|-----|-------|
| `מספר_תיק` | מזהה תיק (e.g., "8011-12-25") |
| `שם_תיק` | שם המוקד (e.g., "בז'נוב נ' אריסטון") |
| `תאריך_פתיחה` | תאריך הגשה |
| `בית_משפט` | בית משפט (e.g., "אזורי לעבודה חיפה") |
| `קבוצה_תובעים` | קבוצת התובעים |
| `שאלה_משפטית` | השאלה המשפטית |
| `סעד_מבוקש` | הסעד הנדרש |
| `סכום_תביעה` | סכום התביעה (מספר) |
| `מספר_תיק_id` | ID פנימי |
| `תיק_ערעור` | האם זה תיק ערעור ("0" או "1") |
| `מספר_מסמכים` | מספר מסמכים מצורפים |

## 🧪 בדיקות

הרצת בדיקות Unit:
```bash
python test_scraper.py
```

או עם verbose:
```bash
python test_scraper.py -v
```

## 📝 הערות חשובות

1. **זכויות**: בדוק את תנאי השימוש של האתר
2. **Throttling**: כדי לא לעמוס את השרתים, הוסף עיכובים
3. **Caching**: שמור את ה-HTML המקומי כדי לא להוריד בכל פעם
4. **Errors**: בדוק את `logs/scraper.log` לעם בעיות

## 📧 תמיכה

אם יש בעיות, בדוק:
1. קובץ log ב-`logs/scraper.log`
2. בדוק את תקינות ה-HTML
3. נסה Selenium (advanced_scraper.py)
