import streamlit as st
import pandas as pd
from dashboard.utils import get_dataset_path
from dashboard.views.overview import show_overview_page
from dashboard.views.edu_lang import show_education_language_page
from dashboard.views.skills import show_skills_page
from dashboard.views.digcomp import show_digcomp_page
from dashboard.views.greencomp import show_greencomp_page
from dashboard.views.profiles import show_profiles_page
from dashboard.views.home import show_home_page

# Configs
st.set_page_config(
    page_title="European Job Market Dashboard",
    layout="wide"
)

# Simple, clean CSS that just works
st.markdown("""
<style>
/* Set page background */
.main .block-container {
    background-color: #f8f9fa;
}

/* Simple card styling for charts only */
div[data-testid="stPlotlyChart"] {
    background-color: white !important;
    padding: 1.25rem !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    margin-bottom: 1.5rem !important;
    border: 1px solid #e5e7eb !important;
}
</style>
""", unsafe_allow_html=True)

# Datasets with relative paths
eur_jobs = pd.read_csv(get_dataset_path('european_jobs.csv'))
content = pd.read_csv(get_dataset_path('extractions.csv'))

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    " ",
    [
        "Home",
        "Overview",
        "Education & Languages",
        "Skills",
        "GreenComp",
        "DigComp",
        "Profiles"
    ]
)

# ---- Homepage ----
if page == "Home":
    show_home_page()

# ---- Overview ----
elif page == "Overview":
    show_overview_page()

# ---- Education & Languages ----
elif page == "Education & Languages":
    show_education_language_page(content)

# ---- Skills ----
elif page == "Skills":
    show_skills_page()

# ---- GreenComp ----
elif page == "GreenComp":
    show_greencomp_page(eur_jobs)

# ---- DigComp ----
elif page == "DigComp":
    show_digcomp_page(eur_jobs)

# ---- Profiles ----
elif page == "Profiles":
    show_profiles_page(eur_jobs)
