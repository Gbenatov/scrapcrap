#!/bin/bash
# 🚀 הרץ את ה-Streamlit Frontend

cd "$(dirname "$0")"

# בדוק אם streamlit מותקן
if ! command -v streamlit &> /dev/null; then
    echo "📦 מתקין Streamlit..."
    pip install -r requirements.txt
fi

echo ""
echo "🚀 מכינים את ה-Frontend..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚖️  מערכת Scraping - פנקס תובענות ייצוגיות"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ הממשק הדינמי מתחיל בעוד רגע..."
echo "📱 יפתח בדפדפן שלך ב: http://localhost:8501"
echo ""

streamlit run app.py
