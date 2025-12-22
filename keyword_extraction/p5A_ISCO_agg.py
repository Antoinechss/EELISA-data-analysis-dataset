import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# ----------------------------
# Load artefacts
# ----------------------------
job_docs = pd.read_csv("job_phrase_documents_filtered.csv")

print("Jobs loaded:", job_docs.shape[0])

# ----------------------------
# FORCE tfidf_doc to be valid
# ----------------------------
# This MUST happen before any TF-IDF call
job_docs["tfidf_doc"] = job_docs["tfidf_doc"].fillna("").astype(str)

# Drop empty documents
job_docs = job_docs[job_docs["tfidf_doc"].str.strip() != ""]

print("Jobs kept for ISCO TF-IDF:", job_docs.shape[0])

# ----------------------------
# TF-IDF configuration
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

# Attach ISCO labels
tfidf_matrix["isco_3_digit_label"] = job_docs["isco_3_digit_label"].values

# ----------------------------
# Aggregate by ISCO group
# ----------------------------
isco_phrase_scores = (
    tfidf_matrix
    .groupby("isco_3_digit_label")
    .mean()
    .reset_index()
    .melt(
        id_vars="isco_3_digit_label",
        var_name="noun_phrase",
        value_name="mean_tfidf"
    )
)

isco_phrase_scores = isco_phrase_scores[isco_phrase_scores["mean_tfidf"] > 0]

isco_phrase_scores["rank"] = (
    isco_phrase_scores
    .groupby("isco_3_digit_label")["mean_tfidf"]
    .rank(method="dense", ascending=False)
)

TOP_N = 20
isco_top_phrases = isco_phrase_scores[
    isco_phrase_scores["rank"] <= TOP_N
].sort_values(["isco_3_digit_label", "rank"])

# ----------------------------
# Preview one ISCO group
# ----------------------------
example_isco = isco_top_phrases["isco_3_digit_label"].iloc[0]
print("\nExample ISCO group:", example_isco)
print(
    isco_top_phrases[
        isco_top_phrases["isco_3_digit_label"] == example_isco
    ].head(10)
)

# ----------------------------
# Save (CRITICAL)
# ----------------------------
isco_top_phrases.to_csv("isco_top_phrases.csv", index=False)
print("\nSaved: isco_top_phrases.csv")
