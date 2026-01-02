import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os
from PIL import Image

# Add project root to Python path for deployment
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dashboard.style import show_chart_with_card
from dashboard.utils import get_dataset_path

eur_jobs = pd.read_csv(get_dataset_path('european_jobs.csv'))
presentatio_dataset = pd.read_csv(get_dataset_path('overview_dataset.csv'))

EELISA_COUNTRIES = [
    "France",
    "Germany", 
    "Italy",
    "Spain",
    "Hungary",
    "Turkey",
    "Romania"
]

# ISO-2 to ISO-3 conversion mapping
ISO2_TO_ISO3 = {
    "be": "BEL",
    "bg": "BGR",
    "cz": "CZE",
    "dk": "DNK",
    "de": "DEU",
    "ee": "EST",
    "ie": "IRL",
    "el": "GRC",
    "gr": "GRC",
    "es": "ESP",
    "fr": "FRA",
    "hr": "HRV",
    "it": "ITA",
    "cy": "CYP",
    "lv": "LVA",
    "lt": "LTU",
    "lu": "LUX",
    "hu": "HUN",
    "mt": "MLT",
    "nl": "NLD",
    "at": "AUT",
    "pl": "POL",
    "pt": "PRT",
    "ro": "ROU",
    "si": "SVN",
    "sk": "SVK",
    "fi": "FIN",
    "se": "SWE",
    "no": "NOR",
    "ch": "CHE",
}

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

    This overview section describes the dataset's scope, structure, and key variables, and provides essential context for the 
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
        st.metric("Jobs with education requirement", f"{60.0}%")

    with col3:
        st.metric("Countries covered", eur_jobs["country"].nunique() if "country" in eur_jobs.columns else "N/A")

    with col4:
        st.metric("ISCO-3 occupations", eur_jobs["isco_3_digit_label"].nunique() if "isco_3_digit_label" in eur_jobs.columns else "N/A")

    # -----------------------
    # Jobs retrievals per country 
    # -----------------------    
    if not eur_jobs.empty and "country" in eur_jobs.columns:

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
            margin=dict(t=60, l=30, r=20, b=120)
        )

        show_chart_with_card(fig)

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

        TOP_N = 20
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
            height = 600,
            yaxis=dict(autorange="reversed"),  # largest on top
            margin=dict(t=60, l=40, r=20, b=90),
            font=dict(color="#1F2933")
        )

        fig_isco.update_traces(
            hovertemplate="<b>%{y}</b><br>" +
                        "Jobs: %{x:,}<br>" +
                        "<extra></extra>"
        )
        show_chart_with_card(fig_isco)

    # ----------------------------
    # ISCO × Country Chloropleth map 
    # ----------------------------
    col1, col2 = st.columns(2)
    with col1: 
        df = eur_jobs.copy()

        df = df[
            df["country_code"].notna() &
            df["isco_3_digit_label"].notna()
        ]

        # ISCO selector
        isco_options = (
            df["isco_3_digit_label"]
            .value_counts()
            .index
            .tolist()
        )

        selected_isco = st.selectbox(
            "Select an ISCO-3 occupation:",
            isco_options
        )

        df_isco = df[df["isco_3_digit_label"] == selected_isco]

        country_counts = (
            df_isco
            .groupby("country_code")
            .size()
            .reset_index(name="job_count")
        )

        # Convert ISO-2 to ISO-3 codes
        country_counts["country_code_iso3"] = country_counts["country_code"].str.lower().map(ISO2_TO_ISO3)
        
        # Filter out any unmapped codes
        country_counts = country_counts[country_counts["country_code_iso3"].notna()]

        fig = px.choropleth(
            country_counts,
            locations="country_code_iso3",  # Use ISO-3 codes
            color="job_count",
            locationmode="ISO-3",  # Changed from ISO-2 to ISO-3
            scope="europe",
            color_continuous_scale="Blues",
            labels={"job_count": "Number of job postings"},
            title=f"Geographic Distribution of {selected_isco}"
        )
        fig.update_layout(
            height=600,
            margin=dict(t=60, l=20, r=20, b=20),
            font=dict(color="#1F2933"),
            coloraxis_showscale=False,  
            paper_bgcolor="rgba(0,0,0,0)"
        )

        show_chart_with_card(fig)
    with col2: 
        pass