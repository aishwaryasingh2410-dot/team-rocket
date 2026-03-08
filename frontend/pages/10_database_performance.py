import streamlit as st
from backend.db.performance_test import run_test

st.title("Database Optimization Monitor")

if st.button("Run Cursor Test"):

    normal, optimized = run_test()

    st.metric("Normal Cursor Time", normal)
    st.metric("Optimized Cursor Time", optimized)

    improvement = ((normal - optimized) / normal) * 100

    st.success(f"Performance improved by {improvement:.2f}%")