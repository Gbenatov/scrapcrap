# 🎨 מערכת Scraping - פנקס תובענות ייצוגיות

מערכת Python **מלאה וקל להשתמש** לscraping וניתוח של נתוני תובענות ייצוגיות מאתר בית המשפט הישראלי.

## 🎯 תכונות עיקריות

✅ **Streamlit Frontend** - ממשק משתמש דינמי וקל
✅ **JSON Extraction** - חילוץ נתונים JSON מה-HTML
✅ **Data Processing** - ניקיון והכנת נתונים
✅ **Multi-Format Export** - CSV, JSON, דוחות
✅ **Analytics Dashboard** - גרפים וסטטיסטיקה
✅ **Search & Filter** - חיפוש וסינון קל
✅ **Hebrew Support** - תמיכה מלאה בעברית

## 🚀 התחלה מהירה

### דרך 1: Streamlit (מומלץ)
```bash
cd scraper_system
./start.sh
```

ממשק יפתח ב: **http://localhost:8501**

### דרך 2: Command Line
```bash
cd scraper_system
python run.py
```

### דרך 3: Python API
```python
from main_scraper import CaseScraper
scraper = CaseScraper()
cases = scraper.extract_json_data(scraper.fetch_page())
```

## 📱 ממשק Streamlit

### פאנלים עיקריים:
1. **🚀 הרצה** - Run scraper עם הגדרות
2. **📈 סטטיסטיקה** - Metrics וגרפים
3. **📊 גרפים** - Visualization
4. **📋 טבלה** - צפייה בנתונים
5. **🔍 חיפוש** - חיפוש וסינון
6. **📥 ייצוא** - הורדת קבצים

## 📚 תיעוד

| קובץ | תיאור |
|------|-------|
| [FRONTEND.md](FRONTEND.md) | מדריך Frontend |
| [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) | מדריך מפורט |
| [USAGE.md](USAGE.md) | תיעוד API |
| [STATUS.md](STATUS.md) | סטטוס כללי |

## 🔧 התקנה

```bash
pip install -r requirements.txt
```

## הנתונים המופקים

- **מספר תיק** - מזהה תיק
- **שם תיק** - שם המוקד
- **תאריך פתיחה** - מתי הוגש
- **בית משפט** - מיקום
- **סכום תביעה** - סכום בדוקים
- **קבוצת תובעים** - שם הקבוצה
- **וועד ייצוג** - פרטי הוועד

## פלט

```
data/
├── cases.csv           # נתונים בformат CSV
├── cases.json          # נתונים בformט JSON
└── report.json         # דוח סטטיסטי
```

## בעיות ידועות ופתרונות

### בעיה: Timeout
```python
response.timeout = 20  # הגביל זמן
```

### בעיה: JavaScript אתרים
```python
# השתמש ב-Selenium למקרה צורך
from selenium import webdriver
driver = webdriver.Chrome()
```

## מבנה הנתונים

כל תיק מכיל:
```json
{
  "מספר_תיק": "8011-12-25",
  "שם_תיק": "בז'נוב נ' אריסטון",
  "סכום_תביעה": 15000000,
  ...
}
```
