import streamlit as st
import plotly.express as px


def render_volume_heatmap(df):

    st.title("🔥 Options Volume Heatmap")

    # Ensure total_volume exists
    temp = df.copy()
    temp["total_volume"] = temp["volume_CE"] + temp["volume_PE"]

    # ----------------------------------------------------
    # STRIKE vs EXPIRY HEATMAP
    # ----------------------------------------------------

    st.subheader("📊 Volume Heatmap (Strike vs Expiry)")

    pivot = temp.pivot_table(
        values="total_volume",
        index="strike",
        columns="expiry",
        aggfunc="sum"
    )

    fig = px.imshow(
        pivot,
        color_continuous_scale="Turbo",
        aspect="auto"
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Expiry",
        yaxis_title="Strike Price",
        coloraxis_colorbar=dict(title="Volume")
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # TIME vs STRIKE HEATMAP
    # ----------------------------------------------------

    st.subheader("⏱ Volume Heatmap (Strike vs Time)")

    time_pivot = temp.pivot_table(
        values="total_volume",
        index="strike",
        columns="datetime",
        aggfunc="sum"
    )

    fig2 = px.imshow(
        time_pivot,
        color_continuous_scale="Turbo",
        aspect="auto"
    )

    fig2.update_layout(
        template="plotly_dark",
        xaxis_title="Time",
        yaxis_title="Strike"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # ----------------------------------------------------
    # CE vs PE VOLUME
    # ----------------------------------------------------

    st.subheader("📊 Call vs Put Volume")

    volume_group = temp.groupby("strike")[["volume_CE", "volume_PE"]].sum().reset_index()

    fig3 = px.bar(
        volume_group,
        x="strike",
        y=["volume_CE", "volume_PE"],
        barmode="group",
        title="Call vs Put Volume by Strike"
    )

    fig3.update_layout(template="plotly_dark")

    st.plotly_chart(fig3, use_container_width=True)

    # ----------------------------------------------------
    # VOLUME SPIKE DETECTION
    # ----------------------------------------------------

    st.subheader("🚨 Volume Spike Detection")

    threshold = temp["total_volume"].quantile(0.98)

    spikes = temp[temp["total_volume"] > threshold]

    if not spikes.empty:
        st.dataframe(spikes.head(20), use_container_width=True)
    else:
        st.success("No significant volume spikes detected")

    # ----------------------------------------------------
    # DATA PREVIEW
    # ----------------------------------------------------

    st.subheader("📋 Data Preview")

    st.dataframe(temp.head(50), use_container_width=True)