import streamlit as st
import plotly.express as px
import pandas as pd
from PIL import Image

eur_jobs_path = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/datasets/european_jobs.csv'
eur_jobs = pd.read_csv(eur_jobs_path)
presentatio_dataset_path = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/datasets/overview_dataset.csv'
presentatio_dataset = pd.read_csv(presentatio_dataset_path)

def show_overview_page():
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
    comprehensive representat ion of employment structures.

    This overview section describes the dataset’s scope, structure, and key variables, and provides essential context for the 
    subsequent analytical sections of the dashboard.
    """)

    st.markdown("---")

    # =======================
    # DATASET OVERVIEW
    # =======================
    st.header("Dataset Overview")
    st.dataframe(presentatio_dataset, use_container_width=True)

    # =======================
    # KEY STATISTICS
    # =======================
    st.subheader("Key Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total job postings", f"{len(eur_jobs):,}")

    with col2:
        pct_edu = (eur_jobs["education_level"].notna().mean() * 100) if "education_level" in eur_jobs.columns else 0
        st.metric("Jobs with education requirement", f"{pct_edu:.1f}%")

    with col3:
        st.metric("Countries covered", eur_jobs["country"].nunique() if "country" in eur_jobs.columns else "N/A")

    with col4:
        st.metric("ISCO-3 occupations", eur_jobs["isco_3_digit_label"].nunique() if "isco_3_digit_label" in eur_jobs.columns else "N/A")

    # =======================
    # DATA VISUALIZATIONS
    # =======================
    if not eur_jobs.empty and "country" in eur_jobs.columns:

        EELISA_COUNTRIES = [
            "France",
            "Germany", 
            "Italy",
            "Spain",
            "Hungary",
            "Turkey",
            "Romania"
        ]

        # Aggregate job counts
        country_counts = eur_jobs["country"].value_counts()

        country_df = pd.DataFrame({
            "country_name": country_counts.index,
            "job_count": country_counts.values
        })

        # Color mapping (aligned with dashboard style)
        country_df["color"] = country_df["country_name"].apply(
            lambda x: "#3B6C8E" if x in EELISA_COUNTRIES else "#D1D5DB"
        )

        fig = px.bar(
            country_df,
            x="country_name",
            y="job_count",
            color="color",
            color_discrete_map="identity",
            title="Job Postings by Country (EELISA Countries Highlighted)",
            labels={
                "country_name": "Country",
                "job_count": "Number of job postings"
            },
            template="plotly_white"
        )

        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>" +
                        "Job postings: %{y:,}<br>" +
                        "<extra></extra>"
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            font=dict(color="#1F2933"),
            margin=dict(t=60, l=30, r=20, b=80)
        )

        st.plotly_chart(fig, use_container_width=True, theme=None)

    # -----------------------
    # JOBS BY ISCO-3 FIELD
    # -----------------------
    if "isco_3_digit_label" in eur_jobs.columns:

        isco_counts = (
            eur_jobs["isco_3_digit_label"]
            .value_counts()
            .reset_index()
        )

        isco_counts.columns = ["isco_3_label", "job_count"]

        # Optional: keep only top 15 for readability
        TOP_N = 15
        isco_counts = isco_counts.head(TOP_N)

        fig_isco = px.bar(
            isco_counts,
            x="job_count",
            y="isco_3_label",
            orientation="h",
            title="Job Postings by ISCO-3 Occupational Group",
            labels={
                "job_count": "Number of Job Postings in the dataset",
                "isco_3_label": "ISCO-3 Occupational Group"
            },
            color_discrete_sequence=["#3B6C8E"],  # consistent neutral / digital blue
            template="plotly_white"
        )

        fig_isco.update_layout(
            yaxis=dict(autorange="reversed"),  # largest on top
            margin=dict(t=60, l=40, r=20, b=40),
            font=dict(color="#1F2933")
        )

        fig_isco.update_traces(
            hovertemplate="<b>%{y}</b><br>" +
                        "Jobs: %{x:,}<br>" +
                        "<extra></extra>"
        )

        st.plotly_chart(fig_isco, use_container_width=True, theme=None)

