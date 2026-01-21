"""
Streamlit App - מערכת Scraping פנקס תובענות ייצוגיות
ממשק משתמש דינמי וקל לשימוש
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px

# Page config
st.set_page_config(
    page_title="פנקס תובענות ייצוגיות",
    page_icon="⚖️",
    layout="wide"
)

# Title
st.title("⚖️ מערכת Scraping - פנקס תובענות ייצוגיות")
st.markdown("סקרוף וניתוח של נתוני תיקים בבתי המשפט")

# Sample data
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
    st.session_state.data = SAMPLE_DATA

# Sidebar
with st.sidebar:
    st.header("🔧 בקרה")
    st.info("ℹ️ דוגמה של נתוני תיקים")

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
