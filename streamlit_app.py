"""
Streamlit App - מערכת Scraping פנקס תובענות ייצוגיות
ממשק משתמש דינמי וקל לשימוש
"""

import streamlit as st
import pandas as pd
import json
import os
import re
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup

# ⚙️ Streamlit Configuration
st.set_page_config(
    page_title="פנקס תובענות ייצוגיות",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 Title & Branding
st.markdown("""
<style>
    .header-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .header-subtitle {
        text-align: center;
        font-size: 1.2em;
        color: #666;
        margin-bottom: 2em;
    }
</style>

<div class="header-title">⚖️ מערכת Scraping - פנקס תובענות ייצוגיות</div>
<div class="header-subtitle">סקרוף וניתוח של נתוני תיקים בבתי המשפט</div>
""", unsafe_allow_html=True)

# ==================== SCRAPER ====================
class CaseScraper:
    """Israeli Court Case Scraper"""
    
    def __init__(self):
        self.base_url = "https://www.court.gov.il/NGCS.Web.Site/HomePage.aspx"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract_json_from_page(self, html_content):
        """Extract JSON data from hidden input elements"""
        soup = BeautifulSoup(html_content, 'html.parser')
        cases = []
        
        # Find all input elements with data
        for input_elem in soup.find_all('input', {'type': 'hidden'}):
            value = input_elem.get('value', '')
            try:
                if value.startswith('{'):
                    data = json.loads(value)
                    if 'CaseNumber' in data:
                        cases.append(data)
            except json.JSONDecodeError:
                pass
        
        return cases
    
    def fetch_cases(self):
        """Fetch case data from Israeli court website"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            cases = self.extract_json_from_page(response.text)
            return cases if cases else self._get_sample_data()
        except Exception as e:
            st.warning(f"Could not fetch live data: {str(e)}")
            return self._get_sample_data()
    
    def _get_sample_data(self):
        """Return sample data for demo"""
        return [
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
            }
        ]

# ==================== DATA ANALYZER ====================
class DataAnalyzer:
    """Analyze case data"""
    
    @staticmethod
    def analyze(cases):
        """Generate analytics"""
        if not cases:
            return {}
        
        df = pd.DataFrame(cases)
        
        analysis = {
            "total_cases": len(df),
            "total_claim_amount": df.get('ClaimAmount', pd.Series(0)).sum(),
            "avg_plaintiffs": df.get('Plaintiffs', pd.Series(0)).mean(),
            "cases_by_court": df.groupby('Court').size().to_dict() if 'Court' in df.columns else {},
            "cases_by_status": df.groupby('Status').size().to_dict() if 'Status' in df.columns else {}
        }
        
        return analysis

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

# Sidebar
with st.sidebar:
    st.header("🔧 בקרה")
    
    # Mode selection
    mode = st.radio(
        "בחר מצב:",
        ["📊 דוגמה", "🔄 טעינת נתונים"],
        help="בחר בין צפייה בדוגמה או טעינת נתונים חיים"
    )
    
    if mode == "🔄 טעינת נתונים":
        if st.button("⬇️ טען נתונים", key="fetch_btn"):
            with st.spinner("טוען נתונים..."):
                scraper = CaseScraper()
                st.session_state.data = scraper.fetch_cases()
                st.success("נטענו הנתונים!")
    else:
        # Demo mode
        scraper = CaseScraper()
        st.session_state.data = scraper._get_sample_data()

# Main content
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📋 סה\"כ תיקים", len(df))
    
    with col2:
        if 'ClaimAmount' in df.columns:
            total_claim = df['ClaimAmount'].sum()
            st.metric("💰 סה\"כ תביעה", f"₪{total_claim:,.0f}")
        else:
            st.metric("💰 סה\"כ תביעה", "N/A")
    
    with col3:
        if 'Plaintiffs' in df.columns:
            avg_plaintiffs = df['Plaintiffs'].mean()
            st.metric("👥 ממוצע תובעים", f"{avg_plaintiffs:.0f}")
        else:
            st.metric("👥 ממוצע תובעים", "N/A")
    
    # Analysis
    analyzer = DataAnalyzer()
    analysis = analyzer.analyze(st.session_state.data)
    
    st.divider()
    st.header("📈 ניתוח")
    
    # Charts
    tab1, tab2, tab3 = st.tabs(["📊 גרפים", "🔍 חיפוש", "💾 ייצוא"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Court' in df.columns and analysis.get('cases_by_court'):
                fig = px.bar(
                    pd.DataFrame(analysis['cases_by_court'].items(), columns=['Court', 'Count']),
                    x='Court', y='Count',
                    title="תיקים לפי בית משפט",
                    color_discrete_sequence=['#1f77b4']
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Status' in df.columns and analysis.get('cases_by_status'):
                fig = px.pie(
                    pd.DataFrame(analysis['cases_by_status'].items(), columns=['Status', 'Count']),
                    names='Status', values='Count',
                    title="התפלגות סטטוסים"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("🔍 חיפוש בתיקים")
        search_col = st.selectbox("חפש לפי:", df.columns.tolist())
        search_term = st.text_input("הזן טקסט לחיפוש:")
        
        if search_term:
            filtered = df[df[search_col].astype(str).str.contains(search_term, case=False, na=False)]
            st.dataframe(filtered, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
    
    with tab3:
        st.subheader("💾 ייצוא נתונים")
        
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
            json_data = json.dumps(st.session_state.data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 הורד JSON",
                data=json_data,
                file_name=f"cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Data preview
    st.divider()
    st.header("📋 תצוגה מקדימה של נתונים")
    st.dataframe(df, use_container_width=True)

else:
    st.info("📌 לחץ על 'טען נתונים' בתפריט הצד להתחלה")
