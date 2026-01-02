import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import networkx as nx
import itertools
from collections import Counter
import plotly.express as px
from dashboard.helpers import restore_list_safe, normalize
from dashboard.style import show_chart_with_card
from dashboard.utils import get_dataset_path

df = pd.read_csv(get_dataset_path('extractions.csv'))

SKILL_COLOR_PALETTE = {
    "Hard": "#3B6C8E",
    "Soft": "#94A3B8"
}


def show_skills_page():
    st.title("European Job Market Skills Framework")
    st.markdown("---")
    
    # Calculate unique skills metrics
    base_df = df.copy()
    base_df['hard_skills'] = base_df['hard_skills'].apply(restore_list_safe)
    base_df['soft_skills'] = base_df['soft_skills'].apply(restore_list_safe)
    
    # Get unique hard and soft skills
    all_hard_skills = set()
    all_soft_skills = set()
    
    for skills_list in base_df['hard_skills']:
        if isinstance(skills_list, list):
            all_hard_skills.update([normalize(skill) for skill in skills_list if skill])
    
    for skills_list in base_df['soft_skills']:
        if isinstance(skills_list, list):
            all_soft_skills.update([normalize(skill) for skill in skills_list if skill])
    
    # Display metrics at the top - REMOVE show_chart_with_card wrapper
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Number of Unique Hard Skills Mentioned",
            value=f"{len(all_hard_skills):,} Skills"
        )
    
    with col2:
        st.metric(
            label="Number of Unique Soft Skills Mentioned", 
            value=f"{len(all_soft_skills):,} Skills"
        )
    
    st.markdown("---")
    
    # -----------------
    # Comparing the demand for soft vs hard skills 
    # -----------------
    col1, col2 = st.columns([2, 3])
    with col1:
        # overall distribution
        base_df = df.copy()
        base_df['hard_skills'] = base_df['hard_skills'].apply(restore_list_safe)
        base_df['soft_skills'] = base_df['soft_skills'].apply(restore_list_safe)

        # Fix: Count soft_skills, not hard_skills twice
        hard_count = base_df['hard_skills'].apply(len).sum()
        soft_count = base_df['soft_skills'].apply(len).sum()

        shared_df = pd.DataFrame({
            "skill_type": ["Hard", "Soft"],  # Change this to match other charts
            "count": [hard_count, soft_count]
        })

        shared_df["share"] = shared_df["count"] / shared_df["count"].sum() * 100
        shared_df["Group"] = "All jobs"

        # Fix: Use correct column names
        fig = px.bar(
            shared_df,
            x="share",           # Fixed: use actual column name
            y="Group",           # This column exists
            color="skill_type",  # Fixed: use actual column name
            orientation="h",
            text=shared_df["share"].round(1).astype(str) + "%",
            color_discrete_map={
                "Hard": "#3B6C8E",      # Changed from "Hard skills"
                "Soft": "#94A3B8"       # Changed from "Soft skills"
            },
            labels={
                "share": "Share of skill mentions (%)",  # Fixed
                "Group": "",
                "skill_type": "Skill Type"  # Fixed
            },
            title="Distribution of Hard and Soft Skill Requirements"
        )

        fig.update_layout(
            barmode="stack",
            showlegend=True,
            font=dict(color="#1F2933"),
            margin=dict(t=60, l=40, r=120, b=90),  # Increased right margin from r=90 to r=120
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        fig.update_traces(
            textposition="inside",
            insidetextanchor="middle"
        )
        show_chart_with_card(fig)

    with col2:
        # Distribution by ISCO occupation
        skills_df = base_df.copy()
        skills_df["hard_skills"] = skills_df["hard_skills"].apply(restore_list_safe)
        skills_df["soft_skills"] = skills_df["soft_skills"].apply(restore_list_safe)
        skills_df["hard_count"] = skills_df["hard_skills"].apply(len)
        skills_df["soft_count"] = skills_df["soft_skills"].apply(len)
        isco_skills = (
            skills_df
            .groupby("isco_3_label")[["hard_count", "soft_count"]]
            .sum()
            .reset_index()
        )

        isco_skills["total"] = isco_skills["hard_count"] + isco_skills["soft_count"]
        isco_skills = isco_skills[isco_skills["total"] > 0]
        isco_skills["hard_share"] = isco_skills["hard_count"] / isco_skills["total"] * 100
        isco_skills["soft_share"] = isco_skills["soft_count"] / isco_skills["total"] * 100
        
        TOP_N = 12

        top_isco = (
            isco_skills
            .sort_values("total", ascending=False)
            .head(TOP_N)
        )

        isco_long = top_isco.melt(
            id_vars="isco_3_label",
            value_vars=["hard_share", "soft_share"],
            var_name="skill_type",
            value_name="share"
        )

        isco_long["skill_type"] = isco_long["skill_type"].map({
            "hard_share": "Hard",    # Changed from "Hard skills"
            "soft_share": "Soft"     # Changed from "Soft skills"
        })

        fig = px.bar(
            isco_long,
            x="share",
            y="isco_3_label",
            color="skill_type",
            orientation="h",
            color_discrete_map={
                "Hard": "#3B6C8E",
                "Soft": "#94A3B8"
            },
            labels={
                "share": "Share of skill mentions (%)",
                "isco_3_label": " ",
                "skill_type": "Skill type"
            },
            title="Distribution of Hard and Soft Skill Requirements by ISCO-3 Occupation"
        )

        fig.update_layout(
            barmode="stack",
            xaxis_range=[0, 100],
            yaxis=dict(autorange="reversed"),
            font=dict(color="#1F2933"),
            margin=dict(t=60, l=40, r=120, b=90),  # Increased right margin from r=90 to r=120
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        fig.update_traces(
            texttemplate="%{x:.1f}%",
            textposition="inside"
        )

        show_chart_with_card(fig)

    # -----------------
    # Extracting most valued soft and hard skills -- Bubble chart 
    # -----------------

    def resolve_collisions(df, iterations=200):
        # Reset index to ensure consecutive integers
        df = df.reset_index(drop=True)
        
        for _ in range(iterations):
            for i in range(len(df)):
                for j in range(i + 1, len(df)):
                    dx = df.at[i, "x"] - df.at[j, "x"]
                    dy = df.at[i, "y"] - df.at[j, "y"]
                    dist = np.sqrt(dx * dx + dy * dy)

                    min_dist = (df.at[i, "size"] + df.at[j, "size"]) / 2

                    if dist < min_dist:
                        if dist == 0:
                            dx, dy = np.random.rand(), np.random.rand()
                            dist = np.sqrt(dx * dx + dy * dy)

                        shift = (min_dist - dist) / dist * 0.5
                        df.at[i, "x"] += dx * shift
                        df.at[i, "y"] += dy * shift
                        df.at[j, "x"] -= dx * shift
                        df.at[j, "y"] -= dy * shift
        return df

    skills_df = base_df.copy()
    skills_df["hard_skills"] = skills_df["hard_skills"].apply(restore_list_safe)
    skills_df["soft_skills"] = skills_df["soft_skills"].apply(restore_list_safe)

    # ISCO selector
    isco_options = (
        skills_df["isco_3_label"]
        .value_counts()
        .index
        .tolist()
    )

    selected_isco = st.selectbox(
        "Select an ISCO-3 occupation:",
        isco_options
    )

    isco_df = skills_df[skills_df["isco_3_label"] == selected_isco]

    # Hard skills
    hard_exploded = isco_df.explode("hard_skills")
    hard_exploded = hard_exploded[
        hard_exploded["hard_skills"].notna()
        & (hard_exploded["hard_skills"] != "")
    ]
    hard_exploded["hard_skills"] = hard_exploded["hard_skills"].apply(normalize)

    hard_counts = (
        hard_exploded["hard_skills"]
        .value_counts()
        .reset_index()
    )
    hard_counts.columns = ["skill", "count"]
    hard_counts["type"] = "Hard"    # Changed from "Hard skill"

    # Soft skills
    soft_exploded = isco_df.explode("soft_skills")
    soft_exploded = soft_exploded[
        soft_exploded["soft_skills"].notna()
        & (soft_exploded["soft_skills"] != "")
    ]
    soft_exploded["soft_skills"] = soft_exploded["soft_skills"].apply(normalize)

    soft_counts = (
        soft_exploded["soft_skills"]
        .value_counts()
        .reset_index()
    )
    soft_counts.columns = ["skill", "count"]
    soft_counts["type"] = "Soft"    # Changed from "Soft skill"
    skills_counts = pd.concat([hard_counts, soft_counts], ignore_index=True)
    skills_counts = skills_counts.reset_index(drop=True)

    MIN_COUNT = 3
    TOP_N = 25

    skills_counts = skills_counts[skills_counts["count"] >= MIN_COUNT]
    skills_counts = skills_counts.sort_values("count", ascending=False).head(TOP_N)
    skills_counts = skills_counts.reset_index(drop=True)

    BASE_SIZE = 18
    SIZE_FACTOR = 6

    skills_counts["size"] = (
        BASE_SIZE + np.sqrt(skills_counts["count"]) * SIZE_FACTOR
    )

    # Random layout
    CANVAS_SIZE = 600  
    np.random.seed(42)
    skills_counts["x"] = np.random.uniform(0, CANVAS_SIZE, size=len(skills_counts))
    skills_counts["y"] = np.random.uniform(0, CANVAS_SIZE, size=len(skills_counts))


    # Resolve overlaps
    skills_counts = resolve_collisions(skills_counts, iterations=60)

    # Plot
    fig = px.scatter(
        skills_counts,
        x="x",
        y="y",
        size="size",
        color="type",
        text="skill",
        size_max=130,
        color_discrete_map={
            "Hard": "#3B6C8E",
            "Soft": "#94A3B8"
        },
        hover_data={
            "skill": True,
            "count": True,
            "x": False,
            "y": False,
            "size": False
        },
        title=f"Skill Bubble Map — {selected_isco}"
    )

    fig.update_traces(
        textposition="middle center",
        textfont=dict(size=12, color="white"),
        marker=dict(opacity=0.9, line=dict(width=2, color="white"))
    )

    fig.update_layout(
        height=900, 
        xaxis=dict(
            visible=False,
            range=[0, CANVAS_SIZE],
            fixedrange=True
        ),
        yaxis=dict(
            visible=False,
            range=[0, CANVAS_SIZE],
            fixedrange=True
        ),
        legend_title_text="Skill type",
        font=dict(color="#1F2933"),
        margin=dict(t=90, l=90, r=90, b=90),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    show_chart_with_card(fig)
    # --------------
    # Skills specialization vs diversification 
    # --------------
    col1, col2 = st.columns(2)

    with col1:
        # overview of skills diversity and qty per domain 
        skill_dvsc_df = base_df.copy()

        skill_dvsc_df["hard_skills"] = skill_dvsc_df["hard_skills"].apply(restore_list_safe)
        skill_dvsc_df["soft_skills"] = skill_dvsc_df["soft_skills"].apply(restore_list_safe)

        skill_dvsc_df["all_skills"] = skill_dvsc_df.apply(
            lambda r: list(set(r["hard_skills"] + r["soft_skills"])),
            axis=1
        )

        exploded = skill_dvsc_df.explode("all_skills")
        exploded = exploded[
            exploded["all_skills"].notna() & (exploded["all_skills"] != "")
        ]

        isco_skill_stats = (
            exploded
            .groupby("isco_3_label")
            .agg(
                total_skill_mentions=("all_skills", "count"),
                unique_skills=("all_skills", "nunique"),
                job_count=("job_id", "nunique")
            )
            .reset_index()
        )

        MIN_JOBS = 30
        isco_skill_stats = isco_skill_stats[
            isco_skill_stats["job_count"] >= MIN_JOBS
        ]

        # ------------------
        # ISCO selector
        # ------------------
        isco_options = ["All"] + sorted(isco_skill_stats["isco_3_label"].unique().tolist())

        selected_isco = st.selectbox(
            "Highlight an ISCO-3 occupation:",
            isco_options,
            index=0
        )

        # Color logic
        if selected_isco == "All":
            isco_skill_stats["color"] = isco_skill_stats["isco_3_label"]
            color_map = None
        else:
            isco_skill_stats["color"] = isco_skill_stats["isco_3_label"].apply(
                lambda x: "Selected ISCO" if x == selected_isco else "Other ISCOs"
            )
            color_map = {
                "Selected ISCO": "#3B6C8E",
                "Other ISCOs": "#D1D5DB"
            }

        # ------------------
        # Plot
        # ------------------
        fig = px.scatter(
            isco_skill_stats,
            x="unique_skills",
            y="total_skill_mentions",
            size="job_count",
            color="color",
            hover_name="isco_3_label",
            size_max=60,
            labels={
                "unique_skills": "Number of unique skills",
                "total_skill_mentions": "Total skill mentions",
                "job_count": "Number of job postings",
                "color": ""
            },
            title="Skill Concentration vs Diversification by ISCO-3 Occupation",
            color_discrete_map=color_map,
            template="plotly_white"
        )

        fig.update_traces(
            marker=dict(
                opacity=0.85,
                line=dict(width=1, color="white")
            )
        )

        fig.update_layout(
            showlegend=(selected_isco != "All"),
            legend_title_text="",
            font=dict(color="#1F2933"),
            margin=dict(t=60, l=40, r=40, b=90),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        x_med = isco_skill_stats["unique_skills"].median()
        y_med = isco_skill_stats["total_skill_mentions"].median()

        fig.add_vline(x=x_med, line_dash="dot", line_color="gray")
        fig.add_hline(y=y_med, line_dash="dot", line_color="gray")

        show_chart_with_card(fig)

    with col2:
        # Skill diversity overview 
        skill_dvsc_df = base_df.copy()

        skill_dvsc_df["hard_skills"] = skill_dvsc_df["hard_skills"].apply(restore_list_safe)
        skill_dvsc_df["soft_skills"] = skill_dvsc_df["soft_skills"].apply(restore_list_safe)

        skill_dvsc_df["all_skills"] = skill_dvsc_df.apply(
            lambda r: list(set(r["hard_skills"] + r["soft_skills"])),
            axis=1
        )

        exploded = skill_dvsc_df.explode("all_skills")
        exploded = exploded[
            exploded["all_skills"].notna() & (exploded["all_skills"] != "")
        ]

        isco_skill_stats = (
            exploded
            .groupby("isco_3_label")
            .agg(
                total_skill_mentions=("all_skills", "count"),
                unique_skills=("all_skills", "nunique"),
                job_count=("job_id", "nunique")
            )
            .reset_index()
        )

        MIN_JOBS = 30
        isco_skill_stats = isco_skill_stats[
            isco_skill_stats["job_count"] >= MIN_JOBS
        ]

        MAX_LEN = 40
        isco_skill_stats["isco_short"] = isco_skill_stats["isco_3_label"].apply(
            lambda x: x if len(x) <= MAX_LEN else x[:MAX_LEN] + "…"
        )

        isco_skill_stats["skill_diversification_ratio"] = (
            isco_skill_stats["unique_skills"]
            / isco_skill_stats["total_skill_mentions"]
        )
        plot_df = isco_skill_stats.sort_values("skill_diversification_ratio")

        fig = px.bar(
            plot_df,
            x="skill_diversification_ratio",
            y="isco_3_label",   # use full unique label as axis category
            orientation="h",
            hover_name="isco_3_label",
            hover_data={
                "isco_short": True,
                "unique_skills": True,
                "total_skill_mentions": True,
                "job_count": True,
                "skill_diversification_ratio": ":.3f"
            },
            labels={
                "skill_diversification_ratio": "Skill diversification ratio",
                "isco_3_label": "ISCO-3 occupation"
            },
            color="skill_diversification_ratio",
            color_continuous_scale="Blues",
            template="plotly_white"
        )

        # Replace tick labels with the shortened version
        fig.update_yaxes(
            tickmode="array",
            tickvals=plot_df["isco_3_label"].tolist(),
            ticktext=plot_df["isco_short"].tolist()
        )

        fig.update_layout(
            height=900,
            font=dict(color="#1F2933"),
            margin=dict(t=60, l=40, r=20, b=90),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False
        )

        show_chart_with_card(fig)
    
    # ----------------- 
    # Skills co-occurrence Network 
    # ----------------- 
    # Data preparation 
    skills_df = base_df.copy()
    skills_df["hard_skills"] = skills_df["hard_skills"].apply(restore_list_safe)
    skills_df["soft_skills"] = skills_df["soft_skills"].apply(restore_list_safe)

    # ISCO selector
    isco_options = (
        skills_df["isco_3_label"]
        .value_counts()
        .index
        .tolist()
    )

    selected_isco = st.selectbox(
        "Select an ISCO-3 occupation for skill co-occurrence:",
        isco_options
    )

    isco_df = skills_df[skills_df["isco_3_label"] == selected_isco]

    # Build combined skill list per job
    isco_df["all_skills"] = isco_df.apply(
        lambda r: list(set(
            [normalize(s) for s in r["hard_skills"] + r["soft_skills"]]
        )),
        axis=1
    )

    isco_df = isco_df[isco_df["all_skills"].apply(len) >= 2]
    # Build co-occurrence matrix
    pair_counter = Counter()
    for skills in isco_df["all_skills"]:
        pairs = itertools.combinations(sorted(skills), 2)
        pair_counter.update(pairs)

    cooc_df = (
        pd.DataFrame(pair_counter.items(), columns=["pair", "count"])
        .sort_values("count", ascending=False)
    )
    # Noise filtering 
    MIN_COOC = 5
    TOP_PAIRS = 50
    cooc_df = cooc_df[cooc_df["count"] >= MIN_COOC].head(TOP_PAIRS)
    # Build network graph 
    G = nx.Graph()
    for _, row in cooc_df.iterrows():
        skill_a, skill_b = row["pair"]
        weight = row["count"]
        G.add_edge(skill_a, skill_b, weight=weight)

    # Layout 
    pos = nx.spring_layout(
        G,
        k=0.8,
        iterations=50,
        seed=42
    )
    edge_x, edge_y = [], []

    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="#CBD5E1"),
        hoverinfo="none",
        mode="lines"
    )

    node_x, node_y, node_size, node_text = [], [], [], []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        node_size.append(G.degree(node) * 6)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="middle center",
        hoverinfo="text",
        marker=dict(
            size=node_size,
            color="#3B6C8E",
            opacity=0.85,
            line=dict(width=1, color="white")
        )
    )
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=f"Skill Co-occurrence Network — {selected_isco}",
            showlegend=False,
            hovermode="closest",
            margin=dict(t=60, l=20, r=20, b=20),
            font=dict(color="#1F2933"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False)
        )
    )

    fig.update_layout(
            height=900
        )

    show_chart_with_card(fig)






