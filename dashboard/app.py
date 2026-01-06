import streamlit as st
import pandas as pd
import sys
import os

# Add project root to Python path for deployment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dashboard.utils import get_dataset_path
from dashboard.style import apply_global_style
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

# Apply centralized styling
apply_global_style()

# Datasets with relative paths
eur_jobs = pd.read_csv(get_dataset_path('european_jobs.csv'))

# Try to load enhanced dataset with education fields, fallback to original
try:
    enhanced_jobs = pd.read_csv(get_dataset_path('european_jobs_with_education_fields.csv'))
    print("✅ Using enhanced dataset with education fields")
    eur_jobs = enhanced_jobs
except FileNotFoundError:
    print("ℹ️ Enhanced dataset not found, using original dataset")

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
    show_education_language_page(content, eur_jobs)

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
    show_profiles_page(content)
