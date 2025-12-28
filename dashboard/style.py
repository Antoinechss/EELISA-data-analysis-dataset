import streamlit as st

# -----------------
# CARD WRAPPER FOR CHARTS
# -----------------

def show_chart_with_card(fig, height=None):
    if height is not None:
        fig.update_layout(height=height)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    with st.container():
        st.plotly_chart(fig, use_container_width=True, theme=None)