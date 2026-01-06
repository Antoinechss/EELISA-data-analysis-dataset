import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
import json

# Add project root to Python path for deployment
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dashboard.style import show_chart_with_card
from dashboard.utils import get_dataset_path
from dashboard.helpers import restore_list_safe

# Load extractions data for profile analysis
extractions_df = pd.read_csv(get_dataset_path('extractions.csv'))

# Define Transition Engineering Profiles
TRANSITION_PROFILES = {
    "Sustainable Systems": {
        "description": "Engineers designing holistic sustainable systems",
        "keywords": ["systems", "sustainability", "holistic", "design", "integration"],
        "isco_focus": ["Engineering professionals", "Science and engineering associate professionals"]
    },
    "Digital Green": {
        "description": "Bridges digital technologies with environmental sustainability",
        "keywords": ["digital", "green", "environmental", "technology", "sustainable"],
        "isco_focus": ["Information and communications technology professionals", "Engineering professionals"]
    },
    "Industrial Transition": {
        "description": "Transforms traditional industrial processes for sustainability",
        "keywords": ["industrial", "transition", "manufacturing", "process", "transformation"],
        "isco_focus": ["Engineering professionals", "Science and engineering associate professionals"]
    },
    "Research & Innovation": {
        "description": "Drives research and innovation in sustainable technologies",
        "keywords": ["research", "innovation", "technology", "development", "R&D"],
        "isco_focus": ["Engineering professionals", "Science and engineering professionals"]
    },
    "Policy-Aware": {
        "description": "Integrates engineering solutions with policy and regulatory frameworks",
        "keywords": ["policy", "regulation", "governance", "compliance", "framework"],
        "isco_focus": ["Engineering professionals", "Legal, social and cultural professionals"]
    }
}

# Skills categories for analysis
SKILL_CATEGORIES = {
    "Core Engineering": ["engineering", "technical", "design", "development"],
    "Digital & Data": ["digital", "data", "software", "AI", "programming", "analytics"],
    "Sustainability": ["sustainability", "environmental", "green", "renewable", "climate"],
    "Soft Skills": ["communication", "leadership", "management", "teamwork"],
    "Systems Thinking": ["systems", "complex", "integration", "interdisciplinary"]
}


def classify_job_into_profiles(row):
    """Classify a job into transition engineering profiles based on content."""
    scores = {}
    
    # Combine text fields for analysis
    text_content = " ".join([
        str(row.get('job_title', '')),
        str(row.get('isco_3_label', '')),
        " ".join(restore_list_safe(row.get('hard_skills', '[]'))),
        " ".join(restore_list_safe(row.get('knowledge_domains', '[]'))),
        " ".join(restore_list_safe(row.get('green_competences', '[]')))
    ]).lower()
    
    # Score each profile
    for profile_name, profile_info in TRANSITION_PROFILES.items():
        score = 0
        keyword_matches = 0
        
        # Check keywords
        for keyword in profile_info['keywords']:
            if keyword in text_content:
                keyword_matches += 1
        
        # Check ISCO alignment
        isco_match = any(isco.lower() in str(row.get('isco_3_label', '')).lower() 
                        for isco in profile_info['isco_focus'])
        
        # Calculate composite score
        score = keyword_matches + (2 if isco_match else 0)
        scores[profile_name] = score
    
    # Return best matching profile if score > threshold
    if scores and max(scores.values()) >= 2:
        return max(scores, key=scores.get)
    else:
        return "Other Engineering"


