import streamlit as st
import pandas as pd
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

# Datasets
eur_jobs_path = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/datasets/european_jobs.csv'
eur_jobs = pd.read_csv(eur_jobs_path)

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
if page == "Overview":
    show_overview_page()

# ---- Education & Languages ----
elif page == "Education & Languages":
    show_education_language_page(eur_jobs)

# ---- Skills ----
elif page == "Skills":
    show_skills_page(eur_jobs)

# ---- GreenComp ----
elif page == "GreenComp":
    show_greencomp_page(eur_jobs)

# ---- DigComp ----
elif page == "DigComp":
    show_digcomp_page(eur_jobs)

# ---- Profiles ----
elif page == "Profiles":
    show_profiles_page(eur_jobs)
