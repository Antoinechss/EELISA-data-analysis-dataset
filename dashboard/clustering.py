"""
Transition Engineering Profiles Discovery via Unsupervised Clustering

This module implements a complete clustering pipeline to discover distinct 
engineering profiles from job posting data. It focuses on transition-related
characteristics: sustainability, digitalization, and systems thinking.

Architecture:
- Feature engineering based on skills, competences, and job characteristics
- KMeans clustering with automatic K selection via silhouette analysis
- Profile characterization and naming based on cluster centroids
"""

import pandas as pd
import numpy as np
import ast
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')


def safe_parse_list(x):
    """Safely parse string representations of lists."""
    if pd.isna(x) or x == '[]' or x == '':
        return []
    try:
        return ast.literal_eval(x) if isinstance(x, str) else []
    except:
        return []


def engineer_clustering_features(df):
    """
    Engineer features suitable for clustering transition engineering profiles.
    
    Focus on quantitative indicators that capture:
    1. Skill intensity and diversity
    2. Digital and green transition alignment
    3. Education and occupation characteristics
    4. Geographic and systemic factors
    
    Returns DataFrame with engineered features for clustering.
    """
    df_features = df.copy()
    
    # Parse skill lists
    df_features['hard_skills_parsed'] = df['hard_skills'].apply(safe_parse_list)
    df_features['digital_competences_parsed'] = df['digital_competences'].apply(safe_parse_list)
    df_features['green_competences_parsed'] = df['green_competences'].apply(safe_parse_list)
    df_features['knowledge_domains_parsed'] = df['knowledge_domains'].apply(safe_parse_list)
    df_features['tools_parsed'] = df['tools'].apply(safe_parse_list)
    
    # Feature 1: Skill intensity metrics
    df_features['total_skills_count'] = df_features['hard_skills_parsed'].apply(len)
    df_features['digital_intensity'] = df_features['digital_competences_parsed'].apply(len)
    df_features['green_intensity'] = df_features['green_competences_parsed'].apply(len)
    df_features['knowledge_breadth'] = df_features['knowledge_domains_parsed'].apply(len)
    df_features['tool_proficiency'] = df_features['tools_parsed'].apply(len)
    
    # Feature 2: Transition indicators
    df_features['digital_green_ratio'] = (
        df_features['digital_intensity'] / 
        (df_features['digital_intensity'] + df_features['green_intensity'] + 1)
    )
    df_features['sustainability_focus'] = (
        df_features['green_intensity'] > 0
    ).astype(int)
    df_features['high_digital'] = (
        df_features['digital_intensity'] >= df_features['digital_intensity'].quantile(0.75)
    ).astype(int)
    
    # Feature 3: Education level encoding
    education_order = ['none', 'other', 'bachelor', 'master', 'phd']
    df_features['education_level_encoded'] = df_features['education_level'].map({
        level: idx for idx, level in enumerate(education_order)
    }).fillna(1)  # Default to 'other'
    
    # Feature 4: ISCO category indicators (top categories)
    top_isco = df['isco_3_label'].value_counts().head(8).index
    for i, isco in enumerate(top_isco):
        # Create safe column names
        safe_name = f'isco_cat_{i}'
        df_features[safe_name] = (
            df_features['isco_3_label'] == isco
        ).astype(int)
    
    # Feature 5: Geographic clustering (EU regions)
    western_eu = ['Germany', 'France', 'Switzerland', 'Belgium', 'Netherlands']
    northern_eu = ['Sweden', 'Denmark', 'Finland', 'Norway']
    southern_eu = ['Italy', 'Spain', 'Portugal', 'Greece']
    eastern_eu = ['Poland', 'Czech Republic', 'Hungary', 'Croatia', 'Latvia']
    
    df_features['region_western'] = df_features['country'].isin(western_eu).astype(int)
    df_features['region_northern'] = df_features['country'].isin(northern_eu).astype(int)
    df_features['region_southern'] = df_features['country'].isin(southern_eu).astype(int)
    df_features['region_eastern'] = df_features['country'].isin(eastern_eu).astype(int)
    df_features['region_other'] = (
        ~df_features['country'].isin(western_eu + northern_eu + southern_eu + eastern_eu)
    ).astype(int)
    
    # Feature 6: Skill complexity indicators
    df_features['skill_diversity_ratio'] = (
        df_features['knowledge_breadth'] / 
        (df_features['total_skills_count'] + 1)
    )
    df_features['tech_intensity'] = (
        (df_features['digital_intensity'] + df_features['tool_proficiency']) /
        (df_features['total_skills_count'] + 1)
    )
    
    # Select final feature set for clustering
    clustering_features = [
        # Core skill metrics
        'total_skills_count', 'digital_intensity', 'green_intensity', 
        'knowledge_breadth', 'tool_proficiency',
        # Transition indicators  
        'digital_green_ratio', 'sustainability_focus', 'high_digital',
        # Education and complexity
        'education_level_encoded', 'skill_diversity_ratio', 'tech_intensity',
        # Regional indicators
        'region_western', 'region_northern', 'region_southern', 'region_eastern', 'region_other'
    ]
    
    # Add top ISCO categories
    isco_features = [col for col in df_features.columns if col.startswith('isco_cat_')]
    clustering_features.extend(isco_features)
    
    return df_features[['row_id'] + clustering_features], clustering_features


