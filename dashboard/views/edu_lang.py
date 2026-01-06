import streamlit as st
import pandas as pd
import json
import ast
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from dashboard.utils import get_dataset_path, get_static_path


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

def load_isced_classifications():
    """Load ISCED classification results and merge with main dataset."""
    try:
        # Load ISCED classification
        project_root = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        ))
        isced_path = os.path.join(
            project_root, "outputs", "isced_classification.jsonl"
        )
        
        with open(isced_path, 'r') as f:
            isced_data = [json.loads(line) for line in f]
        
        # Convert to DataFrame and filter out null classifications
        isced_df = pd.DataFrame(isced_data)
        isced_df = isced_df[isced_df['isced_broad_code'].notna()]
        
        return isced_df
    
    except FileNotFoundError:
        st.warning(
            "ISCED classification file not found. "
            "Please run the education classifier first."
        )
        return None
    except Exception as e:
        st.error(f"Error loading ISCED classifications: {e}")
        return None


def create_isced_isco_heatmap(base_df: pd.DataFrame):
    """Create ISCED Field × ISCO Domain Matrix Heatmap."""
    
    # Load ISCED classifications
    isced_df = load_isced_classifications()
    if isced_df is None:
        return
    
    # Merge with main dataset to get ISCO information
    # Check which ISCO column is available
    isco_col = None
    if "isco_3_digit_label" in base_df.columns:
        isco_col = "isco_3_digit_label"
    elif "isco_3_label" in base_df.columns:
        isco_col = "isco_3_label"
    else:
        st.error("No ISCO label column found in dataset")
        return
    
    # Merge datasets
    merged_df = base_df[['job_id', isco_col]].merge(
        isced_df[['job_id', 'isced_broad_name']],
        on='job_id',
        how='inner'
    )
    
    if merged_df.empty:
        st.warning(
            "No data found after merging ISCED and ISCO classifications"
        )
        return
    
    # Create cross-tabulation for heatmap
    heatmap_data = pd.crosstab(
        merged_df['isced_broad_name'],
        merged_df[isco_col],
        normalize='index'  # Normalize by row (ISCED field)
    ) * 100  # Convert to percentages
    
    # Keep only top ISCO categories to avoid clutter
    top_isco = merged_df[isco_col].value_counts().head(12).index
    heatmap_data = heatmap_data[top_isco]
    
    # Keep only top ISCED categories
    top_isced = merged_df['isced_broad_name'].value_counts().head(8).index
    heatmap_data = heatmap_data.loc[top_isced]
    
    # Create heatmap
    x_labels = [
        label[:25] + "..." if len(label) > 25 else label 
        for label in heatmap_data.columns
    ]
    y_labels = [
        label[:30] + "..." if len(label) > 30 else label 
        for label in heatmap_data.index
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=x_labels,
        y=y_labels,
        colorscale='Blues',
        showscale=False,  # Remove color bar
        hovertemplate='<b>%{y}</b><br>%{x}<br>%{z:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="ISCED Education Field × ISCO Occupation Distribution",
        xaxis_title="ISCO-3 Occupation",
        yaxis_title="ISCED Education Field",
        height=500,
        margin=dict(t=60, l=200, r=40, b=150),
        font=dict(color="#1F2933"),
        xaxis=dict(tickangle=45)
    )
    
    show_chart_with_card(fig)
    
    # Show summary statistics
    n_fields = len(heatmap_data)
    n_occupations = len(heatmap_data.columns)
    n_jobs = len(merged_df)
    st.caption(
        f"Showing top {n_fields} ISCED fields × "
        f"top {n_occupations} ISCO occupations | "
        f"Based on {n_jobs:,} classified jobs"
    )


