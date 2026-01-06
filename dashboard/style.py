"""
Centralized styling system for the European Job Market Dashboard.

This module provides a consistent, professional styling system following
a clean, card-based design with muted colors and excellent readability.
"""

import streamlit as st
import plotly.graph_objects as go

# =============================================================================
# COLOR PALETTE (LOCKED - DO NOT MODIFY)
# =============================================================================

COLOR_PALETTE = {
    # Background colors
    'page_background': '#f8f9fa',      # Very light neutral gray
    'card_background': '#ffffff',       # Pure white for cards
    'border_light': '#e5e7eb',         # Very light gray borders
    'border_medium': '#d1d5db',        # Medium gray borders
    
    # Text colors
    'text_primary': '#1f2937',         # Near-black dark gray
    'text_secondary': '#6b7280',       # Medium gray
    'text_disabled': '#9ca3af',        # Light gray for metadata
    
    # Chart colors (muted, professional)
    'primary_blue': '#3b82f6',         # Blue (primary)
    'secondary_red': '#ef4444',        # Red (secondary/negative)
    'tertiary_orange': '#f97316',      # Orange (tertiary/warning) 
    'positive_green': '#10b981',       # Green (positive/improvement)
    
    # Additional chart colors for variety
    'chart_purple': '#8b5cf6',
    'chart_teal': '#14b8a6',
    'chart_pink': '#ec4899',
    'chart_indigo': '#6366f1',
}

# Chart color sequence for consistent multi-series charts
CHART_COLOR_SEQUENCE = [
    COLOR_PALETTE['primary_blue'],
    COLOR_PALETTE['secondary_red'],
    COLOR_PALETTE['tertiary_orange'],
    COLOR_PALETTE['positive_green'],
    COLOR_PALETTE['chart_purple'],
    COLOR_PALETTE['chart_teal'],
    COLOR_PALETTE['chart_pink'],
    COLOR_PALETTE['chart_indigo'],
]

# =============================================================================
# TYPOGRAPHY
# =============================================================================

FONT_SIZES = {
    'title': '1.875rem',          # 30px - Page titles
    'section_title': '1.5rem',    # 24px - Section titles  
    'card_title': '1.25rem',      # 20px - Card titles
    'body': '1rem',               # 16px - Body text
    'small': '0.875rem',          # 14px - Small text, metadata
    'kpi_value': '2.25rem',       # 36px - Large KPI numbers
    'kpi_label': '0.875rem',      # 14px - KPI labels
}

FONT_WEIGHTS = {
    'light': 300,
    'regular': 400,
    'medium': 500,
    'semibold': 600,
    'bold': 700,
}

# =============================================================================
# GLOBAL STYLING
# =============================================================================

