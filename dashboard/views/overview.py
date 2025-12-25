import streamlit as st
import plotly.express as px
import pandas as pd
from PIL import Image


def show_overview_page(df):
    """Display the Job Offers Dataset page"""

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
    The dataset **job offers.csv** was delivered to EELISA on **10.12.2025** for research purposes as part of a broader initiative to 
    analyse labour market trends, digital and green competencies, and emerging skill requirements across Europe. 
    
    It compiles job postings collected from multiple online recruitment platforms and harmonised to support cross-country comparison. 
    This document provides an overview of the dataset's structure, the methodology used to collect and normalise the 
    information, and the key variables included. 
    
    It also outlines the limitations inherent to web-scraped labour data, the assumptions applied during preprocessing, and 
    recommendations for safe and rigorous use of the dataset in research and policy analysis.
    
    **The objective** of this note is to ensure transparency, reproducibility, and a clear understanding of the dataset's scope so that 
    it can be reliably used by researchers, academic partners, and stakeholders involved in the **EELISA Data Science Mission**.
    """)

    st.markdown("---")

    # =======================
    # DATASET OVERVIEW
    # =======================
    st.header("Dataset Overview")
    st.dataframe(df, use_container_width=True)

    # =======================
    # KEY STATISTICS
    # =======================
    st.subheader("Key Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Jobs", len(df))

    with col2:
        st.metric("Total Columns", len(df.columns))

    with col3:
        st.metric("Countries", df["country"].nunique() if "country" in df.columns else "N/A")

    with col4:
        st.metric("Fields", df["field"].nunique() if "field" in df.columns else "N/A")

    # =======================
    # DATA VISUALIZATIONS
    # =======================
    if not df.empty:

        # -----------------------
        # JOBS BY COUNTRY (EELISA HIGHLIGHT)
        # -----------------------
        if "country" in df.columns:

            EELISA_COUNTRIES = [
                "France",
                "Germany", 
                "Italy",
                "Spain",
                "Hungary",
                "Turkey",
                "Romania"
            ]

            # Get country counts without sorting by value
            country_counts = df["country"].value_counts()
            
            # Create DataFrame while preserving original order
            country_df = pd.DataFrame({
                "country_name": country_counts.index,
                "job_count": country_counts.values
            })

            country_df["color"] = country_df["country_name"].apply(
                lambda x: "#648fa9" if x in EELISA_COUNTRIES else "#d3d3d3"
            )

            fig = px.bar(
                country_df,
                x="country_name",
                y="job_count",
                title="Job Distribution by Country (EELISA Countries Highlighted)",
                color="color",
                color_discrete_map="identity",
                labels={
                    "country_name": "Country",
                    "job_count": "Number of Job Postings"
                }
            )

            # You can also add hover data
            fig.update_traces(
                hovertemplate="<b>%{x}</b><br>" +
                              "Jobs: %{y:,}<br>" +
                              "<extra></extra>"
            )

            fig.update_layout(
                xaxis_tickangle=-45,
                showlegend=False,
                template="plotly_white",
                paper_bgcolor="white",
                font=dict(color="black"),
                margin=dict(t=60, l=20, r=20, b=80)
            )

            st.plotly_chart(fig, use_container_width=True, theme=None)