def calculate_profile_dimensions(profile_df):
    """Calculate radar chart dimensions for a profile."""
    dimensions = {}
    
    # Digital intensity
    digital_skills = profile_df['digital_competences'].apply(
        lambda x: len(restore_list_safe(x)) if pd.notna(x) else 0
    )
    dimensions['Digital Intensity'] = digital_skills.mean()
    
    # Sustainability (GreenComp score)
    green_skills = profile_df['green_competences'].apply(
        lambda x: len(restore_list_safe(x)) if pd.notna(x) else 0
    )
    dimensions['Sustainability'] = green_skills.mean()
    
    # Education level (normalized)
    edu_mapping = {'Bachelor': 1, 'Master': 2, 'PhD': 3}
    education_scores = profile_df['education_level'].map(edu_mapping).fillna(0)
    dimensions['Education Level'] = education_scores.mean()
    
    # Systems thinking (interdisciplinary skills)
    systems_score = profile_df.apply(lambda row: sum([
        1 for skill in restore_list_safe(row.get('hard_skills', '[]'))
        if any(keyword in skill.lower() 
               for keyword in ['system', 'integration', 'complex'])
    ]), axis=1)
    dimensions['Systems Thinking'] = systems_score.mean()
    
    # Innovation orientation
    innovation_score = profile_df.apply(lambda row: sum([
        1 for skill in restore_list_safe(row.get('knowledge_domains', '[]'))
        if any(keyword in skill.lower() 
               for keyword in ['research', 'innovation', 'development'])
    ]), axis=1)
    dimensions['Innovation'] = innovation_score.mean()
    
    # Regulatory awareness
    regulatory_score = profile_df.apply(lambda row: sum([
        1 for skill in restore_list_safe(row.get('knowledge_domains', '[]'))
        if any(keyword in skill.lower() 
               for keyword in ['policy', 'regulation', 'compliance'])
    ]), axis=1)
    dimensions['Regulatory Awareness'] = regulatory_score.mean()
    
    return dimensions


def create_profile_radar_chart(profile_name, dimensions):
    """Create radar/spider chart for profile signature."""
    
    # Normalize dimensions to 0-100 scale
    max_vals = {
        'Digital Intensity': 5, 'Sustainability': 5, 'Education Level': 3,
        'Systems Thinking': 3, 'Innovation': 3, 'Regulatory Awareness': 2
    }
    
    normalized_dims = {}
    for dim, val in dimensions.items():
        max_val = max_vals.get(dim, 5)
        normalized_dims[dim] = min((val / max_val) * 100, 100)
    
    categories = list(normalized_dims.keys())
    values = list(normalized_dims.values())
    
    # Close the polygon
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=profile_name,
        line=dict(color='#2E86AB', width=2),
        fillcolor='rgba(46, 134, 171, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%'
            )
        ),
        title=f"{profile_name} - Profile Signature",
        height=400,
        margin=dict(t=60, l=20, r=20, b=60),
        font=dict(color="#1F2933")
    )
    
    return fig


def create_skill_stack_composition(profile_df):
    """Create skill stack composition chart."""
    skill_counts = {category: 0 for category in SKILL_CATEGORIES.keys()}
    
    for _, row in profile_df.iterrows():
        all_skills = []
        for skill_field in ['hard_skills', 'knowledge_domains', 'soft_skills']:
            all_skills.extend(restore_list_safe(row.get(skill_field, '[]')))
        
        for skill in all_skills:
            skill_lower = skill.lower()
            for category, keywords in SKILL_CATEGORIES.items():
                if any(keyword in skill_lower for keyword in keywords):
                    skill_counts[category] += 1
                    break
    
    total_skills = sum(skill_counts.values())
    if total_skills == 0:
        return None
    
    # Calculate percentages
    skill_percentages = {k: (v/total_skills)*100 for k, v in skill_counts.items()}
    
    # Create horizontal stacked bar
    fig = go.Figure()
    
    categories = list(skill_percentages.keys())
    values = list(skill_percentages.values())
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83']
    
    y_pos = 0
    x_pos = 0
    for i, (category, percentage) in enumerate(skill_percentages.items()):
        if percentage > 0:
            fig.add_trace(go.Bar(
                name=category,
                x=[percentage],
                y=[y_pos],
                orientation='h',
                marker=dict(color=colors[i % len(colors)]),
                text=f"{percentage:.1f}%",
                textposition='inside',
                base=x_pos
            ))
            x_pos += percentage
    
    fig.update_layout(
        title="Skill Stack Composition",
        xaxis_title="Percentage of Skills",
        yaxis=dict(showticklabels=False),
        barmode='stack',
        height=200,
        margin=dict(t=60, l=20, r=20, b=80),
        font=dict(color="#1F2933"),
        showlegend=True,
        legend=dict(orientation="h", y=-0.3)
    )
    
    return fig


