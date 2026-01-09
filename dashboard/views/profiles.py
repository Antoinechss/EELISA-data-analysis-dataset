"""
Transition Engineering Profiles Interface

This module provides the Streamlit interface for displaying discovered
engineering profiles through unsupervised clustering. It focuses on
clean visualization and insight delivery without ML complexity.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys
import os

# Add analysis directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import centralized styling
from style import COLOR_PALETTE, apply_chart_style, show_chart_with_card

try:
    from clustering import run_clustering, characterize_clusters, get_cluster_summary_stats
except ImportError as e:
    st.error(f"Could not import clustering module: {e}")
    run_clustering = None
    characterize_clusters = None
    get_cluster_summary_stats = None


def create_cluster_projection_chart(df_clustered, profiles):
    """Create 2D projection of discovered profiles."""
    
    # Map cluster IDs to profile names
    df_plot = df_clustered.copy()
    df_plot['Profile'] = df_plot['profile_cluster'].map(
        lambda x: profiles.get(x, {}).get('name', f'Profile {x}')
    )
    
    fig = px.scatter(
        df_plot,
        x='pca_x', 
        y='pca_y',
        color='Profile',
        title="Engineering Profile Landscape",
        labels={'pca_x': 'Technical Specialization', 'pca_y': 'Systems Integration'},
        hover_data={
            'country': True,
            'isco_3_label': True,
            'education_level': True,
            'pca_x': False,
            'pca_y': False
        },
        height=500
    )
    
    fig.update_traces(
        marker=dict(size=6, opacity=0.7),
        hovertemplate="<b>%{customdata[0]}</b><br>" +
                     "Occupation: %{customdata[1]}<br>" +
                     "Education: %{customdata[2]}<br>" +
                     "Profile: %{fullData.name}<extra></extra>"
    )
    
    fig.update_layout(
        font=dict(color=COLOR_PALETTE['text_primary']),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig


def create_profile_radar_chart(cluster_stats):
    """Create radar chart for profile characteristics."""
    
    metrics = cluster_stats.get('skill_metrics', {})
    transition = cluster_stats.get('transition_indicators', {})
    
    categories = [
        'Technical Skills',
        'Digital Competences', 
        'Green Focus',
        'Knowledge Breadth',
        'Sustainability Adoption',
        'Digital Intensity'
    ]
    
    values = [
        min(metrics.get('avg_hard_skills', 0) / 15 * 100, 100),  # Normalize to 0-100
        min(metrics.get('avg_digital_competences', 0) / 6 * 100, 100),
        min(metrics.get('avg_green_competences', 0) / 3 * 100, 100),
        min(metrics.get('avg_knowledge_domains', 0) / 8 * 100, 100),
        transition.get('sustainability_adoption', 0),
        transition.get('high_digital_intensity', 0)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Profile Signature',
        line_color=COLOR_PALETTE['positive_green'],
        fillcolor='rgba(16, 185, 129, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%'
            )
        ),
        title="Profile Characteristics",
        height=400,
        font=dict(color=COLOR_PALETTE['text_primary']),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig


def create_occupation_distribution_chart(cluster_stats):
    """Create top occupations chart."""
    
    isco_data = cluster_stats.get('isco_distribution', {})
    if not isco_data:
        return None
        
    # Take top 6 occupations and truncate names
    isco_items = list(isco_data.items())[:6]
    df_isco = pd.DataFrame(isco_items, columns=['Occupation', 'Count'])
    df_isco['Occupation_Short'] = df_isco['Occupation'].apply(
        lambda x: x[:30] + "..." if len(x) > 30 else x
    )
    
    fig = px.bar(
        df_isco,
        x='Count',
        y='Occupation_Short',
        orientation='h',
        title="Primary Occupations",
        color_discrete_sequence=[COLOR_PALETTE['tertiary_orange']]
    )
    
    fig.update_layout(
        height=max(250, len(df_isco) * 45),
        font=dict(color=COLOR_PALETTE['text_primary']),
        showlegend=False,
        yaxis=dict(autorange="reversed"),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig


def create_geographic_distribution_chart(cluster_stats):
    """Create geographic distribution map."""
    
    country_data = cluster_stats.get('country_distribution', {})
    if not country_data:
        return None
    
    # Create country mapping for European countries
    country_code_mapping = {
        'Germany': 'DEU', 'France': 'FRA', 'Switzerland': 'CHE', 'Poland': 'POL',
        'Italy': 'ITA', 'Latvia': 'LVA', 'Croatia': 'HRV', 'Belgium': 'BEL',
        'Sweden': 'SWE', 'Spain': 'ESP', 'Netherlands': 'NLD', 'Turkey': 'TUR',
        'Austria': 'AUT', 'Portugal': 'PRT', 'Czech Republic': 'CZE',
        'Denmark': 'DNK', 'Finland': 'FIN', 'Greece': 'GRC', 'Hungary': 'HUN',
        'Ireland': 'IRL', 'Luxembourg': 'LUX', 'Slovakia': 'SVK', 'Slovenia': 'SVN',
        'Estonia': 'EST', 'Lithuania': 'LTU', 'Malta': 'MLT', 'Cyprus': 'CYP',
        'Bulgaria': 'BGR', 'Romania': 'ROU', 'Norway': 'NOR', 'Iceland': 'ISL'
    }
    
    # Prepare data for choropleth
    df_geo = pd.DataFrame([
        {
            'country': country,
            'job_count': count,
            'country_code': country_code_mapping.get(country, country[:3].upper())
        }
        for country, count in country_data.items()
    ])
    
    # Create choropleth map
    fig = px.choropleth(
        df_geo,
        locations='country_code',
        color='job_count',
        hover_name='country',
        color_continuous_scale="Blues",
        labels={"job_count": "Jobs"},
        title="Geographic Distribution"
    )
    
    fig.update_geos(
        scope="europe",
        showframe=False,
        showcoastlines=True,
        projection_type='equirectangular'
    )
    
    fig.update_layout(
        height=400,
        font=dict(color=COLOR_PALETTE['text_primary']),
        coloraxis_showscale=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig


def show_cluster_overview_metrics(df_clustered, profiles):
    """Show overview metrics for all discovered clusters."""
    
    st.markdown("### Profile Discovery Overview")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Profiles Discovered", len(profiles))
    
    with col2:
        total_jobs = len(df_clustered)
        st.metric("Total Jobs Analyzed", f"{total_jobs:,}")
    
    with col3:
        avg_cluster_size = len(df_clustered) / len(profiles)
        st.metric("Average Profile Size", f"{avg_cluster_size:.0f}")
    
    with col4:
        largest_profile = max(profiles.values(), key=lambda x: x['size'])
        st.metric("Largest Profile", largest_profile['name'])


def show_profiles_page(df):
    """Main interface for Transition Engineering Profiles discovery."""
    
    st.title("Transition Engineering Profiles")
    st.markdown("---")
    
    # Check if clustering functions are available
    if run_clustering is None:
        st.error("Clustering functionality is not available. Please check the clustering module.")
        st.info("The clustering module requires scikit-learn. Please ensure it's installed.")
        return
    
    st.markdown("""
    This section uses clustering analysis to automatically group similar engineering jobs into distinct profiles.
    The algorithm identifies patterns in skills, competencies, and job characteristics to discover different 
    types of engineering roles across European markets.
    """)
    
    # Initialize session state for clustering
    if 'clustering_done' not in st.session_state:
        st.session_state.clustering_done = False
        st.session_state.df_clustered = None
        st.session_state.profiles = None
    
    # Clustering execution
    if not st.session_state.clustering_done:
        with st.spinner("Analyzing job patterns and discovering profiles..."):
            try:
                df_clustered, cluster_info = run_clustering(df)
                profiles = characterize_clusters(df_clustered, cluster_info)
                
                st.session_state.df_clustered = df_clustered
                st.session_state.profiles = profiles
                st.session_state.cluster_info = cluster_info
                st.session_state.clustering_done = True
                
                st.success(f"Successfully discovered {len(profiles)} distinct engineering profiles!")
                
            except Exception as e:
                st.error(f"Error during profile discovery: {str(e)}")
                return
    
    df_clustered = st.session_state.df_clustered
    profiles = st.session_state.profiles
    
    if df_clustered is None or profiles is None:
        st.error("Profile discovery failed. Please refresh the page.")
        return
    
    # Overview metrics
    show_cluster_overview_metrics(df_clustered, profiles)
    
    st.markdown("---")
    
    # Profile landscape visualization
    st.markdown("### Profile Landscape")
    st.markdown("Explore how different engineering profiles are distributed across the technical-systems space:")
    
    projection_fig = create_cluster_projection_chart(df_clustered, profiles)
    show_chart_with_card(projection_fig)
    
    st.markdown("---")
    
    # Profile selector and detailed view
    st.markdown("### Detailed Profile Analysis")
    
    profile_options = {
        profiles[cluster_id]['name']: cluster_id 
        for cluster_id in sorted(profiles.keys())
    }
    
    selected_profile_name = st.selectbox(
        "Select a profile for detailed analysis:",
        options=list(profile_options.keys()),
        key="profile_selector"
    )
    
    selected_cluster_id = profile_options[selected_profile_name]
    selected_profile = profiles[selected_cluster_id]
    
    # Profile header
    st.markdown(f"#### {selected_profile['name']}")
    st.markdown(f"*{selected_profile['description']}*")
    
    # Get detailed stats for selected profile
    cluster_stats = get_cluster_summary_stats(df_clustered, selected_cluster_id)
    
    # Detailed visualizations
    st.markdown("##### Profile Characteristics")
    
    # Top row: Radar chart (full width)
    radar_fig = create_profile_radar_chart(cluster_stats)
    show_chart_with_card(radar_fig)
    
    # Bottom row: Occupations and geography
    col1, col2 = st.columns([1, 1])
    
    with col1:
        occ_fig = create_occupation_distribution_chart(cluster_stats)
        if occ_fig:
            show_chart_with_card(occ_fig)
        else:
            st.info("Occupation data not available")
    
    with col2:
        geo_fig = create_geographic_distribution_chart(cluster_stats)
        if geo_fig:
            show_chart_with_card(geo_fig)
        else:
            st.info("Geographic data not available")
    
    # Profile insights summary
    st.markdown("##### Key Insights")
    
    characteristics = selected_profile.get('characteristics', {})
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown("**Skills & Competencies:**")
        st.markdown(f"- Average technical skills: {characteristics.get('avg_total_skills', 0):.1f}")
        st.markdown(f"- Digital competencies: {characteristics.get('avg_digital_competences', 0):.1f}")
        st.markdown(f"- Green competencies: {characteristics.get('avg_green_competences', 0):.1f}")
    
    with insights_col2:
        st.markdown("**Geographic & Occupational Focus:**")
        top_countries = characteristics.get('top_countries', [])
        if top_countries:
            st.markdown(f"- Primary markets: {', '.join(top_countries[:3])}")
        primary_occ = characteristics.get('primary_occupation', 'N/A')
        if len(primary_occ) > 50:
            primary_occ = primary_occ[:50] + "..."
        st.markdown(f"- Main occupation: {primary_occ}")
    
    # Reset clustering button
    st.markdown("---")
    if st.button("Rediscover Profiles", help="Re-run the clustering analysis"):
        st.session_state.clustering_done = False
        st.rerun()
