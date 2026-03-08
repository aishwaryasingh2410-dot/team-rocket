import streamlit as st
import pandas as pd
import glob
import plotly.express as px
from sklearn.cluster import KMeans

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Market Activity Clustering",
    layout="wide",
    page_icon="🧠"
)

# --------------------------------------------------
# STYLING
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
}

[data-testid="stSidebar"] {
    background-color: #161B22;
}

h1,h2,h3,h4 {
    color: white;
}

.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🧠 Market Activity Clustering")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():

    files = glob.glob("data/*.csv")

    if not files:
        return pd.DataFrame()

    df = pd.concat([pd.read_csv(file) for file in files])

    # Clean columns
    df.columns = df.columns.str.strip().str.lower()

    return df


df = load_data()

if df.empty:
    st.warning("⚠️ No CSV files found in /data folder")
    st.stop()

# --------------------------------------------------
# REQUIRED COLUMN CHECK
# --------------------------------------------------

required_cols = ["volume_ce","volume_pe","oi_ce","oi_pe","strike"]

missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

# --------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------

df["total_volume"] = df["volume_ce"] + df["volume_pe"]
df["total_oi"] = df["oi_ce"] + df["oi_pe"]

# --------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------

with st.sidebar:

    st.header("⚙️ Cluster Settings")

    n_clusters = st.slider(
        "Number of Clusters",
        min_value=2,
        max_value=6,
        value=3
    )

# --------------------------------------------------
# CLUSTERING
# --------------------------------------------------

features = df[["total_volume","total_oi"]]

if len(df) < n_clusters:
    st.error("Dataset too small for clustering")
    st.stop()

model = KMeans(
    n_clusters=n_clusters,
    random_state=42,
    n_init=10
)

df["cluster"] = model.fit_predict(features)

df["cluster"] = df["cluster"].astype(str)

# --------------------------------------------------
# VISUALIZATION
# --------------------------------------------------

st.subheader("📊 Market Activity Clusters")

fig = px.scatter(
    df,
    x="strike",
    y="total_volume",
    color="cluster",
    size="total_oi",
    template="plotly_dark",
    title="Options Market Activity Clusters"
)

fig.update_layout(
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(color="white")
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# CLUSTER SUMMARY
# --------------------------------------------------

st.subheader("📊 Cluster Summary")

summary = df.groupby("cluster")[["total_volume","total_oi"]].mean().round(0)

st.dataframe(summary, use_container_width=True)

# --------------------------------------------------
# EXPLANATION
# --------------------------------------------------

st.info("""
### Cluster Meaning

Cluster 0 → Low market activity  
Cluster 1 → Medium activity  
Cluster 2 → High activity / Institutional trading  

Higher **Total Volume + OI** usually signals **smart money participation**.
""")