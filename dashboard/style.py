import streamlit as st

# -----------------
# CARD WRAPPER FOR CHARTS
# -----------------

def show_chart_with_card(fig, height=None):
    # Only set height if explicitly provided, otherwise let it auto-fit
    if height is not None:
        fig.update_layout(height=height)
    else:
        # Let plotly auto-size based on content
        fig.update_layout(autosize=True)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    with st.container():
        st.plotly_chart(fig, use_container_width=True, theme=None)