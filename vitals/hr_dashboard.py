# enhanced_heart_dashboard.py
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

DB_NAME = "heart.db"

# -------------------- Fetch Data --------------------
def get_hr_data(start_iso, end_iso):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    query = """
    SELECT ts_iso, bpm FROM heart_rate
    WHERE ts_iso BETWEEN ? AND ?
    ORDER BY ts_iso ASC
    """
    cur.execute(query, (start_iso, end_iso))
    rows = cur.fetchall()
    conn.close()
    
    df = pd.DataFrame(rows, columns=["Time", "BPM"])
    df['Time'] = pd.to_datetime(df['Time'])
    return df

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Heart Rate Dashboard", layout="wide")
st.title("❤️ Heart Rate Dashboard")

st.subheader("Filter Data by Date Range")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.today())
with col2:
    end_date = st.date_input("End Date", datetime.today())

if start_date > end_date:
    st.error("❌ Start date must be before End date.")
else:
    start_iso = datetime.combine(start_date, datetime.min.time()).isoformat()
    end_iso = datetime.combine(end_date, datetime.max.time()).isoformat()
    
    df = get_hr_data(start_iso, end_iso)
    
    if df.empty:
        st.warning("⚠ No data found for the selected date range.")
    else:
        # -------------------- Summary Metrics --------------------
        st.subheader("Summary Metrics")
        avg_bpm = df['BPM'].mean()
        min_bpm = df['BPM'].min()
        max_bpm = df['BPM'].max()
        last_bpm = df['BPM'].iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Average BPM", f"{avg_bpm:.1f}")
        col2.metric("Min BPM", f"{min_bpm}")
        col3.metric("Max BPM", f"{max_bpm}")
        col4.metric("Last Recorded BPM", f"{last_bpm}")
        
        # -------------------- Plot --------------------
        st.subheader("Heart Rate Over Time")
        fig, ax = plt.subplots(figsize=(10,5))
        
        # Color zones
        colors = []
        for bpm in df['BPM']:
            if bpm < 60:
                colors.append('blue')
            elif bpm <= 100:
                colors.append('green')
            else:
                colors.append('red')
        
        ax.scatter(df['Time'], df['BPM'], color=colors, label="BPM")
        
        # Rolling average (window = 5 readings)
        df['BPM_avg'] = df['BPM'].rolling(window=5, min_periods=1).mean()
        ax.plot(df['Time'], df['BPM_avg'], color='orange', linestyle='-', label="Rolling Avg (5)")
        
        ax.set_xlabel("Time")
        ax.set_ylabel("Heart Rate (BPM)")
        ax.set_title("Heart Rate Over Time with Zones & Rolling Average")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)
        
        # -------------------- Data Table --------------------
        st.subheader("Heart Rate Data Table")
        st.dataframe(df[['Time', 'BPM']])
        
        # -------------------- CSV Download --------------------
        csv = df[['Time', 'BPM']].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"heart_rate_{start_date}_{end_date}.csv",
            mime='text/csv'
        )