def find_optimal_clusters(X, k_range=(3, 7)):
    """Find optimal number of clusters using silhouette analysis."""
    silhouette_scores = {}
    
    for k in range(k_range[0], k_range[1]):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X)
        silhouette_avg = silhouette_score(X, cluster_labels)
        silhouette_scores[k] = silhouette_avg
    
    optimal_k = max(silhouette_scores, key=silhouette_scores.get)
    return optimal_k, silhouette_scores


def run_clustering(df):
    """
    Execute complete clustering pipeline on job data.
    
    Returns:
    - df_clustered: Original dataframe with profile_cluster column added
    - cluster_info: Dictionary with clustering metadata and summaries
    """
    print("🔍 Engineering features for clustering...")
    
    # Feature engineering
    df_features, feature_names = engineer_clustering_features(df)
    
    # Prepare clustering data
    X = df_features[feature_names].fillna(0)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print("🎯 Finding optimal number of clusters...")
    
    # Find optimal K
    optimal_k, silhouette_scores = find_optimal_clusters(X_scaled)
    
    print(f"✅ Optimal K: {optimal_k}")
    print("Silhouette scores:", {k: f"{v:.3f}" for k, v in silhouette_scores.items()})
    
    # Final clustering
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    # Add clusters to original dataframe
    df_clustered = df.copy()
    df_clustered['profile_cluster'] = cluster_labels
    
    # Create 2D projection for visualization
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    
    df_clustered['pca_x'] = X_pca[:, 0]
    df_clustered['pca_y'] = X_pca[:, 1]
    
    # Generate cluster summaries
    cluster_info = {
        'optimal_k': optimal_k,
        'silhouette_scores': silhouette_scores,
        'feature_names': feature_names,
        'cluster_centroids': kmeans.cluster_centers_,
        'scaler': scaler,
        'pca': pca,
        'pca_explained_variance': pca.explained_variance_ratio_
    }
    
    print(f"🎨 Discovered {optimal_k} transition engineering profiles")
    
    return df_clustered, cluster_info


def characterize_clusters(df_clustered, cluster_info):
    """
    Analyze cluster characteristics and generate human-readable profile names.
    
    Returns dictionary mapping cluster IDs to profile descriptions.
    """
    profiles = {}
    
    for cluster_id in sorted(df_clustered['profile_cluster'].unique()):
        cluster_data = df_clustered[df_clustered['profile_cluster'] == cluster_id]
        
        # Parse skill lists for analysis
        cluster_data = cluster_data.copy()
        cluster_data['digital_parsed'] = cluster_data['digital_competences'].apply(safe_parse_list)
        cluster_data['green_parsed'] = cluster_data['green_competences'].apply(safe_parse_list)
        cluster_data['hard_skills_parsed'] = cluster_data['hard_skills'].apply(safe_parse_list)
        
        # Calculate key characteristics
        avg_digital = cluster_data['digital_parsed'].apply(len).mean()
        avg_green = cluster_data['green_parsed'].apply(len).mean()
        avg_skills = cluster_data['hard_skills_parsed'].apply(len).mean()
        
        top_education = cluster_data['education_level'].mode()[0] if not cluster_data.empty else 'bachelor'
        top_isco = cluster_data['isco_3_label'].value_counts().index[0] if not cluster_data.empty else 'Engineering'
        top_countries = cluster_data['country'].value_counts().head(3).index.tolist()
        
        sustainability_rate = (cluster_data['green_parsed'].apply(len) > 0).mean()
        high_digital_rate = (cluster_data['digital_parsed'].apply(len) >= 3).mean()
        
        # Generate profile name and description based on characteristics
        profile_name, description = _generate_profile_name(
            avg_digital, avg_green, avg_skills, sustainability_rate, 
            high_digital_rate, top_education, top_isco
        )
        
        profiles[cluster_id] = {
            'name': profile_name,
            'description': description,
            'size': len(cluster_data),
            'characteristics': {
                'avg_digital_competences': round(avg_digital, 2),
                'avg_green_competences': round(avg_green, 2),
                'avg_total_skills': round(avg_skills, 2),
                'sustainability_adoption_rate': round(sustainability_rate * 100, 1),
                'high_digital_rate': round(high_digital_rate * 100, 1),
                'primary_education': top_education,
                'primary_occupation': top_isco,
                'top_countries': top_countries
            }
        }
    
    return profiles