def create_isced_geo_map(base_df: pd.DataFrame):
    """Create choropleth map of ISCED education field requirements."""
    
    # Load ISCED classifications
    isced_df = load_isced_classifications()
    if isced_df is None:
        return
    
    # Check available columns in base_df
    available_cols = ['job_id', 'country']
    if 'country_code' in base_df.columns:
        available_cols.append('country_code')
    
    # Merge with main dataset to get country information
    merged_df = base_df[available_cols].merge(
        isced_df[['job_id', 'isced_broad_name']],
        on='job_id',
        how='inner'
    )
    
    if merged_df.empty:
        st.warning("No data found for geographic analysis")
        return
    
    # ISO-2 to ISO-3 conversion mapping (same as overview.py)
    ISO2_TO_ISO3 = {
        "be": "BEL", "bg": "BGR", "cz": "CZE", "dk": "DNK", "de": "DEU",
        "ee": "EST", "ie": "IRL", "el": "GRC", "gr": "GRC", "es": "ESP",
        "fr": "FRA", "hr": "HRV", "it": "ITA", "cy": "CYP", "lv": "LVA",
        "lt": "LTU", "lu": "LUX", "hu": "HUN", "mt": "MLT", "nl": "NLD",
        "at": "AUT", "pl": "POL", "pt": "PRT", "ro": "ROU", "si": "SVN",
        "sk": "SVK", "fi": "FIN", "se": "SWE", "no": "NOR", "ch": "CHE",
        "tr": "TUR"
    }
    
    # Convert country_code to ISO-3 if available
    if 'country_code' in merged_df.columns:
        merged_df['country_code_iso3'] = (
            merged_df['country_code'].str.lower().map(ISO2_TO_ISO3)
        )
    else:
        # Create country code mapping from country names if needed
        country_name_to_iso2 = {
            'Austria': 'at', 'Belgium': 'be', 'Bulgaria': 'bg',
            'Croatia': 'hr', 'Cyprus': 'cy', 'Czechia': 'cz',
            'Denmark': 'dk', 'Estonia': 'ee', 'Finland': 'fi',
            'France': 'fr', 'Germany': 'de', 'Greece': 'gr',
            'Hungary': 'hu', 'Ireland': 'ie', 'Italy': 'it',
            'Latvia': 'lv', 'Lithuania': 'lt', 'Luxembourg': 'lu',
            'Malta': 'mt', 'Netherlands': 'nl', 'Norway': 'no',
            'Poland': 'pl', 'Portugal': 'pt', 'Romania': 'ro',
            'Slovakia': 'sk', 'Slovenia': 'si', 'Spain': 'es',
            'Sweden': 'se', 'Switzerland': 'ch', 'Turkey': 'tr'
        }
        merged_df['country_code_iso2'] = (
            merged_df['country'].map(country_name_to_iso2)
        )
        merged_df['country_code_iso3'] = (
            merged_df['country_code_iso2'].map(ISO2_TO_ISO3)
        )
    
    # Filter out unmapped codes
    merged_df = merged_df[merged_df['country_code_iso3'].notna()]
    
    # Add field selector
    isced_fields = sorted(merged_df['isced_broad_name'].unique())
    selected_field = st.selectbox(
        "Select ISCED Education Field:",
        ["All Fields"] + list(isced_fields),
        key="isced_geo_field"
    )
    
    # Filter data
    if selected_field != "All Fields":
        map_data = merged_df[merged_df['isced_broad_name'] == selected_field]
        title_text = (f"Geographic Distribution of "
                      f"{selected_field} Requirements")
    else:
        map_data = merged_df
        title_text = "Geographic Distribution of Education Field Requirements"
    
    # Aggregate by country
    country_stats = (
        map_data.groupby(['country', 'country_code_iso3'])
        .size()
        .reset_index(name='job_count')
    )
    
    # Create choropleth map using Plotly Express (same approach as overview.py)
    fig = px.choropleth(
        country_stats,
        locations="country_code_iso3",
        color="job_count",
        locationmode="ISO-3",
        scope="europe",
        color_continuous_scale="Blues",
        labels={"job_count": "Number of job postings"},
        title=title_text,
        hover_name="country",
        hover_data={"country_code_iso3": False, "job_count": ":,"}
    )
    
    fig.update_layout(
        height=500,
        margin=dict(t=60, l=20, r=20, b=90),
        font=dict(color="#1F2933"),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False  # Remove color bar
    )
    
    show_chart_with_card(fig)
    
    # Show summary statistics
    total_countries = len(country_stats)
    total_jobs = country_stats['job_count'].sum()
    if selected_field != "All Fields":
        st.caption(
            f"{total_countries} countries | {total_jobs:,} jobs requiring "
            f"{selected_field}"
        )
    else:
        caption_text = (f"{total_countries} countries | "
                        f"{total_jobs:,} jobs with specific education field "
                        f"requirements")
        st.caption(caption_text)


