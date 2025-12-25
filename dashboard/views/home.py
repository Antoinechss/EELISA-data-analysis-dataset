import streamlit as st
import plotly.express as px
import pandas as pd
from PIL import Image

def show_home_page():

    # =======================
    # HEADER WITH LOGOS
    # =======================
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        try:
            eelisa_logo = Image.open(
                "/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/dashboard/static/eelisa_logo.png"
            )
            st.image(eelisa_logo, width=150)
        except:
            st.write("EELISA Logo")

    with col2:
        st.title("Job Offers Dataset")

    with col3:
        try:
            pep_logo = Image.open(
                "/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/dashboard/static/PEP_logo.png"
            )
            st.image(pep_logo, width=150)
        except:
            st.write("PEP Logo")

    # =======================
    # INTRODUCTION
    # =======================
    st.markdown("---")
    st.header("About this Dataset")

    st.markdown("""
    The dataset **job offers.csv** was delivered to **EELISA** on **10.12.2025** for research purposes within the framework of the 
    **EELISA Data Science Mission**, which aims to mobilise data-driven methods to analyse major societal and economic transformations 
    in Europe, including digitalisation, sustainability, and skills development.

    The dataset compiles job postings collected from multiple online recruitment platforms and harmonised to enable cross-country 
    comparisons of labour market dynamics. It supports the analysis of education requirements, skill demand, and alignment with 
    European digital and sustainability competence frameworks.

    This dashboard provides an overview of the dataset’s structure, the methodological choices applied during data collection and 
    preprocessing, and the key variables available for analysis. It also highlights the limitations inherent to web-scraped labour 
    market data, the assumptions made during normalisation, and recommendations for safe and rigorous use in research and policy-oriented 
    studies.

    **The objective** of this work is to ensure transparency, reproducibility, and a clear understanding of the dataset’s scope, 
    so that it can be reliably used by researchers, academic partners, and stakeholders involved in the **EELISA Data Science Mission**.
    """)
