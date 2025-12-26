import streamlit as st
import pandas as pd

def show_education_language_page(df):
    st.title("Education & Language Requirements on the European Job Market")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Education Requirements")
    with col2:
        st.subheader("Language Requirements")

