import streamlit as st
import pandas as pd
from greencomp import GREENCOMP_FRAMEWORK
from dashboard.helpers import restore_list_safe
from dashboard.style import show_chart_with_card
import plotly.graph_objects as go

path = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/datasets/extractions.csv'
base_df = pd.read_csv(path)

def show_greencomp_page(df):

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("GreenComp European Competence Framework")
        st.caption("4 domains & 12 competences to assess environmental abilities")
    with col2:
        try:
            with open('/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/dashboard/static/GreenComp.pdf', "rb") as pdf_file:
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

    col1, col2, col3 = st.columns([3, 2, 2])

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

                    fig = go.Figure()

                    fig.add_trace(
                        go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill="toself",
                            line=dict(color="#3B6C8E", width=2),
                            fillcolor="rgba(59,108,142,0.3)",
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
                        font=dict(color="#1F2933"),
                        margin=dict(t=60, l=40, r=40, b=40),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )

                    show_chart_with_card(fig, height=None)
    with col2:
        pass
    with col3:
        pass