def create_isced_level_distribution(base_df: pd.DataFrame):
    """Create education field distribution visualization."""
    
    # Load ISCED classifications
    isced_df = load_isced_classifications()
    if isced_df is None:
        return
    
    # Merge with base dataset
    merged_df = base_df[['job_id']].merge(
        isced_df[['job_id', 'isced_broad_name']],
        on='job_id',
        how='inner'
    )
    
    if merged_df.empty:
        st.warning("No ISCED classification data found")
        return
    
    # Calculate distribution
    field_counts = (
        merged_df['isced_broad_name']
        .value_counts()
        .reset_index()
    )
    field_counts.columns = ['education_field', 'job_count']
    
    # Remove null values and calculate percentages
    field_counts = field_counts[field_counts['education_field'] != 'null']
    total_jobs = field_counts['job_count'].sum()
    field_counts['percentage'] = (
        field_counts['job_count'] / total_jobs * 100
    ).round(1)
    
    # Add cumulative percentage
    field_counts['cumulative_pct'] = field_counts['percentage'].cumsum()
    
    # Set to static top 15
    max_fields = len(field_counts)
    top_n = min(15, max_fields)  # Top 15 or all fields if less than 15
    
    # Filter to top N
    display_data = field_counts.head(top_n)
    
    # Create horizontal bar chart
    fig = px.bar(
        display_data,
        x='job_count',
        y='education_field',
        orientation='h',
        title=f"Top {top_n} Education Field Requirements",
        labels={
            'job_count': 'Number of Job Postings',
            'education_field': 'ISCED Education Field'
        },
        color='percentage',
        color_continuous_scale='Blues',
        text='percentage',
        template='plotly_white'
    )
    
    # Update layout for better readability
    fig.update_layout(
        height=max(400, top_n * 40),  # Dynamic height based on bars
        yaxis=dict(autorange="reversed"),  # Largest on top
        margin=dict(t=60, l=40, r=120, b=90),
        font=dict(color="#1F2933"),
        showlegend=False,
        coloraxis_showscale=False
    )
    
    # Update text annotations
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside',
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Jobs: %{x:,}<br>"
            "Percentage: %{text:.1f}%<br>"
            "<extra></extra>"
        )
    )
    
    show_chart_with_card(fig)
    
    # Show summary statistics
    if top_n < max_fields:
        other_count = field_counts.iloc[top_n:]['job_count'].sum()
        other_pct = other_count / total_jobs * 100
        st.caption(
            f"Showing top {top_n} of {max_fields} fields | "
            f"{total_jobs:,} total jobs | "
            f"Other fields: {other_count:,} jobs ({other_pct:.1f}%)"
        )
    else:
        st.caption(
            f"All {max_fields} education fields | {total_jobs:,} total jobs"
        )
    
    # Show detailed breakdown table
    with st.expander("Detailed Education Field Statistics"):
        # Prepare display table
        display_table = field_counts.copy()
        display_table['percentage_str'] = display_table['percentage'].apply(
            lambda x: f"{x:.1f}%"
        )
        display_table['cumulative_str'] = (
            display_table['cumulative_pct'].apply(lambda x: f"{x:.1f}%")
        )
        
        # Rename columns for display
        display_table = display_table[[
            'education_field', 'job_count', 'percentage_str', 'cumulative_str'
        ]]
        display_table.columns = [
            'Education Field', 'Job Count', 'Percentage', 'Cumulative %'
        ]
        
        st.dataframe(
            display_table,
            hide_index=True,
            use_container_width=True
        )


