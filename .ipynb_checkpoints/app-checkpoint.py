import streamlit as st
import pandas as pd
import os

# Optional: Set working directory if running locally (comment this out before cloud deployment)
# os.chdir("/Users/sushant/Desktop/ITC/JIPITE")

# --- Page Setup ---
st.set_page_config(page_title="Condition Viewer", layout="centered")
st.title("📉 Condition Monitoring Dashboard")

# --- Upload or Load Excel ---
uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
else:
    try:
        df = pd.read_excel("condition_summary.xlsx")
    except FileNotFoundError:
        st.error("No file uploaded and default 'condition_summary.xlsx' not found.")
        st.stop()

# --- Required Columns Check ---
expected_cols = ['StartTime', 'Condition', 'TimeUntilAnomaly']
missing = [col for col in expected_cols if col not in df.columns]
if missing:
    st.error(f"Missing columns in file: {missing}")
    st.stop()

# --- Ensure StartTime is datetime ---
if not pd.api.types.is_datetime64_any_dtype(df['StartTime']):
    df['StartTime'] = pd.to_datetime(df['StartTime'], errors='coerce')

# --- Sort by StartTime ---
df = df.sort_values("StartTime").reset_index(drop=True)

# --- Slider to select a single row by index ---
st.markdown("### ⏳ Select a Time Point")
row_index = st.slider(
    "Use the slider to browse rows",
    min_value=0,
    max_value=len(df) - 1,
    value=len(df) - 1,  # default to most recent
    format="%d"
)

# --- Get selected row ---
selected_row = df.iloc[row_index]
condition = selected_row['Condition']
time_until_anomaly = selected_row['TimeUntilAnomaly']
start_time = selected_row['StartTime']

# --- Custom CSS ---
st.markdown("""
<style>
.blinking {
    animation: blinker 1s linear infinite;
}
@keyframes blinker {
    50% { opacity: 0.4; }
}
.status-box {
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    color: black;
}
.healthy {
    background-color: #d1ffd6;
}
.unhealthy {
    background-color: #ffe0e0;
}
.time-box {
    padding: 1rem;
    border-radius: 10px;
    background-color: #f0f0f0;
    text-align: center;
    font-size: 22px;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# --- Display Start Time ---
st.markdown(f"**🕒 Selected Start Time:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# --- Condition Box ---
st.markdown("### 📦 Current Condition Status")
box_class = "status-box healthy" if condition == "Healthy" else "status-box unhealthy blinking"
st.markdown(f"<div class='{box_class}'>{condition}</div>", unsafe_allow_html=True)

# --- Time Until Anomaly Box ---
st.markdown("### ⏱️ Time Until Anomaly")
time_display = "NA" if condition == "Healthy" else f"{time_until_anomaly} minutes"
st.markdown(f"<div class='time-box'>{time_display}</div>", unsafe_allow_html=True)