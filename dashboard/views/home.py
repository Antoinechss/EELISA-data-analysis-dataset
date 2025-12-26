import streamlit as st
from PIL import Image

def show_home_page():

    # =======================
    # HEADER WITH LOGOS
    # =======================
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        try:
            eelisa_logo = Image.open(
                "/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/dashboard/static/eelisa_logo.png"
            )
            st.image(eelisa_logo, width=140)
        except:
            st.write("EELISA")

    with col2:
        st.markdown(
            """
            <h1 style="text-align: center; margin-bottom: 0;">
            Reporting of the European Technical Job Market
            </h1>
            <h4 style="text-align: center; margin-top: 0;">
            EELISA Data Science Mission
            </h4>
            <p style="text-align: center; font-size: 0.9em;">
            Provided by Ponts Études Projets<br>
            Antoine Chosson – École des Ponts ParisTech (IMI027)
            </p>
            """,
            unsafe_allow_html=True
        )

    with col3:
        try:
            pep_logo = Image.open(
                "/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/dashboard/static/PEP_logo.png"
            )
            st.image(pep_logo, width=140)
        except:
            st.write("PEP")

    st.markdown("---")

    # =======================
    # CONTEXT & OBJECTIVES
    # =======================

    st.markdown(
        """
        ### Context and objectives

        This dashboard was developed within the framework of the **EELISA Data Science Mission** to support the analysis of 
        the European technical job market through large-scale job posting data. The project aims to leverage data science 
        methods to better understand how education requirements, skills, and competences are articulated in job offers 
        across countries and occupational fields.

        A central objective of this work is to contribute to the identification and characterisation of **emerging professional 
        profiles** in the European labour market, with particular attention to the integration of **digital** and 
        **sustainability-related competences**. By aligning job market signals with European competence frameworks, the 
        dashboard supports evidence-based reflection on skills development, training pathways, and workforce transformation.
        """
    )
