import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def render_price_analysis(df):

    st.title("📈 NIFTY Price Analysis")

    # ----------------------------------------------------
    # SPOT PRICE TIMESERIES
    # ----------------------------------------------------

    st.subheader("📊 Spot Price Movement")

    fig = px.line(
        df,
        x="datetime",
        y="spot_close",
        title="NIFTY Spot Price Over Time",
        markers=True
    )

    fig.update_layout(
        template="plotly_dark",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # ATM STRIKE ANALYSIS
    # ----------------------------------------------------

    st.subheader("📍 ATM Option Price Movement")

    temp = df.copy()
    temp["distance_from_spot"] = abs(temp["strike"] - temp["spot_close"])

    atm_df = temp.loc[temp.groupby("datetime")["distance_from_spot"].idxmin()]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=atm_df["datetime"],
            y=atm_df["CE"],
            name="ATM Call Price",
            mode="lines"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=atm_df["datetime"],
            y=atm_df["PE"],
            name="ATM Put Price",
            mode="lines"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        title="ATM Option Prices Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # CE vs PE PRICE BY STRIKE
    # ----------------------------------------------------

    st.subheader("📊 Option Prices by Strike")

    strike_df = df.groupby("strike")[["CE", "PE"]].mean().reset_index()

    fig = px.line(
        strike_df,
        x="strike",
        y=["CE", "PE"],
        title="Average Option Prices by Strike"
    )

    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # PRICE DISTRIBUTION
    # ----------------------------------------------------

    st.subheader("📊 Spot Price Distribution")

    fig2 = px.histogram(
        df,
        x="spot_close",
        nbins=40,
        title="Spot Price Distribution"
    )

    fig2.update_layout(template="plotly_dark")

    st.plotly_chart(fig2, use_container_width=True)

    # ----------------------------------------------------
    # VOLATILITY PROXY
    # ----------------------------------------------------

    st.subheader("📉 Price Volatility Proxy")

    temp["returns"] = temp["spot_close"].pct_change()

    volatility = temp["returns"].rolling(20).std() * (252 ** 0.5)

    fig3 = px.line(
        x=temp["datetime"],
        y=volatility,
        labels={"x": "Datetime", "y": "Volatility"},
        title="Rolling Volatility (20 Period)"
    )

    fig3.update_layout(template="plotly_dark")

    st.plotly_chart(fig3, use_container_width=True)

    # ----------------------------------------------------
    # DATA PREVIEW
    # ----------------------------------------------------

    st.subheader("📋 Data Preview")

    st.dataframe(df.head(50), use_container_width=True)