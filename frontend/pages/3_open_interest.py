import streamlit as st
import plotly.express as px


def render_open_interest(df):

    st.title("📊 Open Interest Analysis")

    # ----------------------------------------------------
    # GROUP OI
    # ----------------------------------------------------

    oi_group = df.groupby("strike")[["oi_CE", "oi_PE"]].sum().reset_index()

    # ----------------------------------------------------
    # OI DISTRIBUTION
    # ----------------------------------------------------

    st.subheader("📊 Call vs Put Open Interest")

    fig = px.bar(
        oi_group,
        x="strike",
        y=["oi_CE", "oi_PE"],
        barmode="group",
        title="Call vs Put Open Interest by Strike"
    )

    fig.update_layout(
        template="plotly_dark",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # MARKET BIAS
    # ----------------------------------------------------

    st.subheader("📈 Market Bias (OI Difference)")

    oi_group["oi_diff"] = oi_group["oi_PE"] - oi_group["oi_CE"]

    fig2 = px.bar(
        oi_group,
        x="strike",
        y="oi_diff",
        title="Put - Call Open Interest"
    )

    fig2.update_layout(template="plotly_dark")

    st.plotly_chart(fig2, use_container_width=True)

    # ----------------------------------------------------
    # SUPPORT / RESISTANCE
    # ----------------------------------------------------

    st.subheader("📍 Key OI Levels")

    max_call = oi_group.loc[oi_group["oi_CE"].idxmax(), "strike"]
    max_put = oi_group.loc[oi_group["oi_PE"].idxmax(), "strike"]

    col1, col2 = st.columns(2)

    col1.metric("Strong Call OI (Resistance)", max_call)
    col2.metric("Strong Put OI (Support)", max_put)

    # ----------------------------------------------------
    # OI HEATMAP
    # ----------------------------------------------------

    st.subheader("🔥 Open Interest Heatmap")

    heatmap_df = df.pivot_table(
        values="oi_CE",
        index="strike",
        columns="datetime",
        aggfunc="sum"
    )

    fig3 = px.imshow(
        heatmap_df,
        aspect="auto",
        title="Call Open Interest Heatmap"
    )

    fig3.update_layout(template="plotly_dark")

    st.plotly_chart(fig3, use_container_width=True)

    # ----------------------------------------------------
    # DATA PREVIEW
    # ----------------------------------------------------

    st.subheader("📋 Data Preview")

    st.dataframe(df.head(50), use_container_width=True)