def render_ISCED_section(base_df: pd.DataFrame):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader("ISCED Field Classification Analysis")
    with col2:
        try:
            # Use the correct path to the ISCED PDF
            project_root = os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ))
            isced_path = os.path.join(
                project_root, "processing", "education_classification",
                "ISCED_official.pdf"
            )
            
            with open(isced_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                st.download_button(
                    label="Read Official ISCED Classification",
                    data=pdf_bytes,
                    file_name="ISCED_official.pdf",
                    mime="application/pdf"
                )
        except FileNotFoundError:
            st.warning("Official documentation not found")

    col1, col2 = st.columns(2)
    with col1:
        # ISCED Field × ISCO Domain Matrix - IMPLEMENTED!
        create_isced_isco_heatmap(base_df)
        st.markdown("---")
        # Education Level Distribution - IMPLEMENTED!
        create_isced_level_distribution(base_df)
    with col2:
        # Geo map of ISCED requests - IMPLEMENTED!
        create_isced_geo_map(base_df)
        st.markdown("---")
        # Education Field × Sustainability (GreenComp Overlay) - NOW IMPLEMENTED!
        create_isced_greencomp_overlay(base_df)


def create_isced_greencomp_overlay(base_df: pd.DataFrame):
    """Create Education Field × Sustainability (GreenComp) overlay analysis."""
    
    # Load ISCED classifications
    isced_df = load_isced_classifications()
    if isced_df is None:
        return
    
    # Load GreenComp extractions data
    try:
        from dashboard.helpers import restore_list_safe
        extractions_df = pd.read_csv(get_dataset_path('extractions.csv'))
        
        # Merge ISCED with GreenComp data
        merged_df = base_df[['job_id']].merge(
            isced_df[['job_id', 'isced_broad_name']],
            on='job_id',
            how='inner'
        ).merge(
            extractions_df[['job_id', 'green_competences']],
            on='job_id',
            how='inner'
        )
        
        if merged_df.empty:
            st.warning("No data found for ISCED-GreenComp analysis")
            return
        
        # Process GreenComp data
        merged_df['green_competences'] = merged_df['green_competences'].apply(
            restore_list_safe
        )
        
        # Create sustainability exposure metrics
        merged_df['has_sustainability'] = merged_df['green_competences'].apply(
            lambda x: len(x) > 0 if isinstance(x, list) else False
        )
        merged_df['sustainability_count'] = merged_df['green_competences'].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        )
        
        # Remove null ISCED fields
        analysis_df = merged_df[
            (merged_df['isced_broad_name'] != 'null') & 
            (merged_df['isced_broad_name'].notna())
        ]
        
        # Calculate sustainability exposure by education field
        field_sustainability = (
            analysis_df.groupby('isced_broad_name')
            .agg({
                'job_id': 'count',  # Total jobs in field
                'has_sustainability': 'sum',  # Jobs with sustainability requirements
                'sustainability_count': 'mean'  # Average sustainability competences
            })
            .reset_index()
        )
        
        # Calculate sustainability exposure rate
        field_sustainability['sustainability_rate'] = (
            field_sustainability['has_sustainability'] / 
            field_sustainability['job_id'] * 100
        ).round(1)
        
        # Filter fields with at least 20 jobs for statistical relevance
        field_sustainability = field_sustainability[
            field_sustainability['job_id'] >= 20
        ].sort_values('sustainability_rate', ascending=False)
        
        # Create bubble chart
        fig = px.scatter(
            field_sustainability,
            x='job_id',
            y='sustainability_rate',
            size='sustainability_count',
            hover_name='isced_broad_name',
            title="Education Fields × Sustainability Exposure",
            labels={
                'job_id': 'Total Jobs in Field',
                'sustainability_rate': 'Sustainability Exposure Rate (%)',
                'sustainability_count': 'Avg. Sustainability Competences'
            },
            color='sustainability_rate',
            color_continuous_scale='Greens',
            template='plotly_white',
            size_max=30
        )
        
        # Update layout
        fig.update_layout(
            height=500,
            margin=dict(t=60, l=60, r=20, b=60),
            font=dict(color="#1F2933"),
            xaxis_title="Number of Jobs in Field",
            yaxis_title="Sustainability Exposure Rate (%)",
            coloraxis_showscale=False  # Remove color bar
        )
        
        # Update hover
        fig.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Jobs: %{x:,}<br>"
                "Sustainability Rate: %{y:.1f}%<br>"
                "Avg. Competences: %{marker.size:.2f}<br>"
                "<extra></extra>"
            )
        )
        
        show_chart_with_card(fig)
        
        # Show top sustainability-exposed fields
        top_sustainable = field_sustainability.head(8)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Most Sustainability-Exposed Fields**")
            for _, row in top_sustainable.iterrows():
                field_name = row['isced_broad_name']
                rate = row['sustainability_rate']
                jobs = int(row['job_id'])
                st.markdown(
                    f"• **{field_name}**: {rate:.1f}% ({jobs:,} jobs)"
                )
        
        with col2:
            # Show overall statistics
            total_jobs = field_sustainability['job_id'].sum()
            total_sustainable = field_sustainability['has_sustainability'].sum()
            avg_exposure = (total_sustainable / total_jobs * 100) if total_jobs > 0 else 0
            
            st.markdown("**Overall Statistics**")
            st.markdown(f"• Total analyzed fields: {len(field_sustainability)}")
            st.markdown(f"• Total jobs: {total_jobs:,}")
            st.markdown(f"• Jobs with sustainability: {int(total_sustainable):,}")
            st.markdown(f"• Average exposure rate: {avg_exposure:.1f}%")
        
        # Show detailed table in expander
        with st.expander("Detailed Field Analysis"):
            display_table = field_sustainability.copy()
            display_table['sustainability_rate_str'] = (
                display_table['sustainability_rate'].apply(lambda x: f"{x:.1f}%")
            )
            display_table['sustainability_count_str'] = (
                display_table['sustainability_count'].apply(lambda x: f"{x:.2f}")
            )
            
            display_table = display_table[[
                'isced_broad_name', 'job_id', 'has_sustainability', 
                'sustainability_rate_str', 'sustainability_count_str'
            ]]
            display_table.columns = [
                'Education Field', 'Total Jobs', 'Sustainable Jobs', 
                'Exposure Rate', 'Avg. Competences'
            ]
            
            st.dataframe(
                display_table,
                hide_index=True,
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Error loading GreenComp analysis: {str(e)}")
        st.info("GreenComp analysis requires the extractions dataset with "
                "green_competences column")


# -----------------
# MAIN PAGE FUNCTION
# -----------------


def show_education_language_page(
    contents: pd.DataFrame, enhanced_jobs: pd.DataFrame = None
):
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

