import streamlit as st
import plotly.express as px
from sklearn.ensemble import IsolationForest


def render_ai_anomaly(df):

    st.title("🤖 AI Unusual Options Activity Detector")

    temp = df.copy()

    # ----------------------------------------------------
    # FEATURE ENGINEERING
    # ----------------------------------------------------

    temp["total_volume"] = temp["volume_CE"] + temp["volume_PE"]
    temp["total_oi"] = temp["oi_CE"] + temp["oi_PE"]

    # ----------------------------------------------------
    # MODEL SETTINGS
    # ----------------------------------------------------

    st.sidebar.header("Model Settings")

    contamination = st.sidebar.slider(
        "Anomaly Sensitivity",
        0.01,
        0.10,
        0.02
    )

    # ----------------------------------------------------
    # ISOLATION FOREST MODEL
    # ----------------------------------------------------

    features = temp[["total_volume", "total_oi"]]

    model = IsolationForest(
        contamination=contamination,
        random_state=42
    )

    temp["anomaly"] = model.fit_predict(features)

    # ----------------------------------------------------
    # SUMMARY METRIC
    # ----------------------------------------------------

    total_anomalies = len(temp[temp["anomaly"] == -1])

    st.metric("⚠ Detected Anomalies", total_anomalies)

    # ----------------------------------------------------
    # MARKET INSIGHTS
    # ----------------------------------------------------

    st.subheader("📊 Market Insights")

    if total_anomalies > 5:
        st.error("Unusual trading activity detected")

    elif total_anomalies > 0:
        st.warning("Some unusual activity detected")

    else:
        st.success("No abnormal activity detected")

    # ----------------------------------------------------
    # SCATTER PLOT
    # ----------------------------------------------------

    fig = px.scatter(
        temp,
        x="strike",
        y="total_volume",
        size="total_oi",
        color="anomaly",
        title="AI Detected Unusual Options Activity",
        color_discrete_map={
            1: "#22c55e",
            -1: "#ef4444"
        },
        hover_data=["datetime", "total_volume", "total_oi"]
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Strike Price",
        yaxis_title="Total Volume"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # ANOMALY TABLE
    # ----------------------------------------------------

    st.subheader("🚨 Unusual Activity Detected")

    anomalies = temp[temp["anomaly"] == -1][
        ["datetime", "strike", "total_volume", "total_oi"]
    ]

    st.dataframe(anomalies, use_container_width=True)