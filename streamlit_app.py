"""
Streamlit App - Data Scraper and Exporter
ממשק אינטראקטיבי להזנת URLs וייצוא נתונים
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
from bs4 import BeautifulSoup
import requests

# Page config
st.set_page_config(
    page_title="Data Scraper & Exporter",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Data Scraper & Exporter")
st.markdown("הזן URL ובחר שדות לייצוא")

# Initialize session
if 'data' not in st.session_state:
    st.session_state.data = None
if 'columns_info' not in st.session_state:
    st.session_state.columns_info = {}

# Sidebar - Input Options
with st.sidebar:
    st.header("🔧 אפשרויות")
    
    input_method = st.radio(
        "בחר אפשרות קלט:",
        ["🌐 הזן URL", "📁 העלה קובץ", "📋 דוגמה"]
    )
    
    # Method 1: URL Input
    if input_method == "🌐 הזן URL":
        st.subheader("הזן URL")
        url = st.text_input(
            "כתובת האתר:",
            placeholder="https://example.com",
            key="url_input"
        )
        
        if st.button("⬇️ טען דף", key="load_url"):
            with st.spinner("טוען דף..."):
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # חילוץ טבלאות
                    tables = pd.read_html(url)
                    
                    if tables:
                        st.session_state.data = tables[0]
                        st.success(f"✅ טען {len(tables)} טבלה/ות")
                    else:
                        st.warning("לא נמצאו טבלאות בדף")
                        
                except Exception as e:
                    st.error(f"❌ שגיאה: {str(e)}")
    
    # Method 2: File Upload
    elif input_method == "📁 העלה קובץ":
        st.subheader("העלה קובץ")
        uploaded_file = st.file_uploader(
            "בחר קובץ CSV או Excel:",
            type=['csv', 'xlsx', 'xls'],
            key="file_upload"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    st.session_state.data = pd.read_csv(uploaded_file)
                else:
                    st.session_state.data = pd.read_excel(uploaded_file)
                st.success("✅ קובץ טען בהצלחה")
            except Exception as e:
                st.error(f"❌ שגיאה בטעינת קובץ: {str(e)}")
    
    # Method 3: Sample Data
    else:
        st.subheader("דוגמה")
        sample_data = {
            "CaseNumber": ["CA 2024-001", "CA 2024-002", "CA 2024-003"],
            "CaseName": ["תובענה 1", "תובענה 2", "תובענה 3"],
            "Court": ["תל אביב", "ירושלים", "תא גן"],
            "Status": ["פעיל", "פעיל", "בהליכים"],
            "Amount": [5000000, 3500000, 7500000]
        }
        st.session_state.data = pd.DataFrame(sample_data)
        st.success("✅ נטען נתוני דוגמה")

# Main content
if st.session_state.data is not None:
    df = st.session_state.data
    
    # Show data info
    st.subheader("📋 מידע על הנתונים")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("שורות", len(df))
    with col2:
        st.metric("עמודות", len(df.columns))
    with col3:
        st.metric("גודל", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    
    st.divider()
    
    # Column selection and transformation
    st.subheader("🔧 בחר עמודות לייצוא")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Select columns to export
        available_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "בחר עמודות:",
            available_columns,
            default=available_columns,
            key="column_select"
        )
    
    with col2:
        # Filter rows
        if len(df) > 0:
            max_rows = len(df)
            num_rows = st.number_input(
                "מספר שורות:",
                min_value=1,
                max_value=max_rows,
                value=min(100, max_rows),
                key="row_filter"
            )
        else:
            num_rows = 0
    
    st.divider()
    
    # Create filtered dataframe
    if selected_columns:
        filtered_df = df[selected_columns].head(num_rows)
        
        # Show preview
        st.subheader("👁️ תצוגה מקדימה")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Statistics
        st.subheader("📊 סטטיסטיקה")
        
        # Numeric columns only
        numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    filtered_df[[numeric_cols[0]]].describe().T,
                    title=f"סטטיסטיקה: {numeric_cols[0]}"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            if len(numeric_cols) > 1:
                with col2:
                    fig = px.bar(
                        filtered_df[[numeric_cols[1]]].describe().T,
                        title=f"סטטיסטיקה: {numeric_cols[1]}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Export options
        st.subheader("💾 ייצוא נתונים")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = filtered_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV",
                data=csv_data,
                file_name=f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            json_data = json.dumps(filtered_df.to_dict(orient='records'), ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 JSON",
                data=json_data,
                file_name=f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col3:
            excel_data = filtered_df.to_excel(index=False)
            st.download_button(
                label="📥 Excel",
                data=excel_data,
                file_name=f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    else:
        st.warning("⚠️ בחר לפחות עמודה אחת")

else:
    st.info("👈 בחר אפשרות בתפריט הצד כדי להתחיל")
