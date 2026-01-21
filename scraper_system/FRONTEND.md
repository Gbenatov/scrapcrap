# 🎨 Frontend Streamlit - מערכת Scraping

ממשק משתמש דינמי וקל לשימוש לscraping וניתוח נתוני פנקס התובענות הייצוגיות.

## 🚀 הפעלה מהירה

### דרך 1: Bash Script (הדרך הקלה)
```bash
cd scraper_system
./start.sh
```

### דרך 2: Streamlit ישיר
```bash
cd scraper_system
streamlit run app.py
```

### דרך 3: עם Python
```bash
cd scraper_system
python -m streamlit run app.py
```

## 📱 תכונות ממשק

### 🚀 שלב 1: הרצה
```
בחר:
- 🌐 Scrape מהאתר (download אמיתי)
- 📝 דוגמה (ללא download)

הגדר:
- Timeout (שניות)
- ניסיונות חוזרים

ולחץ: 🚀 הרץ עכשיו
```

### 📊 שלב 2: ניתוח

**4 כרטיסיות:**

1. **📈 סטטיסטיקה**
   - Metrics (סה״כ, סכום, בתי משפט)
   - Bar chart - בתי משפט
   - Pie chart - קבוצות תובעים
   - Pie chart - תיקי ערעור

2. **📊 גרפים**
   - Histogram - התפלגות סכומים
   - Box plot - outliers וטווח

3. **📋 טבלה**
   - כל התיקים
   - מיון לפי עמודה
   - צפייה אינטראקטיבית

4. **🔍 חיפוש**
   - חיפוש טקסט
   - סינון לפי סכום
   - תוצאות מיידיות

### 📥 שלב 3: ייצוא

**3 פורמטים:**

1. **📥 CSV**
   ```
   מספר_תיק,שם_תיק,סכום_תביעה,...
   ```

2. **📥 JSON**
   ```json
   [{"מספר_תיק":"..."}]
   ```

3. **📊 דוח**
   ```json
   {
     "סטטיסטיקה_בסיסית": {...},
     "התפלגות": {...}
   }
   ```

## 🎯 דוגמאות שימוש

### דוגמה 1: Scrape ו-Export (2 דקות)
```
1. לחץ 🚀 הרץ עכשיו
2. בחר 🌐 Scrape מהאתר
3. המתן 15-30 שניות
4. לחץ 📥 הורד CSV
5. קבל את הנתונים
```

### דוגמה 2: ניתוח מהיר (30 שניות)
```
1. לחץ 🚀 הרץ עכשיו
2. בחר 📝 דוגמה
3. בחן את הגרפים
4. חפש בחלק 🔍
```

### דוגמה 3: סינון תיקים גדולים
```
1. הרץ scraper
2. לך ל 🔍 חיפוש
3. הגדר סכום מינימום: 20M
4. ראה את התיקים המשמעותיים
```

## 📊 מבנה הממשק

### Sidebar (צד שמאל)
```
⚙️ הגדרות וביצוע
├── 🚀 הרצה
│   ├── בחר מצב (Scrape/דוגמה)
│   ├── הגדרות (timeout, retries)
│   └── כפתורים (הרץ, נקה)
├── 📊 נתונים
│   ├── סטטיסטיקה
│   ├── התפלגויות
│   └── תיקי ערך גבוה
└── 📥 ייצוא
    ├── הורד CSV
    ├── הורד JSON
    └── הורד דוח
```

### Main Area (אמצע)
```
📊 STATUS BAR
├── סה״כ תיקים
├── סכום כולל
├── בתי משפט
└── שעת הרצה

📈 TABS
├── סטטיסטיקה + גרפים
├── גרפים advanced
├── טבלה אינטראקטיבית
└── חיפוש וסינון
```

## 🔧 טכנולוגיה

| Component | Version |
|-----------|---------|
| Streamlit | 1.28.1 |
| Plotly | 5.18.0 |
| Pandas | 2.1.3 |
| Python | 3.8+ |

## 📈 גרפים שזמינים

### בעמוד סטטיסטיקה:
- ✅ Bar chart - בתי משפט
- ✅ Pie chart - קבוצות תובעים
- ✅ Pie chart - תיקי ערעור

### בעמוד גרפים:
- ✅ Histogram - התפלגות סכומים
- ✅ Box plot - ניתוח outliers

## 💾 ייצוא מתמטי

### CSV
```python
df.to_csv(encoding='utf-8-sig')  # with BOM
```

### JSON
```python
json.dumps(data, ensure_ascii=False, indent=2)
```

### דוח
```python
analyzer.generate_full_report()
```

## 🐛 Troubleshooting

### ❓ הממשק לא נפתח
```bash
# בדוק שStreamlit מותקן
pip install streamlit

# נסה בכתובת אחרת
streamlit run app.py --server.port=8502
```

### ❓ Scrape לא עובד
```
1. בדוק connection אל האתר
2. נסה דוגמה קודם
3. הגדל timeout ל-20 שניות
```

### ❓ גרפים לא מופיעים
```
1. רענן את הדף (F5)
2. סגור ופתח מחדש
3. בדוק שיש נתונים
```

## 📚 קבצים קשורים

- [app.py](app.py) - קוד Streamlit
- [main_scraper.py](main_scraper.py) - קוד ה-scraping
- [data_analyzer.py](data_analyzer.py) - ניתוח נתונים
- [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) - מדריך מפורט

## 🎨 ממשק משתמש

### צבעים ועיצוב
- ✅ ירוק - SUCCESS
- ✅ אדום - ERROR
- ✅ כחול - INFO
- ✅ צהוב - WARNING

### סמלים וEmojis
```
⚖️  - Header
🚀  - Action
📊  - Data
📈  - Charts
💾  - Export
🔍  - Search
✅  - Success
❌  - Error
⏳  - Loading
```

## 🚀 Features Pipeline

```
Input (Scraper)
     ↓
Processing (Clean & Validate)
     ↓
Analysis (Statistics & Visualization)
     ↓
Output (CSV/JSON/Report)
```

## 📞 Support

- בעיות? בדוק את [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)
- עזרה ב-scraper? ראה [USAGE.md](USAGE.md)
- שאלות על קוד? ראה [STATUS.md](STATUS.md)

## 🎯 Quick Links

| קישור | תיאור |
|-------|-------|
| http://localhost:8501 | הממשק |
| [app.py](app.py) | קוד ממשק |
| [data/](data/) | תוצאות |
| [logs/](logs/) | logs |

---

**Version:** 2.0 Frontend
**Status:** ✅ Ready to Use
**Last Updated:** 2025-01-21
