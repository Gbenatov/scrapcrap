"""
Streamlit Frontend - מערכת Scraping פנקס תובענות ייצוגיות
ממשק משתמש דינמי וקל לשימוש
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from main_scraper import CaseScraper
from data_analyzer import DataAnalyzer

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

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'last_run' not in st.session_state:
    st.session_state.last_run = None

# 📌 Sidebar - Settings & Actions
with st.sidebar:
    st.header("⚙️ הגדרות וביצוע")
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["🚀 הרצה", "📊 נתונים", "📥 ייצוא"])
    
    with tab1:
        st.subheader("בקרה על ה-Scraper")
        
        scrape_mode = st.radio(
            "בחר מצב:",
            ["🌐 Scrape מהאתר", "📝 דוגמה (ללא download)"]
        )
        
        if scrape_mode == "🌐 Scrape מהאתר":
            timeout = st.slider("Timeout (שניות):", 5, 30, 10)
            retries = st.slider("ניסיונות חוזרים:", 1, 5, 3)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 הרץ עכשיו", use_container_width=True, type="primary"):
                with st.spinner("⏳ סקרוף מתבצע..."):
                    try:
                        scraper = CaseScraper(output_dir="./data")
                        
                        if scrape_mode == "🌐 Scrape מהאתר":
                            html = scraper.fetch_page()
                        else:
                            # Sample HTML for demo
                            html = '''
                            <input type="hidden" id="RepresentativeRegistryGridArrayStore" 
                            value='[
                                {"CaseDisplayIdentifier":"8011-01-25","CaseName":"בז\'נוב נ\' אריסטון","CaseOpenDate":"03/12/2025","CourtName":"אזורי לעבודה חיפה","ClaimAmount":15000000,"CaseID":83300966,"isAppealCase":"0","RepresentativeComplaintGroupName":"עובדים","LegalQuestion":"זכויות עובדים","RequestedAID":"תגמול","Docs":[]},
                                {"CaseDisplayIdentifier":"8012-01-25","CaseName":"דוגמה שניה נ\' נתבע","CaseOpenDate":"04/12/2025","CourtName":"מחוזי תל אביב","ClaimAmount":25000000,"CaseID":83300967,"isAppealCase":"1","RepresentativeComplaintGroupName":"צרכנים","LegalQuestion":"הגנת צרכן","RequestedAID":"פיצוי","Docs":[]}
                            ]' />
                            '''
                        
                        cases = scraper.extract_json_data(html)
                        st.session_state.data = cases
                        
                        if cases:
                            processed = scraper.process_cases(cases)
                            st.session_state.processed_data = processed
                            st.session_state.analyzer = DataAnalyzer(processed)
                            st.session_state.last_run = datetime.now()
                            
                            # Auto-save
                            scraper.save_to_csv(processed)
                            scraper.save_to_json(processed)
                            
                            st.success(f"✅ הרצה הצליחה! חולצו {len(cases)} תיקים")
                        else:
                            st.error("❌ לא נמצאו תיקים")
                    
                    except Exception as e:
                        st.error(f"❌ שגיאה: {str(e)}")
        
        with col2:
            if st.button("🔄 נקה", use_container_width=True):
                st.session_state.data = None
                st.session_state.processed_data = None
                st.session_state.analyzer = None
                st.session_state.last_run = None
                st.success("✅ נקוי הנתונים")
    
    with tab2:
        if st.session_state.processed_data:
            st.subheader("🎯 אפשרויות נתונים")
            
            show_stats = st.checkbox("הצג סטטיסטיקה", value=True)
            show_distribution = st.checkbox("הצג התפלגויות", value=True)
            show_high_value = st.checkbox("תיקי ערך גבוה", value=True)
            
            if show_high_value:
                threshold = st.number_input(
                    "סכום מינימום (₪):",
                    value=10000000,
                    step=1000000
                )
        else:
            st.info("⏳ הרץ את ה-scraper קודם")
    
    with tab3:
        if st.session_state.processed_data:
            st.subheader("💾 ייצוא נתונים")
            
            if st.button("📥 הורד CSV", use_container_width=True):
                df = pd.DataFrame(st.session_state.processed_data)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="לחץ להורדה",
                    data=csv,
                    file_name=f"cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            if st.button("📥 הורד JSON", use_container_width=True):
                json_str = json.dumps(st.session_state.processed_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="לחץ להורדה",
                    data=json_str,
                    file_name=f"cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            st.divider()
            
            if st.button("📊 הורד דוח", use_container_width=True):
                if st.session_state.analyzer:
                    report = st.session_state.analyzer.generate_full_report()
                    json_str = json.dumps(report, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="לחץ להורדה",
                        data=json_str,
                        file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

# 📊 Main Content Area
if st.session_state.processed_data:
    
    # Status Bar
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 סה״כ תיקים", len(st.session_state.processed_data))
    
    with col2:
        total = sum(c.get('סכום_תביעה', 0) for c in st.session_state.processed_data)
        st.metric("💰 סכום כולל", f"₪{total:,.0f}")
    
    with col3:
        courts = len(set(c.get('בית_משפט', '') for c in st.session_state.processed_data))
        st.metric("🏛️ בתי משפט", courts)
    
    with col4:
        if st.session_state.last_run:
            st.metric("⏰ הרצה אחרונה", st.session_state.last_run.strftime("%H:%M:%S"))
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 סטטיסטיקה", "📊 גרפים", "📋 טבלה", "🔍 חיפוש"])
    
    with tab1:
        if st.session_state.analyzer:
            stats = st.session_state.analyzer.get_statistics()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("ממוצע תביעה", f"₪{stats['סכום_ממוצע']:,.0f}")
            
            with col2:
                st.metric("חציון", f"₪{stats['סכום_חציון']:,.0f}")
            
            with col3:
                st.metric("מינימום", f"₪{stats['סכום_מינימום']:,.0f}")
            
            with col4:
                st.metric("מקסימום", f"₪{stats['סכום_מקסימום']:,.0f}")
            
            st.divider()
            
            # Court Distribution
            st.subheader("📊 התפלגות בתי משפט")
            courts = st.session_state.analyzer.get_courts_distribution()
            
            if courts:
                fig = px.bar(
                    x=list(courts.keys()),
                    y=list(courts.values()),
                    title="מספר תיקים לפי בית משפט",
                    labels={"x": "בית משפט", "y": "מספר תיקים"}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Plaintiff Groups
            st.subheader("👥 התפלגות קבוצות תובעים")
            groups = st.session_state.analyzer.get_plaintiff_groups_distribution()
            
            if groups:
                fig = px.pie(
                    names=list(groups.keys()),
                    values=list(groups.values()),
                    title="התפלגות קבוצות תובעים"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Appeal Cases
            st.subheader("⚖️ תיקי ערעור")
            appeal_pct = st.session_state.analyzer.get_appeal_cases_percentage()
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=['תיקים רגילים', 'תיקי ערעור'],
                    values=[100 - appeal_pct, appeal_pct],
                    textposition='auto',
                    textinfo='label+percent'
                )
            ])
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("💰 התפלגות סכומי תביעה")
        
        df = pd.DataFrame(st.session_state.processed_data)
        
        # Histogram
        fig = px.histogram(
            df,
            x='סכום_תביעה',
            nbins=20,
            title="התפלגות סכומי התביעות"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Box plot
        fig = px.box(
            df,
            y='סכום_תביעה',
            title="Box plot - סכומי תביעה"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("📋 טבלת כל התיקים")
        
        df = pd.DataFrame(st.session_state.processed_data)
        
        # Sorting options
        col1, col2 = st.columns(2)
        
        with col1:
            sort_by = st.selectbox(
                "מיין לפי:",
                ["מספר_תיק", "שם_תיק", "סכום_תביעה", "תאריך_פתיחה"]
            )
        
        with col2:
            sort_order = st.radio("סדר:", ["↓ יורד", "↑ עולה"], horizontal=True)
        
        ascending = sort_order == "↑ עולה"
        df_sorted = df.sort_values(by=sort_by, ascending=ascending)
        
        st.dataframe(
            df_sorted,
            use_container_width=True,
            height=500
        )
    
    with tab4:
        st.subheader("🔍 חיפוש וסינון")
        
        search_col = st.selectbox(
            "חפש בשדה:",
            ["שם_תיק", "בית_משפט", "קבוצה_תובעים"]
        )
        
        search_term = st.text_input("הקלד כדי לחפש:")
        
        if search_term:
            df = pd.DataFrame(st.session_state.processed_data)
            filtered = df[df[search_col].str.contains(search_term, case=False, na=False)]
            
            if len(filtered) > 0:
                st.success(f"✅ נמצאו {len(filtered)} תוצאות")
                st.dataframe(filtered, use_container_width=True)
            else:
                st.warning("❌ לא נמצאו תוצאות")
        
        # Filter by amount
        st.divider()
        st.subheader("💰 סינון לפי סכום תביעה")
        
        min_amount = st.number_input("סכום מינימום:", value=0, step=1000000)
        max_amount = st.number_input("סכום מקסימום:", value=100000000, step=1000000)
        
        df = pd.DataFrame(st.session_state.processed_data)
        filtered = df[(df['סכום_תביעה'] >= min_amount) & (df['סכום_תביעה'] <= max_amount)]
        
        st.success(f"✅ נמצאו {len(filtered)} תיקים בטווח זה")
        st.dataframe(filtered, use_container_width=True)

else:
    # Landing Page
    st.info("👈 התחל בלחיצה על 'הרץ עכשיו' בתפריט בצד שמאל")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 המערכת מאפשרת:
        
        ✅ סקרוף נתונים מאתר בית המשפט
        ✅ עיבוד וניקיון נתונים
        ✅ ניתוח סטטיסטי מתקדם
        ✅ ייצוא ל-CSV ו-JSON
        ✅ דוחות ניתוח מלאים
        ✅ חיפוש וסינון קל
        """)
    
    with col2:
        st.markdown("""
        ### 📚 שלבי ההשימוש:
        
        1️⃣ לחץ על "🚀 הרץ עכשיו"
        2️⃣ בחר בין Scrape אמיתי או דוגמה
        3️⃣ המתן להשלמה
        4️⃣ בחן את הנתונים בטבלאות ובגרפים
        5️⃣ הורד את הנתונים בפורמט שלך
        """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.9em;'>
📊 מערכת Scraping - פנקס תובענות ייצוגיות | Version 2.0 | Streamlit Interface
</div>
""", unsafe_allow_html=True)
