import streamlit as st
import plotly.express as px
import pandas as pd
from PIL import Image


def show_overview_page(df):
    """Display the Job Offers Dataset page"""

    st.header("European Job Offers Dataset")
    
    st.markdown("---")

    st.markdown("""
    The dataset **job offers.csv** provides a harmonised collection of job postings used to analyse labour market characteristics 
    across Europe. It aggregates vacancy data collected from multiple online recruitment platforms and has been processed to enable 
    systematic comparison across countries, occupations, and skill categories.

    Each record corresponds to a single job posting and includes structured metadata such as job title, country, region, and 
    occupational classification based on the **ISCO** framework, alongside the full unstructured job description. The dataset 
    combines both structured and textual information, allowing for quantitative analysis as well as semantic exploration of job 
    requirements.

    Prior to analysis, the data underwent a normalisation and cleaning process to reduce duplication, harmonise occupational 
    labels, and standardise country-level information. Particular attention was given to ensuring consistency in occupational 
    coding and to preserving the original content of job descriptions to support robust text-based analysis.

    As the data originates from web-scraped job advertisements, it is subject to well-known limitations of online labour market data. 
    These include potential sampling bias, uneven coverage across countries and sectors, and variability in how employers describe 
    job requirements. The dataset should therefore be interpreted as a proxy for labour market demand rather than as a 
    comprehensive representation of employment structures.

    This overview section describes the dataset’s scope, structure, and key variables, and provides essential context for the 
    subsequent analytical sections of the dashboard.
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
