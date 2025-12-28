import streamlit as st
import pandas as pd
from digcomp import DIGCOMP_FRAMEWORK
from dashboard.helpers import restore_list_safe
from dashboard.style import show_chart_with_card
from analysis.digital_tools import display_tools_analysis
import plotly.graph_objects as go

# Load datasets
eur_jobs_path = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/datasets/european_jobs.csv'
eur_jobs = pd.read_csv(eur_jobs_path)
path = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/datasets/extractions.csv'
base_df = pd.read_csv(path)

def show_digcomp_page(df):
        
    # Page title and documentation link
    col1, col2 = st.columns([3, 1])
    with col1: 
        st.title("DigComp European Competence Framework")
        st.caption("5 domains & 21 competences to assess digital abilities")
    with col2:
        try:
            with open('/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/dashboard/static/DigComp.pdf', "rb") as pdf_file:
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

    col1, col2 = st.columns([3, 2])

    # ---------------
    # Radar Chart of DigComp competences
    # ---------------

    with col1:
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

                    fig.add_trace(
                        go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill="toself",
                            line=dict(color="#3B6C8E", width=2),
                            fillcolor="rgba(59,108,142,0.3)",
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
                        font=dict(color="#1F2933"),
                        margin=dict(t=60, l=40, r=40, b=90),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )

                    show_chart_with_card(fig, height=None)
    
    with col2:
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
        
        # Create metric chart
        fig_metric = go.Figure(go.Indicator(
            mode="number",
            value=digcomp_share,
            number={"suffix": "%"},
            title={"text": "Jobs Explicitly Mentioning DigComp Competences"}
        ))
        fig_metric.update_layout(
            margin=dict(t=35, l=20, r=20, b=15),
            font=dict(color="#1F2933")
        )
        show_chart_with_card(fig_metric, height=170)

    # Display digital tools analysis
    display_tools_analysis(eur_jobs)

