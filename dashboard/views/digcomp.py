import streamlit as st
import pandas as pd
import sys
import os
import plotly.graph_objects as go

# Add project root to Python path for deployment
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from digcomp import DIGCOMP_FRAMEWORK
from dashboard.helpers import restore_list_safe
from dashboard.style import show_chart_with_card, COLOR_PALETTE
from analysis.digital_tools import display_tools_analysis
from dashboard.utils import get_dataset_path, get_static_path

# Load datasets
eur_jobs = pd.read_csv(get_dataset_path('european_jobs.csv'))
base_df = pd.read_csv(get_dataset_path('extractions.csv'))

def show_digcomp_page(df):
        
    # Page title and documentation link
    col1, col2 = st.columns([3, 1])
    with col1: 
        st.title("DigComp European Competence Framework")
        st.caption("5 domains & 21 competences to assess digital abilities")
    with col2:
        try:
            with open(get_static_path('DigComp.pdf'), "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                st.download_button(
                    label="📄 Read Official Documentation",
                    data=pdf_bytes,
                    file_name="DigComp.pdf",
                    mime="application/pdf"
                )
        except FileNotFoundError:
            st.warning("📄 Official documentation not found")
    
    st.markdown("---")

    # Domain descriptions
    domain_descriptions = {
        "Information and digital literacy": "Articulate information needs, locate and retrieve digital data, information and content.",
        "Communication and collaboration": "Communicate in digital environments, share resources through online tools, connect and collaborate with others.",
        "Digital content creation": "Create and edit digital content in different formats, express oneself through digital means.",
        "Safety": "Protect devices, personal data, privacy and digital identity, use technology safely and sustainably.",
        "Problem-solving": "Solve problems and make informed decisions about the most appropriate digital tools according to the purpose or need."
    }
    
    # Display domain descriptions and competences
    for domain, description in domain_descriptions.items():
        with st.expander(f"{domain}"):
            st.write(description)
            competences = [comp for dom, comps in DIGCOMP_FRAMEWORK if dom == domain for comp in comps]
            for comp in competences:
                st.write(f"• **{comp}**")
    
    st.markdown("---")

    # ---------------
    # Radar Chart of DigComp competences
    # ---------------

    dig_df = base_df.copy()

    # Restore list structure for competences
    dig_df["digital_competences"] = dig_df["digital_competences"].apply(
        restore_list_safe
    )

    # Explode competences for individual analysis
    dig_exploded = dig_df.explode("digital_competences")
    dig_exploded = dig_exploded[
        dig_exploded["digital_competences"].notna()
        & (dig_exploded["digital_competences"] != "")
    ]

    if dig_exploded.empty:
        st.info("No DigComp competences explicitly identified in the dataset.")
    else:
        dig_counts = (
            dig_exploded["digital_competences"]
            .value_counts()
            .reset_index()
        )
        TOP_N = 8

        dig_counts = (
            dig_counts
            .sort_values("count", ascending=False)
            .head(TOP_N)
        )

        dig_counts.columns = ["competence", "count"]

        total = dig_counts["count"].sum()
        if total == 0:
            st.info("No DigComp competences available for visualisation.")
        else:
            dig_counts["share"] = dig_counts["count"] / total * 100

            categories = dig_counts["competence"].tolist()
            values = dig_counts["share"].tolist()

            if len(categories) < 3:
                st.info("Not enough DigComp competences to build a radar chart.")
            else:
                # Close the loop for radar chart
                categories = categories + [categories[0]]
                values = values + [values[0]]

                fig = go.Figure()

                # Convert hex to rgba with transparency
                primary_rgb = tuple(int(COLOR_PALETTE["primary_blue"][i:i+2], 16) for i in (1, 3, 5))
                fill_color = f'rgba({primary_rgb[0]},{primary_rgb[1]},{primary_rgb[2]},0.3)'

                fig.add_trace(
                    go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill="toself",
                        line=dict(color=COLOR_PALETTE["primary_blue"], width=2),
                        fillcolor=fill_color,
                        name="DigComp"
                    )
                )

                fig.update_layout(
                    title="Relative Importance of DigComp Competences in Job Postings",
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            ticksuffix="%",
                            range=[0, max(values) * 1.1]
                        )
                    ),
                    showlegend=False,
                    font=dict(color=COLOR_PALETTE["text_primary"]),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=500
                )

                show_chart_with_card(fig, height=None)
    
    # Calculate share of jobs mentioning DigComp competences
    dig_df = base_df.copy()
    
    # Process digital competences
    dig_df["digital_competences"] = dig_df["digital_competences"].apply(restore_list_safe)
    
    # Check which jobs have at least one DigComp competence
    dig_df["has_digcomp"] = dig_df["digital_competences"].apply(
        lambda x: isinstance(x, list) and len(x) > 0 and any(comp.strip() for comp in x)
    )
    
    # Calculate percentage
    digcomp_share = dig_df["has_digcomp"].mean() * 100
    
    # Simple metric for DigComp competences
    st.metric(
        label="Jobs Explicitly Mentioning DigComp Competences",
        value=f"{digcomp_share:.1f}%"
    )

    # Display digital tools analysis
    display_tools_analysis(eur_jobs)