def create_education_pathway_matrix(profile_df):
    """Create education level × field matrix."""
    try:
        # Load ISCED data
        isced_path = os.path.join(project_root, "outputs", "isced_classification.jsonl")
        isced_data = []
        with open(isced_path, 'r') as f:
            for line in f:
                isced_data.append(json.loads(line))
        isced_df = pd.DataFrame(isced_data)
        
        # Merge with profile data
        merged_df = profile_df[['job_id', 'education_level']].merge(
            isced_df[['job_id', 'isced_broad_name']], on='job_id', how='inner'
        )
        
        if merged_df.empty:
            return None
        
        # Create cross-tabulation
        education_matrix = pd.crosstab(
            merged_df['education_level'], 
            merged_df['isced_broad_name'], 
            normalize='all'
        ) * 100
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=education_matrix.values,
            x=education_matrix.columns,
            y=education_matrix.index,
            colorscale='Blues',
            showscale=False,
            hovertemplate='<b>%{y}</b><br>%{x}<br>%{z:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="Education Pathway Matrix",
            xaxis_title="ISCED Education Field",
            yaxis_title="Education Level",
            height=300,
            margin=dict(t=60, l=100, r=20, b=120),
            font=dict(color="#1F2933")
        )
        
        return fig
        
    except Exception:
        return None


def create_geographic_footprint(profile_df):
    """Create geographic distribution map."""
    # ISO-2 to ISO-3 conversion
    ISO2_TO_ISO3 = {
        "be": "BEL", "bg": "BGR", "cz": "CZE", "dk": "DNK", "de": "DEU",
        "ee": "EST", "ie": "IRL", "el": "GRC", "gr": "GRC", "es": "ESP",
        "fr": "FRA", "hr": "HRV", "it": "ITA", "cy": "CYP", "lv": "LVA",
        "lt": "LTU", "lu": "LUX", "hu": "HUN", "mt": "MLT", "nl": "NLD",
        "at": "AUT", "pl": "POL", "pt": "PRT", "ro": "ROU", "si": "SVN",
        "sk": "SVK", "fi": "FIN", "se": "SWE", "no": "NOR", "ch": "CHE",
        "tr": "TUR"
    }
    
    country_counts = profile_df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'job_count']
    
    # Map country names to ISO codes
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
    
    country_counts['country_code_iso2'] = country_counts['country'].map(
        country_name_to_iso2)
    country_counts['country_code_iso3'] = country_counts['country_code_iso2'].map(
        ISO2_TO_ISO3)
    
    # Filter valid codes
    country_counts = country_counts[country_counts['country_code_iso3'].notna()]
    
    fig = px.choropleth(
        country_counts,
        locations="country_code_iso3",
        color="job_count",
        locationmode="ISO-3",
        scope="europe",
        color_continuous_scale="Blues",
        labels={"job_count": "Jobs"},
        title="Geographic Footprint",
        hover_name="country",
        hover_data={"country_code_iso3": False, "job_count": ":,"}
    )
    
    fig.update_layout(
        height=400,
        margin=dict(t=60, l=20, r=20, b=60),
        font=dict(color="#1F2933"),
        coloraxis_showscale=False
    )
    
    return fig


def create_isco_occupation_mix(profile_df):
    """Create ISCO occupation distribution."""
    isco_counts = profile_df['isco_3_label'].value_counts().head(7)
    total_jobs = len(profile_df)
    isco_percentages = (isco_counts / total_jobs * 100).round(1)
    
    fig = px.bar(
        x=isco_percentages.values,
        y=isco_percentages.index,
        orientation='h',
        title="ISCO Occupation Mix",
        labels={'x': 'Percentage of Jobs (%)', 'y': 'ISCO-3 Occupation'},
        color_discrete_sequence=['#2E86AB']
    )
    
    fig.update_layout(
        height=max(300, len(isco_counts) * 40),
        yaxis=dict(autorange="reversed"),
        margin=dict(t=60, l=40, r=20, b=80),
        font=dict(color="#1F2933"),
        showlegend=False
    )
    
    return fig


