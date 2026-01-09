#!/usr/bin/env python3
"""
Standalone script to generate ISCED Field × ISCO Occupation Distribution Heatmap as PDF.

This script creates a high-quality heatmap showing the distribution of education fields
across different occupation categories and exports it as a PDF file.

Usage:
    python generate_isced_isco_heatmap_pdf.py

Output:
    - isced_isco_heatmap.pdf (in the same directory)
    - Optional: isced_isco_heatmap.png (high-resolution PNG)
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import dashboard utilities
try:
    from dashboard.utils import get_dataset_path
except ImportError:
    # Fallback to direct path if imports fail
    def get_dataset_path(filename):
        return os.path.join(project_root, 'datasets', filename)

def load_data():
    """Load and prepare the datasets."""
    print("📁 Loading datasets...")
    
    try:
        # Load main jobs dataset
        jobs_df = pd.read_csv(get_dataset_path('european_jobs.csv'))
        print(f"✅ Loaded {len(jobs_df):,} job records")
        
        # Load education classification
        edu_df = pd.read_csv(get_dataset_path('extractions.csv'))
        print(f"✅ Loaded {len(edu_df):,} education records")
        
        return jobs_df, edu_df
        
    except FileNotFoundError as e:
        print(f"❌ Error loading data: {e}")
        print("Please ensure the datasets are in the 'datasets' folder:")
        print("  - european_jobs.csv")
        print("  - extractions.csv")
        sys.exit(1)

def prepare_education_data(edu_df):
    """Prepare education field data."""
    print("🔄 Processing education fields...")
    
    # Helper function to safely evaluate lists
    def restore_list_safe(x):
        if pd.isna(x) or x == "" or x == "[]":
            return []
        if isinstance(x, list):
            return x
        if isinstance(x, str):
            try:
                import ast
                return ast.literal_eval(x)
            except (ValueError, SyntaxError):
                return [x] if x.strip() else []
        return []
    
    # Process education fields
    edu_df_clean = edu_df.copy()
    edu_df_clean['isced_fields'] = edu_df_clean['isced_fields'].apply(restore_list_safe)
    
    # Explode to have one row per education field
    edu_exploded = edu_df_clean.explode('isced_fields')
    edu_exploded = edu_exploded[
        edu_exploded['isced_fields'].notna() & 
        (edu_exploded['isced_fields'] != "")
    ]
    
    # Map to broad ISCED categories
    isced_mapping = {
        # Broad field mappings for better visualization
        "Business and administration": "Business and administration",
        "Engineering and engineering trades": "Engineering and engineering trades", 
        "Information and Communication Technologies": "Information and Communication Technologies",
        "Natural sciences, mathematics and statistics": "Natural sciences, mathematics and statistics",
        "Health and welfare": "Health and welfare",
        "Education": "Education",
        "Social sciences, journalism and information": "Social sciences, journalism and information",
        "Arts and humanities": "Arts and humanities",
        "Services": "Services",
        "Manufacturing and processing": "Manufacturing and processing",
        "Architecture and building": "Architecture and building",
        "Agriculture, forestry, fisheries and veterinary": "Agriculture, forestry, fisheries and veterinary"
    }
    
    # Map detailed fields to broad categories
    edu_exploded['isced_broad_name'] = edu_exploded['isced_fields'].map(
        lambda x: isced_mapping.get(x, x) if pd.notna(x) else None
    )
    
    print(f"✅ Processed {len(edu_exploded)} education-job mappings")
    return edu_exploded

def create_heatmap_data(jobs_df, edu_df):
    """Create the heatmap data by merging jobs with education fields."""
    print("📊 Creating heatmap data...")
    
    # Prepare education data
    edu_processed = prepare_education_data(edu_df)
    
    # Merge with jobs data
    merged_df = pd.merge(
        edu_processed[['job_id', 'isced_broad_name']].dropna(),
        jobs_df[['job_id', 'isco_3_digit_label']].dropna(),
        on='job_id',
        how='inner'
    )
    
    if merged_df.empty:
        print("❌ No matching data found between education fields and occupations")
        sys.exit(1)
    
    print(f"✅ Merged data: {len(merged_df):,} job-education-occupation records")
    
    # Create cross-tabulation for heatmap
    heatmap_data = pd.crosstab(
        merged_df['isced_broad_name'],
        merged_df['isco_3_digit_label'],
        normalize='index'  # Normalize by row (ISCED field)
    ) * 100  # Convert to percentages
    
    # Keep only top ISCO categories to avoid clutter
    top_isco = merged_df['isco_3_digit_label'].value_counts().head(12).index
    heatmap_data = heatmap_data[top_isco]
    
    # Keep only top ISCED categories
    top_isced = merged_df['isced_broad_name'].value_counts().head(10).index
    heatmap_data = heatmap_data.loc[top_isced]
    
    print(f"✅ Heatmap dimensions: {heatmap_data.shape[0]} education fields × {heatmap_data.shape[1]} occupations")
    return heatmap_data, len(merged_df)

def create_pdf_figure(heatmap_data, n_jobs):
    """Create a high-quality figure optimized for PDF export."""
    print("🎨 Creating PDF-optimized figure...")
    
    # Prepare labels with reasonable length for PDF
    x_labels = [
        label[:30] + "..." if len(label) > 30 else label 
        for label in heatmap_data.columns
    ]
    y_labels = [
        label[:35] + "..." if len(label) > 35 else label 
        for label in heatmap_data.index
    ]
    
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=x_labels,
        y=y_labels,
        colorscale='Blues',
        showscale=True,
        colorbar=dict(
            title="Percentage of Jobs<br>in Education Field (%)",
            titleside="right",
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            thickness=25,
            len=0.8,
            x=1.02
        ),
        hovertemplate='<b>%{y}</b><br>%{x}<br>%{z:.1f}%<extra></extra>',
        # Add text annotations for better readability
        text=[[f"{val:.1f}%" if val > 2 else "" for val in row] for row in heatmap_data.values],
        texttemplate="%{text}",
        textfont=dict(size=8, color="white")
    ))
    
    # PDF-optimized layout
    fig.update_layout(
        title=dict(
            text=f"ISCED Education Field × ISCO Occupation Distribution<br><sub>Based on {n_jobs:,} European Job Postings</sub>",
            font=dict(size=18, color="#1f2937", family="Arial"),
            x=0.5,
            xanchor='center',
            y=0.95
        ),
        xaxis=dict(
            title="ISCO-3 Occupation Categories",
            titlefont=dict(size=14, color="#1f2937", family="Arial"),
            tickfont=dict(size=11, color="#1f2937", family="Arial"),
            tickangle=45,
            side="bottom"
        ),
        yaxis=dict(
            title="ISCED Education Field",
            titlefont=dict(size=14, color="#1f2937", family="Arial"),
            tickfont=dict(size=11, color="#1f2937", family="Arial"),
            autorange="reversed"  # Top to bottom ordering
        ),
        width=1200,
        height=800,
        margin=dict(t=120, l=280, r=150, b=180),  # Generous margins for PDF
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", size=12, color="#1f2937")
    )
    
    # Add footer with metadata
    current_date = datetime.now().strftime("%Y-%m-%d")
    fig.add_annotation(
        text=f"Generated on {current_date} | EELISA Data Analysis Project",
        xref="paper", yref="paper",
        x=0.5, y=-0.15,
        showarrow=False,
        font=dict(size=10, color="#6b7280", family="Arial"),
        xanchor="center"
    )
    
    return fig

def export_pdf(fig, filename="isced_isco_heatmap.pdf"):
    """Export the figure as a PDF."""
    print(f"💾 Exporting to PDF: {filename}")
    
    try:
        # Configure PDF export
        pio.kaleido.scope.default_format = "pdf"
        
        # Export as PDF with high quality
        fig.write_image(
            filename,
            format="pdf",
            width=1200,
            height=800,
            scale=2  # High resolution
        )
        
        print(f"✅ PDF exported successfully: {filename}")
        
        # Also export as high-res PNG for backup
        png_filename = filename.replace(".pdf", ".png")
        fig.write_image(
            png_filename,
            format="png",
            width=1200,
            height=800,
            scale=3  # Very high resolution for PNG
        )
        print(f"✅ High-resolution PNG also saved: {png_filename}")
        
    except Exception as e:
        print(f"❌ Error exporting PDF: {e}")
        print("Trying to export as HTML instead...")
        
        html_filename = filename.replace(".pdf", ".html")
        fig.write_html(html_filename)
        print(f"✅ Exported as HTML: {html_filename}")
        print("You can open the HTML file in a browser and print to PDF")

def main():
    """Main execution function."""
    print("🚀 ISCED × ISCO Heatmap PDF Generator")
    print("=" * 50)
    
    # Load data
    jobs_df, edu_df = load_data()
    
    # Create heatmap data
    heatmap_data, n_jobs = create_heatmap_data(jobs_df, edu_df)
    
    # Create figure
    fig = create_pdf_figure(heatmap_data, n_jobs)
    
    # Export to PDF
    export_pdf(fig)
    
    print("\n" + "=" * 50)
    print("🎉 ISCED × ISCO Heatmap generation completed!")
    print("\nFiles generated:")
    print("📄 isced_isco_heatmap.pdf - High-quality PDF")
    print("🖼️  isced_isco_heatmap.png - High-resolution PNG backup")

if __name__ == "__main__":
    main()
