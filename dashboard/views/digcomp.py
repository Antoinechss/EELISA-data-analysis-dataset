import streamlit as st
import pandas as pd
from digcomp import DIGCOMP_FRAMEWORK

def show_digcomp_page(df):
        
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

    domain_descriptions = {
        "Information and digital literacy": "Articulate information needs, locate and retrieve digital data, information and content.",
        "Communication and collaboration": "Communicate in digital environments, share resources through online tools, connect and collaborate with others.",
        "Digital content creation": "Create and edit digital content in different formats, express oneself through digital means.",
        "Safety": "Protect devices, personal data, privacy and digital identity, use technology safely and sustainably.",
        "Problem-solving": "Solve problems and make informed decisions about the most appropriate digital tools according to the purpose or need."
    }
    
    for domain, description in domain_descriptions.items():
        with st.expander(f"{domain}"):
            st.write(description)
            competences = [comp for dom, comps in DIGCOMP_FRAMEWORK if dom == domain for comp in comps]
            for comp in competences:
                st.write(f"• **{comp}**")
    
    st.markdown("---")
