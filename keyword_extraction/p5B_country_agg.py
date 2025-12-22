import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# ----------------------------
# Load artefacts
# ----------------------------
job_docs = pd.read_csv("job_phrase_documents_filtered.csv")

print("Jobs loaded:", job_docs.shape[0])

# ----------------------------
# Clean TF-IDF documents
# ----------------------------
job_docs["tfidf_doc"] = job_docs["tfidf_doc"].fillna("").astype(str)
job_docs = job_docs[job_docs["tfidf_doc"].str.strip() != ""]

print("Jobs kept for country TF-IDF:", job_docs.shape[0])

# ----------------------------
# TF-IDF configuration (same as before)
# ----------------------------
vectorizer = TfidfVectorizer(
    lowercase=False,
    tokenizer=str.split,
    preprocessor=None,
    token_pattern=None,
    min_df=10,
    max_df=0.5,
    norm="l2"
)

# ----------------------------
# Compute TF-IDF
# ----------------------------
X = vectorizer.fit_transform(job_docs["tfidf_doc"])
phrases = vectorizer.get_feature_names_out()

print("TF-IDF matrix shape:", X.shape)

# ----------------------------
# Build TF-IDF DataFrame
# ----------------------------
tfidf_matrix = pd.DataFrame(
    X.toarray(),
    columns=phrases
)

# Attach country
tfidf_matrix["country"] = job_docs["country"].values

# ----------------------------
# Aggregate by country
# ----------------------------
country_phrase_scores = (
    tfidf_matrix
    .groupby("country")
    .mean()
    .reset_index()
    .melt(
        id_vars="country",
        var_name="noun_phrase",
        value_name="mean_tfidf"
    )
)

country_phrase_scores = country_phrase_scores[
    country_phrase_scores["mean_tfidf"] > 0
]

country_phrase_scores["rank"] = (
    country_phrase_scores
    .groupby("country")["mean_tfidf"]
    .rank(method="dense", ascending=False)
)

TOP_N = 20
country_top_phrases = country_phrase_scores[
    country_phrase_scores["rank"] <= TOP_N
].sort_values(["country", "rank"])

# ----------------------------
# Preview one country
# ----------------------------
example_country = country_top_phrases["country"].iloc[0]
print("\nExample country:", example_country)
print(
    country_top_phrases[
        country_top_phrases["country"] == example_country
    ].head(10)
)

# ----------------------------
# Save (CRITICAL)
# ----------------------------
country_top_phrases.to_csv("country_top_phrases.csv", index=False)
print("\nSaved: country_top_phrases.csv")
