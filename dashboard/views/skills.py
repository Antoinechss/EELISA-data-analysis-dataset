import streamlit as st

def show_skills_page(df): 
    st.title("European Job Market Skills Framework")
    col1, col2 = st.columns(2)
    with col1: 
        st.subheader("Soft vs Hard skills distirbution")
    with col2: 
        pass