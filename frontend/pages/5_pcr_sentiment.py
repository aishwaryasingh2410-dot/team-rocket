import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def render_pcr_sentiment(df):

    st.title("📉 PCR Sentiment Dashboard")

    temp = df.copy()

    # ----------------------------------------------------
    # PCR CALCULATION
    # ----------------------------------------------------

    temp["PCR_volume"] = temp["volume_PE"] / (temp["volume_CE"] + 1)
    temp["PCR_OI"] = temp["oi_PE"] / (temp["oi_CE"] + 1)

    pcr = temp.groupby("datetime")[["PCR_volume", "PCR_OI"]].mean().reset_index()

    latest_pcr = pcr["PCR_volume"].iloc[-1]

    # ----------------------------------------------------
    # KPI METRICS
    # ----------------------------------------------------

    col1, col2 = st.columns(2)

    col1.metric("📊 Latest PCR (Volume)", round(latest_pcr, 2))

    if latest_pcr > 1:
        sentiment = "Bearish 🔴"
    else:
        sentiment = "Bullish 🟢"

    col2.metric("Market Sentiment", sentiment)

    # ----------------------------------------------------
    # PCR TREND
    # ----------------------------------------------------

    st.subheader("📊 PCR Trend")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=pcr["datetime"],
            y=pcr["PCR_volume"],
            name="Volume PCR"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=pcr["datetime"],
            y=pcr["PCR_OI"],
            name="OI PCR"
        )
    )

    # Sentiment zones
    fig.add_hline(y=0.8, line_dash="dot", line_color="green")
    fig.add_hline(y=1.0, line_dash="dash", line_color="yellow")
    fig.add_hline(y=1.2, line_dash="dot", line_color="red")

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Time",
        yaxis_title="PCR",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # PCR DISTRIBUTION
    # ----------------------------------------------------

    st.subheader("📊 PCR Distribution")

    fig2 = px.histogram(
        pcr,
        x="PCR_volume",
        nbins=40,
        title="Distribution of Volume PCR"
    )

    fig2.update_layout(template="plotly_dark")

    st.plotly_chart(fig2, use_container_width=True)

    # ----------------------------------------------------
    # MARKET INSIGHTS
    # ----------------------------------------------------

    st.subheader("🧠 Market Insights")

    if latest_pcr > 1.2:
        st.warning("High PCR → Strong Put Activity → Potential Bearish Sentiment")

    elif latest_pcr < 0.8:
        st.success("Low PCR → Strong Call Activity → Potential Bullish Sentiment")

    else:
        st.info("PCR indicates neutral sentiment")

    # ----------------------------------------------------
    # DATA PREVIEW
    # ----------------------------------------------------

    st.subheader("📋 Data Preview")

    st.dataframe(temp.head(50), use_container_width=True)