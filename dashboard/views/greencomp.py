import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os
import plotly.graph_objects as go

# Add project root to Python path for deployment
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from greencomp import GREENCOMP_FRAMEWORK
from dashboard.helpers import restore_list_safe
from dashboard.style import show_chart_with_card, COLOR_PALETTE
from dashboard.utils import get_dataset_path, get_static_path

base_df = pd.read_csv(get_dataset_path('extractions.csv'))

def show_greencomp_page(df):

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("GreenComp European Competence Framework")
        st.caption("4 domains & 12 competences to assess environmental abilities")
    with col2:
        try:
            with open(get_static_path('GreenComp.pdf'), "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                st.download_button(
                    label="📄 Read Official Documentation",
                    data=pdf_bytes,
                    file_name="GreenComp.pdf",
                    mime="application/pdf"
                )
        except FileNotFoundError:
            st.warning("📄 Official documentation not found")
    
    st.markdown("---")
    
    domain_descriptions = {
        "Embodying sustainability values": "Nurturing values that support sustainability and driving actions accordingly.",
        "Embracing complexity in sustainability": "Approaching sustainability challenges and opportunities in all their complexity.",
        "Envisioning sustainable futures": "Envisioning alternative sustainable futures by imagining and developing alternative scenarios.",
        "Acting for sustainability": "Acting as change agents in personal, local, national and global contexts."
    }
    
    for domain, description in domain_descriptions.items():
        with st.expander(f"{domain}"):
            st.write(description)
            competences = [comp for dom, comps in GREENCOMP_FRAMEWORK if dom == domain for comp in comps]
            for comp in competences:
                st.write(f"• **{comp}**")

    st.markdown("---")

    col1, col2 = st.columns([4, 2])

    # ---------------
    # Radar Chart of DigComp competences
    # ---------------

    with col1:
        dig_df = base_df.copy()

        dig_df["green_competences"] = dig_df["green_competences"].apply(
            restore_list_safe
        )

        dig_exploded = dig_df.explode("green_competences")
        dig_exploded = dig_exploded[
            dig_exploded["green_competences"].notna()
            & (dig_exploded["green_competences"] != "")
        ]

        if dig_exploded.empty:
            st.info("No GreenComp competences explicitly identified in the dataset.")
        else:
            dig_counts = (
                dig_exploded["green_competences"]
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
                st.info("No GreenComp competences available for visualisation.")
            else:
                dig_counts["share"] = dig_counts["count"] / total * 100

                categories = dig_counts["competence"].tolist()
                values = dig_counts["share"].tolist()

                if len(categories) < 3:
                    st.info("Not enough GreenComp competences to build a radar chart.")
                else:
                    # Close the loop
                    categories = categories + [categories[0]]
                    values = values + [values[0]]

                    # Convert hex to rgba with transparency
                    primary_rgb = tuple(int(COLOR_PALETTE["primary_blue"][i:i+2], 16) for i in (1, 3, 5))
                    fill_color = f'rgba({primary_rgb[0]},{primary_rgb[1]},{primary_rgb[2]},0.3)'

                    fig = go.Figure()

                    fig.add_trace(
                        go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill="toself",
                            line=dict(color=COLOR_PALETTE["primary_blue"], width=2),
                            fillcolor=fill_color,
                            name="GreenComp"
                        )
                    )

                    fig.update_layout(
                        title="Relative Importance of GreenComp Competences in Job Postings",
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                ticksuffix="%",
                                range=[0, max(values) * 1.1]
                            )
                        ),
                        showlegend=False,
                        font=dict(color=COLOR_PALETTE["text_primary"]),
                        margin=dict(t=60, l=40, r=40, b=90),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )

                    show_chart_with_card(fig, height=None)
    with col2:
        # Calculate share of jobs mentioning GreenComp competences
        green_df = base_df.copy()
        
        # Process green competences
        green_df["green_competences"] = green_df["green_competences"].apply(
            restore_list_safe
        )
        
        # Check which jobs have at least one GreenComp competence
        green_df["has_greencomp"] = green_df["green_competences"].apply(
            lambda x: isinstance(x, list) and len(x) > 0 and any(
                comp.strip() for comp in x
            )
        )
        
        # Calculate percentage
        greencomp_share = green_df["has_greencomp"].mean() * 100
        
        # Create metric chart
        fig_metric = go.Figure(go.Indicator(
            mode="number",
            value=greencomp_share,
            number={"suffix": "%"},
            title={"text": "Jobs Explicitly Mentioning GreenComp Competences"}
        ))
        fig_metric.update_layout(
            margin=dict(t=35, l=20, r=20, b=15),
            font=dict(color=COLOR_PALETTE["text_primary"])
        )
        show_chart_with_card(fig_metric, height=170)

        # Distribution of GreenComp Integration Index
        green_df["green_competences"] = green_df["green_competences"].apply(
            lambda x: x if isinstance(x, list) else []
        )
        green_df["green_distinct_count"] = green_df["green_competences"].apply(
            lambda x: len(set(x))
        )
        green_df["green_total_mentions"] = green_df["green_competences"].apply(
            len
        )
        green_df["green_integration_index"] = (
            green_df["green_distinct_count"]
            * np.log(green_df["green_total_mentions"] + 1)
        )
        fig_dist = px.histogram(
            green_df,
            x="green_integration_index",
            nbins=40,
            title="Distribution of GreenComp Integration Index",
            labels={"green_integration_index": "GreenComp integration score"},
            template="plotly_white",
            color_discrete_sequence=[COLOR_PALETTE["primary_blue"]]
        )

        fig_dist.update_layout(
            bargap=0.05,
            margin=dict(t=60, l=40, r=40, b=90),
            font=dict(color=COLOR_PALETTE["text_primary"])
        )
        show_chart_with_card(fig_dist)

    isco_green = (
        green_df
        .groupby("isco_3_label")
        .agg(
            avg_green_index=("green_integration_index", "mean"),
            job_count=("job_id", "nunique")
        )
        .reset_index()
    )
    isco_green = isco_green[isco_green["job_count"] >= 30]
    isco_green = isco_green.sort_values("avg_green_index", ascending=False)
    fig_isco = px.bar(
        isco_green,
        x="avg_green_index",
        y="isco_3_label",
        orientation="h",
        title="Average GreenComp Integration Index by ISCO-3 Occupation",
        labels={
            "avg_green_index": "Average GreenComp integration score",
            "isco_3_label": "ISCO-3 occupation"
        },
        template="plotly_white",
        color="avg_green_index",
        color_continuous_scale="Blues"
    )

    fig_isco.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(t=60, l=40, r=40, b=90),
        font=dict(color=COLOR_PALETTE["text_primary"]),
        coloraxis_showscale=False
    )
    show_chart_with_card(fig_isco)



