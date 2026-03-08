import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Volatility Smile",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Volatility Smile")

# DATA PATH
DATA_PATH = Path("backend/data")

files = list(DATA_PATH.glob("*.csv"))

if not files:
    st.warning("No CSV files found in backend/data folder")
    st.stop()

df = pd.concat([pd.read_csv(file) for file in files])

df.columns = df.columns.str.strip().str.lower()

# Calculate IV proxy
iv = df.groupby("strike")["ce"].mean().reset_index()

fig = px.line(
    iv,
    x="strike",
    y="ce",
    markers=True,
    template="plotly_dark",
    title="Volatility Smile (Using CE Price)"
)

st.plotly_chart(fig, use_container_width=True)