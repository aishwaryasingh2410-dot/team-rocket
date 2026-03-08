import streamlit as st
import plotly.express as px


def render_volatility_surface(df):

    st.title("🌐 Volatility Surface")

    temp = df.copy()

    # Clean columns
    temp.columns = temp.columns.str.strip().str.lower()

    # Create pivot table
    pivot = temp.pivot_table(
        values="ce",
        index="strike",
        columns="expiry",
        aggfunc="mean"
    )

    # Heatmap
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Turbo",
        template="plotly_dark",
        title="Volatility Surface (Strike vs Expiry)"
    )

    fig.update_layout(
        xaxis_title="Expiry",
        yaxis_title="Strike Price"
    )

    st.plotly_chart(fig, use_container_width=True)