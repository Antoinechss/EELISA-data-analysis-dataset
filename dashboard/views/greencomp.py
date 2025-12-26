import streamlit as st
import pandas as pd
import base64
from greencomp import GREENCOMP_FRAMEWORK

def show_greencomp_page(df):
    """Display the GreenComp overview page"""
    
    st.title("GreenComp European Competence Framework")
    st.caption("4 domains & 12 competences to assess environmental abilities")
    
    # Add PDF download link
    col1, col2 = st.columns([3, 1])
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
