import streamlit as st
import pandas as pd
import json
import ast
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# Add project root to Python path for deployment
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dashboard.style import show_chart_with_card
from dashboard.helpers import restore_list_json



# -----------------
# HELPERS: EDUCATION LEVEL NORMALIZATION
# Only keep bachelor/master/phd (highest if multiple)
# -----------------

EDU_RANK = {"bachelor": 1, "master": 2, "phd": 3}
EDU_ORDER = ["bachelor", "master", "phd"]


def normalize_education_level(x):
    if pd.isna(x):
        return None

    if isinstance(x, str) and x.startswith("["):
        try:
            levels = ast.literal_eval(x)
        except Exception:
            return None
    elif isinstance(x, str):
        levels = [x.lower()]
    elif isinstance(x, list):
        levels = [str(l).lower() for l in x]
    else:
        return None

    levels = [l.strip() for l in levels if isinstance(l, str)]
    valid = [l for l in levels if l in EDU_RANK]
    if not valid:
        return None

    return max(valid, key=lambda l: EDU_RANK[l])

# -----------------
# SECTION: EDUCATION
# -----------------

def render_education_section(base_df: pd.DataFrame):
    st.subheader("Qualification Requirements")

    edu_df = base_df.copy()

    # Education requirement explicitly stated
    edu_df["has_education_requirement"] = (
        edu_df["education_level"].notna() | edu_df["education_field"].notna()
    )

    # Clean education level (bachelor/master/phd only)
    edu_df["education_level_clean"] = edu_df["education_level"].apply(normalize_education_level)

    # Controls
    agg = st.selectbox(
        "Aggregate education analysis by:",
        ["Overall", "Country", "ISCO-3 occupation"],
        key="edu_agg"
    )

    # KPI card: share of jobs mentioning education requirements
    share_edu_req = edu_df["has_education_requirement"].mean() * 100
    fig_kpi = go.Figure(go.Indicator(
        mode="number",
        value=share_edu_req,
        number={"suffix": "%"},
        title={"text": "Jobs Explicitly Mentioning Education Requirements"}
    ))
    fig_kpi.update_layout(
        margin=dict(t=35, l=20, r=20, b=15),
        font=dict(color="#1F2933")
    )
    show_chart_with_card(fig_kpi, height=170)

    # Only jobs with a cleaned level for level distribution plots
    edu_levels = edu_df[edu_df["education_level_clean"].notna()].copy()

    if edu_levels.empty:
        st.info("No valid education level found (bachelor/master/phd) in the dataset.")
        return

    if agg == "Overall":
        dist = (
            edu_levels["education_level_clean"]
            .value_counts(normalize=True)
            .mul(100)
            .reset_index()
        )
        dist.columns = ["education_level", "percentage"]
        dist["education_level"] = pd.Categorical(dist["education_level"], categories=EDU_ORDER, ordered=True)
        dist = dist.sort_values("education_level")

        fig = px.bar(
            dist,
            x="education_level",
            y="percentage",
            text="percentage",
            labels={"education_level": "Education level", "percentage": "Share of job postings (%)"},
            title="Distribution of Education Levels (When Specified)",
            color_discrete_sequence=["#3B6C8E"]
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(
            yaxis_range=[0, 100],
            margin=dict(t=55, l=40, r=20, b=40),
            font=dict(color="#1F2933")
        )
        show_chart_with_card(fig)

    elif agg == "Country":
        dist = (
            edu_levels
            .groupby(["country", "education_level_clean"], dropna=False)
            .size()
            .reset_index(name="count")
        )
        totals = dist.groupby("country")["count"].transform("sum")
        dist["percentage"] = (dist["count"] / totals) * 100

        dist["education_level_clean"] = pd.Categorical(dist["education_level_clean"], categories=EDU_ORDER, ordered=True)
        dist = dist.sort_values(["country", "education_level_clean"])

        fig = px.bar(
            dist,
            x="country",
            y="percentage",
            color="education_level_clean",
            barmode="stack",
            labels={"country": "Country", "percentage": "Share (%)", "education_level_clean": "Education level"},
            title="Education Level Distribution by Country",
            color_discrete_sequence=["#9DB4C0", "#3B6C8E", "#162544"]
        )
        fig.update_layout(
            yaxis_range=[0, 100],
            xaxis_tickangle=-45,
            margin=dict(t=55, l=40, r=20, b=90),
            font=dict(color="#1F2933"),
            legend_title_text="Education level"
        )
        show_chart_with_card(fig)

    else:  # ISCO-3 occupation
        dist = (
            edu_levels
            .groupby(["isco_3_label", "education_level_clean"], dropna=False)
            .size()
            .reset_index(name="count")
        )
        totals = dist.groupby("isco_3_label")["count"].transform("sum")
        dist["percentage"] = (dist["count"] / totals) * 100

        dist["education_level_clean"] = pd.Categorical(dist["education_level_clean"], categories=EDU_ORDER, ordered=True)

        # Optional: reduce clutter by keeping top ISCO groups by volume
        top_n = st.slider("Top ISCO groups to display (by volume)", 5, 40, 15, key="edu_topn")
        isco_order = (
            edu_levels["isco_3_label"]
            .value_counts()
            .head(top_n)
            .index.tolist()
        )
        dist = dist[dist["isco_3_label"].isin(isco_order)].copy()

        fig = px.bar(
            dist,
            y="isco_3_label",
            x="percentage",
            color="education_level_clean",
            orientation="h",
            barmode="stack",
            labels={"isco_3_label": "ISCO-3 occupation", "percentage": "Share (%)", "education_level_clean": "Education level"},
            title="Education Level Distribution by ISCO-3 Occupation (Top groups)",
            color_discrete_sequence=["#9DB4C0", "#3B6C8E", "#162544"]
        )
        fig.update_layout(
            xaxis_range=[0, 100],
            yaxis=dict(autorange="reversed"),
            margin=dict(t=55, l=40, r=20, b=40),
            font=dict(color="#1F2933"),
            legend_title_text="Education level"
        )
        show_chart_with_card(fig)


# -----------------
# SECTION: EDUCATION FIELDS
# -----------------

def build_education_field_df(df: pd.DataFrame):
    """Build a dataframe with education fields from PhD and Master extractions."""
    records = []

    # Check which ISCO column is available
    isco_col = None
    if "isco_3_label" in df.columns:
        isco_col = "isco_3_label"
    elif "isco_3_digit_label" in df.columns:
        isco_col = "isco_3_digit_label"

    for _, row in df.iterrows():
        if pd.notna(row.get("education_field_phd_clean")):
            records.append({
                "degree": "PhD",
                "field": row["education_field_phd_clean"],
                "isco_3_label": row.get(isco_col) if isco_col else None
            })

        if pd.notna(row.get("education_field_master_clean")):
            records.append({
                "degree": "Master",
                "field": row["education_field_master_clean"],
                "isco_3_label": row.get(isco_col) if isco_col else None
            })

    return pd.DataFrame(records)


def render_education_fields_section(base_df: pd.DataFrame):
    st.subheader("Qualification Domain When Mentioned")
    
    # Check if required columns exist
    required_cols = ["education_field_phd_clean", "education_field_master_clean"]
    if not all(col in base_df.columns for col in required_cols):
        st.info("Education field data not available. Please run the education field extraction process first.")
        return
    
    edu_field_df = build_education_field_df(base_df)
    
    if edu_field_df.empty:
        st.info("No education fields found in the dataset.")
        return
    
    agg_choice = st.selectbox(
        "Aggregate by",
        ["Overall", "ISCO-3 occupation"],
        key="edu_field_agg"
    )
    
    degree_choice = st.radio(
        "Degree level",
        ["PhD", "Master"],
        horizontal=True,
        key="edu_field_degree"
    )

    df_sel = edu_field_df[edu_field_df["degree"] == degree_choice].copy()

    # Remove generic placeholders and outliers
    GENERIC_FIELDS = {
        "a relevant field",
        "relevant field",
        "technical or industry related field",
        "one of the following fields",
        "the specialty",
        "a master"
    }
    df_sel = df_sel[~df_sel["field"].str.lower().isin(GENERIC_FIELDS)]
    # Remove fields containing "English" or "Huawei" (outliers)
    df_sel = df_sel[
        ~df_sel["field"].str.contains("English", case=False, na=False)
    ]
    df_sel = df_sel[
        ~df_sel["field"].str.contains("Huawei", case=False, na=False)
    ]

    if agg_choice == "Overall":
        top_fields = (
            df_sel["field"]
            .value_counts()
            .head(10)
        )

    else:  # ISCO-3 occupation
        isco_options = sorted(df_sel["isco_3_label"].dropna().unique())
        if not isco_options:
            st.info(f"No ISCO-3 data available for {degree_choice} degrees.")
            return
            
        isco_choice = st.selectbox(
            "Select ISCO-3 occupation",
            isco_options,
            key="edu_field_isco"
        )

        top_fields = (
            df_sel[df_sel["isco_3_label"] == isco_choice]["field"]
            .value_counts()
            .head(10)
        )

    if top_fields.empty:
        st.info(f"No education fields found for this selection ({degree_choice}).")
    else:
        st.markdown(f"**Top {degree_choice} studies cited**")

        for i, field in enumerate(top_fields.index, start=1):
            st.markdown(f"{i}. **{field}**")


# -----------------
# SECTION: LANGUAGES
# -----------------

def render_language_section(base_df: pd.DataFrame):
    st.subheader("Language Requirements")

    lang_df = base_df.copy()

    # Restore languages list from JSON string
    if "languages" in lang_df.columns:
        lang_df["languages"] = lang_df["languages"].apply(restore_list_json)
    else:
        st.info("No 'languages' column found.")
        return

    # KPI: jobs mentioning at least one language
    lang_df["has_language_requirement"] = lang_df["languages"].apply(
        lambda x: isinstance(x, list) and len(x) > 0
    )
    language_share = lang_df["has_language_requirement"].mean() * 100

    # Create simple metric indicator (same as education section)
    fig_metric = go.Figure(go.Indicator(
        mode="number",
        value=language_share,
        number={"suffix": "%"},
        title={"text": "Jobs Requiring a Language Proficiency"}
    ))
    fig_metric.update_layout(
        margin=dict(t=35, l=20, r=20, b=15),
        font=dict(color="#1F2933")
    )
    show_chart_with_card(fig_metric, height=170)

    # Distribution of languages (only among explicit mentions)
    df_lang = lang_df.explode("languages").copy()
    df_lang = df_lang[df_lang["languages"].notna() & (df_lang["languages"] != "")]
    
    # Filter out invalid languages
    invalid_languages = ["swedish"]  # Add more non-languages here if needed
    df_lang = df_lang[~df_lang["languages"].str.lower().isin(invalid_languages)]
    
    if df_lang.empty:
        st.info("No explicit language mentions found.")
        return

    counts = df_lang["languages"].value_counts().reset_index()
    counts.columns = ["language", "job_count"]
    
    # Fixed to top 8 languages, removed slider
    counts = counts.head(8)

    fig_lang = px.bar(
        counts,
        x="job_count",
        y="language",
        orientation="h",
        labels={"job_count": "Number of job postings", "language": " "},
        title="Top Most Frequently Requested Languages",
        color_discrete_sequence=["#3B6C8E"]
    )
    fig_lang.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(t=55, l=40, r=20, b=40),
        font=dict(color="#1F2933")
    )
    show_chart_with_card(fig_lang)

def render_ISCED_section(base_df: pd.DataFrame):
    st.header("ISCED Field Classification Analysis")

# -----------------
# MAIN PAGE FUNCTION
# -----------------

def show_education_language_page(contents: pd.DataFrame, enhanced_jobs: pd.DataFrame = None):
    # Base dataframe: never mutate this
    base_df = contents.copy()
    st.title("Education & Languages Requirements")
    st.markdown("---")
    
    # Official ISCED Classification
    render_ISCED_section(base_df)
    st.markdown("---")

    # Education qualifications requirements
    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_education_section(base_df)

    with col2:
        if enhanced_jobs is not None:
            render_education_fields_section(enhanced_jobs)
        else:
            render_education_fields_section(base_df)
    
    # Language section
    st.markdown("---")
    col1, col2 = st.columns([3, 2])
    render_language_section(base_df)

