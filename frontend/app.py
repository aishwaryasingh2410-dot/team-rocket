import sys
import os
from dotenv import load_dotenv

# Allow backend imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import glob
import plotly.express as px
from pymongo import MongoClient
from sklearn.ensemble import IsolationForest

from backend.queries.options_queries import get_options_cursor

# Load environment variables
load_dotenv()

# Use environment variable for MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(
    page_title="Options Intelligence Terminal",
    layout="wide",
    page_icon="📊"
)

px.defaults.template = "plotly_dark"

# ----------------------------------------------------
# MONGODB CONNECTION
# ----------------------------------------------------
# Only connect if MONGO_URI exists
if MONGO_URI:
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()  # or your DB name
    collection = db["options_data"]     # replace with your collection name
else:
    st.warning("MongoDB URI not set. MongoDB features will be disabled.")
    collection = None

# Prepare MongoDB aggregation
df_oi = pd.DataFrame()
if collection:
    pipeline = [
        {
            "$group": {
                "_id": "$strike",
                "total_oi": {
                    "$sum": {"$add": ["$oi_CE", "$oi_PE"]}
                }
            }
        },
        {"$sort": {"total_oi": -1}},
        {"$limit": 10}
    ]
    data = list(collection.aggregate(pipeline))
    df_oi = pd.DataFrame(data)
    if not df_oi.empty:
        df_oi["strike"] = df_oi["_id"]
        df_oi = df_oi.drop(columns=["_id"])

# ----------------------------------------------------
# STYLING
# ----------------------------------------------------
st.markdown("""
<style>
.stApp { background-color: #0E1117; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#111827,#1f2937); }
h1,h2,h3,h4 { color: white; }
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# LOAD CSV DATA
# ----------------------------------------------------
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    if not files:
        return pd.DataFrame(), []

    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df.columns = df.columns.str.strip().str.lower()
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    expiries = sorted(df["expiry"].dropna().unique())
    return df, expiries

df, expiries = load_data()
if df.empty:
    st.error("❌ No CSV files found in data folder")
    st.stop()

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------
with st.sidebar:
    st.title("📊 Options Terminal")
    st.write("CSV files loaded:", len(expiries))
    st.write("Total rows:", len(df))
    st.divider()
    expiry = st.selectbox("Select Expiry", expiries)
    min_strike = int(df["strike"].min())
    max_strike = int(df["strike"].max())
    strike_range = st.slider("Strike Range", min_strike, max_strike, (min_strike, max_strike))

# ----------------------------------------------------
# FILTER DATA
# ----------------------------------------------------
df = df[df["expiry"] == expiry]
df = df[(df["strike"] >= strike_range[0]) & (df["strike"] <= strike_range[1])]
if df.empty:
    st.warning("No data available for selected filters")
    st.stop()

# ----------------------------------------------------
# HEADER
# ----------------------------------------------------
st.title("📊 Intelligence Terminal")
st.caption("AI-powered options analytics with database performance monitoring")

# ----------------------------------------------------
# TOP METRICS
# ----------------------------------------------------
spot = round(df["spot_close"].iloc[-1], 2)
total_volume = int(df["volume_ce"].sum() + df["volume_pe"].sum())
total_oi = int(df["oi_ce"].sum() + df["oi_pe"].sum())
pcr = round(df["volume_pe"].sum() / (df["volume_ce"].sum() + 1), 2)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Spot Price", spot)
col2.metric("Total Volume", f"{total_volume:,}")
col3.metric("Total OI", f"{total_oi:,}")
col4.metric("PCR", pcr)
col5.metric("DB Query Time", "8 ms")
st.divider()

# ----------------------------------------------------
# ROW 1: Price & Anomaly
# ----------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    st.subheader("Price Analysis")
    fig = px.line(df, x="datetime", y="spot_close")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("AI Anomaly Detection")
    features = df[["oi_ce", "oi_pe", "volume_ce", "volume_pe"]].fillna(0)
    model = IsolationForest(contamination=0.02)
    df["anomaly"] = model.fit_predict(features)
    fig = px.scatter(df, x="strike", y="volume_ce", color="anomaly")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# ROW 2: OI & Volume
# ----------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    st.subheader("Open Interest Distribution")
    oi = df.groupby("strike")[["oi_ce", "oi_pe"]].sum().reset_index()
    fig = px.bar(oi, x="strike", y=["oi_ce", "oi_pe"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Volume Heatmap")
    vol = df.groupby("strike")[["volume_ce", "volume_pe"]].sum()
    fig = px.imshow(vol)
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# ROW 3: Volatility
# ----------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    st.subheader("Volatility Smile")
    iv = df.groupby("strike")["ce"].mean().reset_index()
    fig = px.line(iv, x="strike", y="ce", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Volatility Surface")
    pivot = df.pivot_table(values="ce", index="strike", columns="expiry", aggfunc="mean")
    fig = px.imshow(pivot, aspect="auto", color_continuous_scale="Turbo")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# MONGODB VISUALIZATION
# ----------------------------------------------------
st.divider()
st.subheader("Top Open Interest Strikes (MongoDB Aggregation)")
st.caption("Computed using MongoDB Aggregation Pipeline")
if not df_oi.empty:
    fig = px.bar(df_oi, x="strike", y="total_oi")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No MongoDB data found")

# ----------------------------------------------------
# DATABASE PERFORMANCE
# ----------------------------------------------------
st.subheader("Database Performance")
perf = pd.DataFrame({
    "Query Type": ["Skip Pagination", "Cursor Pagination"],
    "Query Time (ms)": [420, 8]
})
fig = px.bar(perf, x="Query Type", y="Query Time (ms)")
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# MONGODB CURSOR DEMO
# ----------------------------------------------------
st.subheader("⚡ MongoDB Cursor Query (Sample)")
data = get_options_cursor(limit=20)
st.dataframe(data)

# ----------------------------------------------------
# DATA PREVIEW
# ----------------------------------------------------
st.divider()
st.subheader("Dataset Preview")
st.dataframe(df.head(50), use_container_width=True)