def _generate_profile_name(avg_digital, avg_green, avg_skills, sustainability_rate, 
                          high_digital_rate, top_education, top_isco):
    """Generate human-readable profile names based on cluster characteristics."""
    
    # Determine primary characteristics
    is_highly_digital = avg_digital >= 3
    is_sustainability_focused = avg_green >= 1 or sustainability_rate >= 0.3
    is_skill_intensive = avg_skills >= 10
    is_research_oriented = 'research' in top_isco.lower() or 'science' in top_isco.lower()
    is_software_oriented = 'software' in top_isco.lower() or 'developer' in top_isco.lower()
    
    # Generate names based on combination of characteristics
    if is_software_oriented and is_sustainability_focused:
        return "Green Technology Developers", "Software professionals driving sustainable digital solutions"
    elif is_software_oriented and is_highly_digital:
        return "Digital Innovation Specialists", "Advanced software developers and digital technology experts"
    elif is_highly_digital and is_sustainability_focused:
        return "Sustainable Systems Engineers", "Engineers integrating digital tools with environmental solutions"
    elif is_sustainability_focused and is_skill_intensive:
        return "Environmental Engineering Experts", "Comprehensive sustainability-focused engineering professionals"
    elif is_research_oriented:
        return "Research & Development Engineers", "Engineering professionals focused on innovation and R&D"
    elif is_highly_digital:
        return "Digital Engineering Professionals", "Engineers with strong digital and technical competencies"
    elif is_skill_intensive:
        return "Comprehensive Engineering Generalists", "Well-rounded engineers with broad technical expertise"
    else:
        return "Core Engineering Professionals", "Traditional engineering roles with foundational skills"


def get_cluster_summary_stats(df_clustered, cluster_id):
    """Get detailed statistics for a specific cluster."""
    cluster_data = df_clustered[df_clustered['profile_cluster'] == cluster_id]
    
    if cluster_data.empty:
        return {}
    
    # Parse lists
    cluster_data = cluster_data.copy()
    cluster_data['digital_parsed'] = cluster_data['digital_competences'].apply(safe_parse_list)
    cluster_data['green_parsed'] = cluster_data['green_competences'].apply(safe_parse_list)
    cluster_data['hard_skills_parsed'] = cluster_data['hard_skills'].apply(safe_parse_list)
    cluster_data['knowledge_parsed'] = cluster_data['knowledge_domains'].apply(safe_parse_list)
    
    return {
        'size': len(cluster_data),
        'education_distribution': cluster_data['education_level'].value_counts().to_dict(),
        'country_distribution': cluster_data['country'].value_counts().head(10).to_dict(),
        'isco_distribution': cluster_data['isco_3_label'].value_counts().head(8).to_dict(),
        'skill_metrics': {
            'avg_hard_skills': cluster_data['hard_skills_parsed'].apply(len).mean(),
            'avg_digital_competences': cluster_data['digital_parsed'].apply(len).mean(),
            'avg_green_competences': cluster_data['green_parsed'].apply(len).mean(),
            'avg_knowledge_domains': cluster_data['knowledge_parsed'].apply(len).mean(),
        },
        'transition_indicators': {
            'sustainability_adoption': (cluster_data['green_parsed'].apply(len) > 0).mean() * 100,
            'high_digital_intensity': (cluster_data['digital_parsed'].apply(len) >= 3).mean() * 100,
            'comprehensive_skills': (cluster_data['hard_skills_parsed'].apply(len) >= 10).mean() * 100
        }
    }
