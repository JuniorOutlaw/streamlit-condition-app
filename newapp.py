import streamlit as st
import pandas as pd
import os

# --- Page Setup ---
st.set_page_config(page_title="Condition Viewer", layout="centered")
st.title("Predictive Maintenance Dashboard")

# --- Load Fixed Excel File ---
try:
    df = pd.read_excel("forecast_status_output.xlsx")
except FileNotFoundError:
    st.error("❌ 'forecast_status_output.xlsx' not found in current directory.")
    st.stop()

# --- Required Columns Check ---
expected_cols = ['ForecastStart', 'Status', 'TimeUntilFault']
missing = [col for col in expected_cols if col not in df.columns]
if missing:
    st.error(f"Missing columns in file: {missing}")
    st.stop()

# --- Ensure ForecastStart is datetime ---
df['ForecastStart'] = pd.to_datetime(df['ForecastStart'], errors='coerce')
df = df.sort_values("ForecastStart").reset_index(drop=True)

# --- Anomalous Points Index List ---
anomalous_indices = df[df['Status'] == 'Anomalous'].index.tolist()
forecast_times = df['ForecastStart'].dt.to_pydatetime().tolist()

# --- Initialize Session State ---
if 'selected_time' not in st.session_state:
    st.session_state.selected_time = forecast_times[-1]  # default: latest

# --- Layout: Buttons Side by Side ---
col1, col2 = st.columns(2)

# 🔁 Previous Anomalous Point
with col1:
    if st.button("⬅️ Previous Anomalous Point"):
        current_index = df[df['ForecastStart'] == st.session_state.selected_time].index[0]
        prev_anomalous = df[(df.index < current_index) & (df['Status'] == "Anomalous")]
        if not prev_anomalous.empty:
            st.session_state.selected_time = prev_anomalous.iloc[-1]['ForecastStart']
            st.rerun()
        else:
            st.warning("🚫 No previous anomalous points found.")

# 🔁 Next Anomalous Point
with col2:
    if st.button("➡️ Next Anomalous Point"):
        current_index = df[df['ForecastStart'] == st.session_state.selected_time].index[0]
        next_anomalous = df[(df.index > current_index) & (df['Status'] == "Anomalous")]
        if not next_anomalous.empty:
            st.session_state.selected_time = next_anomalous.iloc[0]['ForecastStart']
            st.rerun()
        else:
            st.warning("🚫 No more anomalous points found after this.")

# --- Select Slider ---
st.markdown("### ⏳ Select a Time Point")
selected_time = st.select_slider(
    "Use the slider to browse forecast times",
    options=forecast_times,
    value=st.session_state.selected_time,
    format_func=lambda x: x.strftime('%d %b %Y, %H:%M'),
    key="slider_time"
)
st.session_state.selected_time = selected_time  # Sync state

# --- Get Selected Row ---
selected_row = df[df['ForecastStart'] == st.session_state.selected_time]
if selected_row.empty:
    selected_row = df.iloc[[df['ForecastStart'].sub(selected_time).abs().argmin()]]
else:
    selected_row = selected_row.iloc[0]

status = selected_row['Status']
time_until_fault = selected_row['TimeUntilFault']
forecast_start = selected_row['ForecastStart']

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

# --- Format Forecast Time ---
def format_datetime_with_suffix(dt):
    day = dt.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return dt.strftime(f"%-d{suffix} %B %Y, %H:%M")

formatted_time = format_datetime_with_suffix(forecast_start)

st.markdown(f"""
<div style="text-align:center; font-size:26px; margin-top:20px;">
    🕒 <strong>Forecast Time:</strong> {formatted_time}
</div>
""", unsafe_allow_html=True)

# --- Display Status ---
st.markdown("### 📦 Current Status")
box_class = "status-box healthy" if status == "Healthy" else "status-box unhealthy blinking"
st.markdown(f"<div class='{box_class}'>{status}</div>", unsafe_allow_html=True)

# --- Display Time Until Fault ---
st.markdown("### ⏱️ Time Until Fault")

if status == "Healthy" or pd.isnull(time_until_fault):
    time_display = "NA"
else:
    # Convert TimeUntilFault to timedelta if needed
    if isinstance(time_until_fault, (float, int)):
        td = pd.to_timedelta(time_until_fault, unit='D')
    elif isinstance(time_until_fault, pd.Timedelta):
        td = time_until_fault
    elif isinstance(time_until_fault, str):
        try:
            td = pd.to_timedelta(time_until_fault)
        except:
            td = pd.to_timedelta("0 days 00:00:00")
    else:
        td = pd.to_timedelta("0 days 00:00:00")

    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    time_display = f"{hours} hours and {minutes} minutes"

st.markdown(f"<div class='time-box'>{time_display}</div>", unsafe_allow_html=True)