def apply_global_style():
    """Apply global CSS styling to the Streamlit app."""
    st.markdown(f"""
    <style>
    /* Page background */
    .main .block-container {{
        background-color: {COLOR_PALETTE['page_background']};
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    
    /* Hide Streamlit header and footer */
    header[data-testid="stHeader"] {{
        display: none;
    }}
    
    /* Card styling for Plotly charts */
    div[data-testid="stPlotlyChart"] {{
        background-color: {COLOR_PALETTE['card_background']} !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        margin-bottom: 1.5rem !important;
        border: 1px solid {COLOR_PALETTE['border_light']} !important;
    }}
    
    /* Metric styling */
    div[data-testid="metric-container"] {{
        background-color: {COLOR_PALETTE['card_background']};
        border: 1px solid {COLOR_PALETTE['border_light']};
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    /* Section titles */
    h1 {{
        color: {COLOR_PALETTE['text_primary']} !important;
        font-weight: {FONT_WEIGHTS['semibold']} !important;
        font-size: {FONT_SIZES['title']} !important;
        margin-bottom: 1rem !important;
    }}
    
    h2 {{
        color: {COLOR_PALETTE['text_primary']} !important;
        font-weight: {FONT_WEIGHTS['medium']} !important;
        font-size: {FONT_SIZES['section_title']} !important;
        margin-bottom: 0.75rem !important;
    }}
    
    h3 {{
        color: {COLOR_PALETTE['text_primary']} !important;
        font-weight: {FONT_WEIGHTS['medium']} !important;
        font-size: {FONT_SIZES['card_title']} !important;
        margin-bottom: 0.5rem !important;
    }}
    
    /* Body text */
    p, div[data-testid="stMarkdownContainer"] {{
        color: {COLOR_PALETTE['text_secondary']} !important;
        font-size: {FONT_SIZES['body']} !important;
        line-height: 1.6 !important;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background-color: {COLOR_PALETTE['card_background']} !important;
        border-right: 1px solid {COLOR_PALETTE['border_light']} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# CHART STYLING
# =============================================================================

def get_default_layout(**kwargs):
    """Get default layout configuration for Plotly charts."""
    default_layout = {
        'paper_bgcolor': COLOR_PALETTE['card_background'],
        'plot_bgcolor': COLOR_PALETTE['card_background'],
        'font': {
            'family': 'system-ui, -apple-system, sans-serif',
            'size': 12,
            'color': COLOR_PALETTE['text_primary']
        },
        'title': {
            'font': {
                'size': 16,
                'color': COLOR_PALETTE['text_primary'],
                'family': 'system-ui, -apple-system, sans-serif'
            },
            'x': 0.5,
            'xanchor': 'center'
        },
        'xaxis': {
            'gridcolor': COLOR_PALETTE['border_light'],
            'linecolor': COLOR_PALETTE['border_medium'],
            'tickfont': {'color': COLOR_PALETTE['text_secondary']},
            'title': {'font': {'color': COLOR_PALETTE['text_primary']}}
        },
        'yaxis': {
            'gridcolor': COLOR_PALETTE['border_light'],
            'linecolor': COLOR_PALETTE['border_medium'],
            'tickfont': {'color': COLOR_PALETTE['text_secondary']},
            'title': {'font': {'color': COLOR_PALETTE['text_primary']}}
        },
        'legend': {
            'font': {'color': COLOR_PALETTE['text_primary']},
            'bgcolor': 'rgba(255, 255, 255, 0.8)',
            'bordercolor': COLOR_PALETTE['border_light'],
            'borderwidth': 1
        },
        'margin': {'t': 60, 'l': 60, 'r': 20, 'b': 60}
    }
    
    # Override with any provided kwargs
    default_layout.update(kwargs)
    return default_layout

def apply_chart_style(fig, **layout_kwargs):
    """Apply consistent styling to a Plotly figure."""
    layout = get_default_layout(**layout_kwargs)
    fig.update_layout(layout)
    return fig

def create_styled_bar_chart(data, x, y, title, color=None, orientation='v'):
    """Create a consistently styled bar chart."""
    import plotly.express as px
    
    fig = px.bar(
        data, x=x, y=y, 
        title=title,
        orientation=orientation,
        color_discrete_sequence=[color or COLOR_PALETTE['primary_blue']]
    )
    
    return apply_chart_style(fig)

def create_styled_line_chart(data, x, y, title, color=None):
    """Create a consistently styled line chart."""
    import plotly.express as px
    
    fig = px.line(
        data, x=x, y=y,
        title=title,
        color_discrete_sequence=[color or COLOR_PALETTE['primary_blue']]
    )
    
    return apply_chart_style(fig)

def create_styled_scatter_chart(data, x, y, title, color=None):
    """Create a consistently styled scatter chart."""
    import plotly.express as px
    
    fig = px.scatter(
        data, x=x, y=y,
        title=title,
        color_discrete_sequence=[color or COLOR_PALETTE['primary_blue']]
    )
    
    return apply_chart_style(fig)

# =============================================================================
# COMPONENT HELPERS
# =============================================================================

def show_chart_with_card(fig, height=None):
    """Display a Plotly chart within a styled card."""
    if height is not None:
        fig.update_layout(height=height)
    
    # Apply consistent styling
    fig = apply_chart_style(fig)
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True, theme=None)

def create_metric_card(label, value, delta=None, help_text=None):
    """Create a styled metric card."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(
            label=label,
            value=value,
            delta=delta,
            help=help_text
        )

def show_section_header(title, description=None):
    """Display a consistently styled section header."""
    st.markdown(f"## {title}")
    if description:
        st.markdown(f"*{description}*")
    st.markdown("---")

def create_info_card(title, content):
    """Create an informational card with consistent styling."""
    st.markdown(f"""
    <div style="
        background-color: {COLOR_PALETTE['card_background']};
        border: 1px solid {COLOR_PALETTE['border_light']};
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    ">
        <h4 style="color: {COLOR_PALETTE['text_primary']}; margin-bottom: 0.75rem;">{title}</h4>
        <p style="color: {COLOR_PALETTE['text_secondary']}; margin: 0;">{content}</p>
    </div>
    """, unsafe_allow_html=True)