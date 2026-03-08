import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def render_market_overview(df):

    st.subheader("📈 Market Overview")

    spot = round(df["spot_close"].iloc[-1], 2)
    total_volume = int(df["total_volume"].sum())
    total_oi = int(df["total_oi"].sum())
    avg_pcr = round(df["PCR"].mean(), 2)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("NIFTY Spot", spot)
    col2.metric("Total Volume", f"{total_volume:,}")
    col3.metric("Total Open Interest", f"{total_oi:,}")
    col4.metric("Average PCR", avg_pcr)

    st.divider()

    # ----------------------------------------------------
    # PCR GAUGE
    # ----------------------------------------------------

    st.subheader("📊 PCR Sentiment Indicator")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_pcr,
        title={'text': "Put Call Ratio"},
        gauge={
            'axis': {'range': [0, 2]},
            'steps': [
                {'range': [0, 0.8], 'color': "#ff4b4b"},
                {'range': [0.8, 1.2], 'color': "#888"},
                {'range': [1.2, 2], 'color': "#2ecc71"}
            ]
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # OI DISTRIBUTION
    # ----------------------------------------------------

    st.subheader("📌 Open Interest Distribution")

    oi_df = df.groupby("strike")[["oi_CE", "oi_PE"]].sum().reset_index()

    fig = px.bar(
        oi_df,
        x="strike",
        y=["oi_CE", "oi_PE"],
        barmode="group"
    )

    fig.add_vline(x=spot, line_dash="dash", line_color="yellow")

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # VOLUME DISTRIBUTION
    # ----------------------------------------------------

    st.subheader("📊 Volume Distribution")

    vol_df = df.groupby("strike")[["volume_CE", "volume_PE"]].sum().reset_index()

    fig = px.bar(
        vol_df,
        x="strike",
        y=["volume_CE", "volume_PE"],
        barmode="group"
    )

    fig.add_vline(x=spot, line_dash="dash", line_color="yellow")

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # SUPPORT / RESISTANCE
    # ----------------------------------------------------

    st.subheader("📍 Key Market Levels")

    max_call = oi_df.loc[oi_df["oi_CE"].idxmax(), "strike"]
    max_put = oi_df.loc[oi_df["oi_PE"].idxmax(), "strike"]

    c1, c2 = st.columns(2)

    c1.success(f"📉 Resistance Level (Max Call OI): {max_call}")
    c2.success(f"📈 Support Level (Max Put OI): {max_put}")

    # ----------------------------------------------------
    # MARKET SIGNAL
    # ----------------------------------------------------

    st.subheader("🧠 AI Market Signal")

    signal = "Neutral"

    if avg_pcr > 1.2 and max_put > max_call:
        signal = "Bullish"

    elif avg_pcr < 0.8 and max_call > max_put:
        signal = "Bearish"

    st.info(f"📡 Market Signal: {signal}")