def create_greencomp_kpi(profile_df):
    """Create GreenComp integration KPI."""
    green_scores = profile_df['green_competences'].apply(
        lambda x: len(restore_list_safe(x)) if pd.notna(x) else 0
    )
    
    avg_score = green_scores.mean()
    max_possible = 5  # Assume max 5 green competences is high
    percentage = min((avg_score / max_possible) * 100, 100)
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "GreenComp Integration"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#27AE60"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "#F39C12"},
                {'range': [80, 100], 'color': "#27AE60"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        },
        number={'suffix': '%'}
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(t=30, l=20, r=20, b=20),
        font=dict(color="#1F2933", size=10)
    )
    
    return fig


def show_profiles_page(df):
    st.title("Transition Engineering Profiles")
    st.markdown("---")
    
    st.markdown("""
    **Transition Engineering Profiles** are multi-dimensional aggregations of jobs that combine:
    Skills (technical + GreenComp) • Education (ISCED) • Occupations (ISCO) • Geography • Transition intensity
    
    Each profile represents a distinct "character sheet" for engineers driving sustainability and digital transformation.
    """)
    
    # Profile selection
    st.markdown("### Select Profile to Analyze")
    
    # Classify jobs into profiles
    extractions_df['profile'] = extractions_df.apply(classify_job_into_profiles, axis=1)
    
    # Show profile distribution
    profile_counts = extractions_df['profile'].value_counts()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_profile = st.selectbox(
            "Choose a Transition Engineering Profile:",
            options=list(TRANSITION_PROFILES.keys()),
            index=0
        )
    with col2:
        st.metric(
            "Jobs in Profile", 
            f"{profile_counts.get(selected_profile, 0):,}",
            f"{(profile_counts.get(selected_profile, 0)/len(extractions_df)*100):.1f}% of total"
        )
    
    # Filter data for selected profile
    profile_df = extractions_df[extractions_df['profile'] == selected_profile]
    
    if profile_df.empty:
        st.warning(f"No jobs found for {selected_profile} profile.")
        return
    
    # Profile description
    st.markdown(f"**{selected_profile}**: {TRANSITION_PROFILES[selected_profile]['description']}")
    st.markdown("---")
    
    # Main profile visualization
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 1. Profile Radar Chart (signature plot)
        dimensions = calculate_profile_dimensions(profile_df)
        radar_fig = create_profile_radar_chart(selected_profile, dimensions)
        show_chart_with_card(radar_fig)
        
        # 2. Skill Stack Composition
        skill_fig = create_skill_stack_composition(profile_df)
        if skill_fig:
            show_chart_with_card(skill_fig)
    
    with col2:
        # 3. Education Pathway Matrix
        edu_fig = create_education_pathway_matrix(profile_df)
        if edu_fig:
            show_chart_with_card(edu_fig)
        else:
            st.info("Education pathway data not available for this profile")
        
        # 4. Geographic Footprint
        geo_fig = create_geographic_footprint(profile_df)
        show_chart_with_card(geo_fig)
    
    # Bottom row
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 5. ISCO Occupation Mix
        isco_fig = create_isco_occupation_mix(profile_df)
        show_chart_with_card(isco_fig)
    
    with col2:
        # 6. GreenComp Integration KPI
        kpi_fig = create_greencomp_kpi(profile_df)
        show_chart_with_card(kpi_fig)
        
        # Add explanation note
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 8px; border-radius: 5px; margin-top: 5px;">
        <small><strong>Computation:</strong> Average number of GreenComp competences per job in this profile, normalized to 0-100% scale (max 5 competences = 100%)</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Profile Statistics Summary
    st.markdown("---")
    st.markdown("### Profile Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_green = profile_df['green_competences'].apply(
            lambda x: len(restore_list_safe(x)) if pd.notna(x) else 0
        ).mean()
        st.metric("Avg. Green Competences", f"{avg_green:.1f}")
    
    with col2:
        avg_digital = profile_df['digital_competences'].apply(
            lambda x: len(restore_list_safe(x)) if pd.notna(x) else 0
        ).mean()
        st.metric("Avg. Digital Competences", f"{avg_digital:.1f}")
    
    with col3:
        countries = profile_df['country'].nunique()
        st.metric("Countries", countries)
    
    with col4:
        top_isco = profile_df['isco_3_label'].value_counts().index[0] if not profile_df.empty else "N/A"
        st.metric("Top ISCO", top_isco[:20] + "..." if len(top_isco) > 20 else top_isco)