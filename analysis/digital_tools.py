import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from collections import Counter
from itertools import chain
from dashboard.style import show_chart_with_card

# =======================
# COLOR PALETTE
# =======================

PRIMARY = "#648fa9"
SECONDARY = "#386c8b"
ACCENT = "#fe5758"
SOFT_BG = "#f2d9bc"

CUSTOM_CONTINUOUS_SCALE = [
    [0.0, SOFT_BG],
    [0.4, PRIMARY],
    [0.7, SECONDARY],
    [1.0, ACCENT],
]

# =======================
# TECH CONTEXT DEFINITIONS
# =======================

TECH_CONTEXT_WORDS = [
    "programming", "language", "development", "developer", "coding",
    "data", "analysis", "analytics", "statistical", "modeling",
    "software", "script", "package", "library", "framework"
]

NEGATIVE_CONTEXT = {
    "r": ["are ", "role ", "grade ", "level ", "team r"],
    "c": ["vitamin c", "c level", "see ", "chapter c"],
    "go": ["go to", "go live", "go ahead"],
    "aws": ["amazon warehouse", "amazon delivery"]
}

# =======================
# TECH TOOLS DICTIONARY
# =======================

TECH_TOOLS = {
    "sql": ["sql", "mysql", "postgresql", "sqlite"],
    "python": ["python", "pandas", "numpy"],
    "excel": ["excel", "microsoft excel"],
    "r": ["r", "rstudio"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "power_bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "docker": ["docker"],
    "git": ["git"],
}

# =======================
# TOOL CATEGORIES
# =======================

CATEGORIES = {
    "Programming Languages": ["python", "java", "javascript", "r"],
    "Data & Analytics": ["sql", "python", "r", "power_bi", "tableau"],
    "Cloud & DevOps": ["aws", "azure", "docker"],
    "Office & Productivity": ["excel"],
    "Version Control": ["git"],
}

# =======================
# EXTRACTION LOGIC
# =======================

AMBIGUOUS_TOOLS = {"r", "c", "go", "aws"}
SAFE_TOOLS = set(TECH_TOOLS.keys()) - AMBIGUOUS_TOOLS


def has_technical_context(text):
    return any(kw in text for kw in TECH_CONTEXT_WORDS)


def contains_negative_context(text, negatives):
    return any(neg in text for neg in negatives)


def extract_tech_tools(text):
    text = str(text).lower()
    found = {}

    for tool, variants in TECH_TOOLS.items():
        for v in variants:
            pattern = r"\b" + re.escape(v) + r"\b"
            for match in re.finditer(pattern, text):
                start, end = match.span()
                context = text[max(0, start - 50): min(len(text), end + 50)]

                if tool in SAFE_TOOLS:
                    found[tool] = "high"
                    break

                if tool in AMBIGUOUS_TOOLS:
                    if contains_negative_context(context, NEGATIVE_CONTEXT.get(tool, [])):
                        continue
                    if has_technical_context(context):
                        found[tool] = "medium"
                        break
        if tool in found:
            break

    return found

# =======================
# STREAMLIT PAGE
# =======================

def display_tools_analysis(df):

    st.title("Digital Tools Analysis")
    st.caption("Context-aware extraction of technical tools from job descriptions")

    col1, col2 = st.columns([4, 2])
    with col1: 
        df["tech_tools"] = df["full_description"].apply(extract_tech_tools)
        df["filtered_tools"] = df["tech_tools"].apply(lambda d: list(d.keys()))

        tool_counts = Counter(chain.from_iterable(df["filtered_tools"]))

        if not tool_counts:
            st.warning("No tools detected.")
            return

        top_tools = tool_counts.most_common(30)
        treemap_df = pd.DataFrame(top_tools, columns=["tool", "count"])

        # =======================
        # TREEMAP
        # =======================

        fig = go.Figure(go.Treemap(
            labels=[f"{t}<br>{c} jobs" for t, c in top_tools],
            values=treemap_df["count"],
            parents=[""] * len(treemap_df),
            root=dict(color="white"),
            marker=dict(
                colors=treemap_df["count"],
                colorscale=CUSTOM_CONTINUOUS_SCALE,
                line=dict(width=2, color="white"),
                showscale=False
            )
        ))

        fig.update_layout(
            title="Top 30 Technical Tools by Mentions",
            height=700,  # Increase height from 600 to 700
            paper_bgcolor="white",
            font=dict(color='black', size=12),  # Reduce font size from 14 to 12
            title_font=dict(color='black', size=18),  # Reduce title size from 20 to 18
            margin=dict(t=80, l=40, r=40, b=40)  # Increase all margins
        )

        show_chart_with_card(fig)

    # =======================
    # CATEGORY BAR CHART
    # =======================
    with col2:
        category_counts = {
            cat: sum(tool_counts.get(t, 0) for t in tools)
            for cat, tools in CATEGORIES.items()
        }

        fig_cat = px.bar(
            x=list(category_counts.keys()),
            y=list(category_counts.values()),
            labels={"x": "Category", "y": "Mentions"},
            title="Tool Mentions by Category",
            color_discrete_sequence=[PRIMARY]
        )

        fig_cat.update_layout(
            template="plotly_white",
            paper_bgcolor="white",
            font=dict(color="black"),
            title_font=dict(color="black", size=18),
            xaxis_tickangle=-30,
            margin=dict(t=60, l=20, r=20, b=150)
        )
        show_chart_with_card(fig_cat)
