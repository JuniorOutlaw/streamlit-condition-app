import streamlit as st
import pandas as pd

import os

# Set working directory to the script's folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- Page Setup ---
st.set_page_config(page_title="Condition Viewer", layout="wide")
st.title("📉 Condition Monitoring Dashboard")

# --- Upload or Load Data ---
uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
else:
    df = pd.read_excel("condition_summary.xlsx")  # fallback default

# --- Assumptions for Columns ---
# Expected columns: ['StartTime', 'Condition', 'TimeUntilAnomaly']
expected_cols = ['StartTime', 'Condition', 'TimeUntilAnomaly']
missing = [col for col in expected_cols if col not in df.columns]

if missing:
    st.error(f"Missing columns in file: {missing}")
    st.stop()

# --- Convert to datetime if needed ---
if not pd.api.types.is_datetime64_any_dtype(df['StartTime']):
    df['StartTime'] = pd.to_datetime(df['StartTime'], errors='coerce')

# --- Slider to limit time range ---
min_time = df['StartTime'].min()
max_time = df['StartTime'].max()

selected_range = st.slider(
    "Select Time Range to Display",
    min_value=min_time,
    max_value=max_time,
    value=(min_time, max_time),
    format="YYYY-MM-DD HH:mm"
)

# --- Filtered Data ---
filtered_df = df[(df['StartTime'] >= selected_range[0]) & (df['StartTime'] <= selected_range[1])]

# --- Display Table ---
st.subheader("📋 Filtered Conditions")
st.dataframe(filtered_df, use_container_width=True)

# --- Optional: Highlight unhealthy conditions ---
st.subheader("❗ Unhealthy Conditions Only")
unhealthy_df = filtered_df[filtered_df['Condition'] != 'Healthy']
st.dataframe(unhealthy_df[['StartTime', 'Condition', 'TimeUntilAnomaly']], use_container_width=True)