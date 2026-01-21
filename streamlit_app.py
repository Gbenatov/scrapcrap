"""
Streamlit App - מערכת Scraping פנקס תובענות ייצוגיות
משתמשת ב-CaseScraper מ-scraper_system
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import sys
import os

# Add scraper_system to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper_system'))

try:
    from main_scraper import CaseScraper
    from data_analyzer import DataAnalyzer
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="פנקס תובענות ייצוגיות",
    page_icon="⚖️",
    layout="wide"
)

# Title
st.title("⚖️ מערכת Scraping - פנקס תובענות ייצוגיות")
st.markdown("סקרוף וניתוח של נתוני תיקים בבתי המשפט")

# Sample data (fallback)
SAMPLE_DATA = [
    {
        "CaseNumber": "CA 2024-001",
        "CaseName": "תובענה ייצוגית ראשונה",
        "Court": "בית משפט מחוזי - תל אביב",
        "FilingDate": "2024-01-15",
        "Status": "פעיל",
        "ClaimAmount": 5000000,
        "Plaintiffs": 150
    },
    {
        "CaseNumber": "CA 2024-002",
        "CaseName": "תובענה ייצוגית שנייה",
        "Court": "בית משפט מחוזי - ירושלים",
        "FilingDate": "2024-02-20",
        "Status": "פעיל",
        "ClaimAmount": 3500000,
        "Plaintiffs": 200
    },
    {
        "CaseNumber": "CA 2024-003",
        "CaseName": "תובענה ייצוגית שלישית",
        "Court": "בית משפט מחוזי - תא גן",
        "FilingDate": "2024-03-10",
        "Status": "בהליכים",
        "ClaimAmount": 7500000,
        "Plaintiffs": 300
    }
]

# Initialize session
if 'data' not in st.session_state:
    st.session_state.data = None

# Sidebar
with st.sidebar:
    st.header("🔧 בקרה")
    
    if SCRAPER_AVAILABLE:
        st.success("✅ Scraper זמין")
        
        if st.button("⬇️ טען נתונים חיים", key="fetch_btn"):
            with st.spinner("טוען נתונים מאתר בתי המשפט..."):
                try:
                    scraper = CaseScraper()
                    cases = scraper.fetch_page_and_extract_cases()
                    
                    if cases:
                        st.session_state.data = cases
                        st.success(f"✅ טען {len(cases)} תיקים בהצלחה!")
                    else:
                        st.warning("לא נמצאו נתונים. משתמש בדוגמה.")
                        st.session_state.data = SAMPLE_DATA
                except Exception as e:
                    st.error(f"❌ שגיאה בטעינה: {str(e)}")
                    st.session_state.data = SAMPLE_DATA
    else:
        st.warning("⚠️ Scraper לא זמין")
    
    st.divider()
    
    if st.button("📊 השתמש בדוגמה", key="demo_btn"):
        st.session_state.data = SAMPLE_DATA

# Initialize with demo data on first load
if st.session_state.data is None:
    st.session_state.data = SAMPLE_DATA

# Main content
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 סה\"כ תיקים", len(df))
    with col2:
        total = df['ClaimAmount'].sum() if 'ClaimAmount' in df.columns else 0
        st.metric("💰 סה\"כ תביעה", f"₪{total:,.0f}")
    with col3:
        avg = df['Plaintiffs'].mean() if 'Plaintiffs' in df.columns else 0
        st.metric("👥 ממוצע תובעים", f"{avg:.0f}")
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 גרפים", "🔍 טבלה", "💾 ייצוא"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            if 'Court' in df.columns:
                court_data = df.groupby('Court').size()
                fig = px.bar(
                    x=court_data.index,
                    y=court_data.values,
                    title="תיקים לפי בית משפט",
                    labels={"x": "בית משפט", "y": "מספר תיקים"}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Status' in df.columns:
                status_data = df.groupby('Status').size()
                fig = px.pie(
                    labels=status_data.index,
                    values=status_data.values,
                    title="התפלגות סטטוסים"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.dataframe(df, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 הורד CSV",
                data=csv,
                file_name=f"cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        with col2:
            json_str = json.dumps(st.session_state.data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 הורד JSON",
                data=json_str,
                file_name=f"cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
