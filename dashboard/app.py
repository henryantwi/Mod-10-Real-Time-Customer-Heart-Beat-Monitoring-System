"""
Streamlit Dashboard — Real-Time Heartbeat Monitoring (Optional Extension).

Provides a simple web UI to visualize heartbeat data stored in PostgreSQL.

Run with:  streamlit run app.py
"""

import sys
import os

# Add src/ to path for config & db imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import streamlit as st
from db import query_latest_readings, query_anomalies, get_customer_stats


st.set_page_config(page_title="Heartbeat Monitor", page_icon="❤️", layout="wide")

st.title("❤️ Real-Time Customer Heartbeat Monitor")
st.caption("Powered by Kafka + PostgreSQL")

# ── Sidebar controls ──────────────────────────────────────────
st.sidebar.header("Settings")
refresh = st.sidebar.button("🔄 Refresh Data")
limit = st.sidebar.slider("Rows to display", 10, 100, 20)

# ── Customer Stats ─────────────────────────────────────────────
st.header("📊 Customer Statistics")

try:
    stats = get_customer_stats()
    if stats:
        st.table(
            [
                {
                    "Customer": row[0],
                    "Total Readings": row[1],
                    "Avg HR": row[2],
                    "Min HR": row[3],
                    "Max HR": row[4],
                    "Anomalies": row[5],
                }
                for row in stats
            ]
        )
    else:
        st.info("No data yet. Start the producer and consumer first.")
except Exception as e:
    st.error(f"Could not connect to database: {e}")
    st.stop()

# ── Latest Readings ────────────────────────────────────────────
st.header("🕐 Latest Readings")

readings = query_latest_readings(limit)
if readings:
    st.table(
        [
            {
                "Customer": row[0],
                "Heart Rate": row[1],
                "Recorded At": row[2],
                "Anomaly": "⚠️ Yes" if row[3] else "No",
            }
            for row in readings
        ]
    )
else:
    st.info("No readings found.")

# ── Anomalies ──────────────────────────────────────────────────
st.header("⚠️ Recent Anomalies")

anomalies = query_anomalies(limit)
if anomalies:
    st.table(
        [
            {
                "Customer": row[0],
                "Heart Rate": row[1],
                "Recorded At": row[2],
            }
            for row in anomalies
        ]
    )
else:
    st.success("No anomalies detected.")
