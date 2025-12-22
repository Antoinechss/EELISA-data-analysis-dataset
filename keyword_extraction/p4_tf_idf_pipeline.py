import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# ----------------------------
# Load locked artefacts
# ----------------------------
corpus_df = pd.read_csv("cleaned_corpus.csv")
np_occ = pd.read_csv("noun_phrase_occurrences.csv")
phrase_candidates = pd.read_csv("phrase_candidates.csv")

# ----------------------------
# Sanitize noun_phrase
# ----------------------------
np_occ["noun_phrase"] = np_occ["noun_phrase"].fillna("").astype(str)
np_occ = np_occ[np_occ["noun_phrase"].str.strip() != ""]

# ----------------------------
# Restrict to validated phrases
# ----------------------------
allowed_phrases = set(phrase_candidates["noun_phrase"].astype(str))
np_occ = np_occ[np_occ["noun_phrase"].isin(allowed_phrases)]

# ----------------------------
# Build job → phrase lists
# ----------------------------
job_phrases = (
    np_occ
    .groupby("job_id")["noun_phrase"]
    .apply(list)
    .reset_index()
)

job_docs = corpus_df.merge(job_phrases, on="job_id", how="left")
job_docs["noun_phrase"] = job_docs["noun_phrase"].apply(
    lambda x: x if isinstance(x, list) else []
)

# ----------------------------
# Phrase → token
# ----------------------------
def phrase_to_token(p):
    return p.replace(" ", "_")

job_docs["tfidf_doc"] = job_docs["noun_phrase"].apply(
    lambda phrases: " ".join(phrase_to_token(p) for p in phrases)
)

print("Jobs:", job_docs.shape[0])

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
# Fit TF-IDF
# ----------------------------
X = vectorizer.fit_transform(job_docs["tfidf_doc"])
feature_names = vectorizer.get_feature_names_out()

print("TF-IDF matrix shape:", X.shape)
print("Number of unique phrases:", len(feature_names))

# ----------------------------
# Aggregate scores
# ----------------------------
mean_tfidf = np.asarray(X.mean(axis=0)).ravel()

tfidf_table = (
    pd.DataFrame({
        "noun_phrase": feature_names,
        "mean_tfidf": mean_tfidf
    })
    .sort_values("mean_tfidf", ascending=False)
)

print("\nTop 20 TF-IDF noun phrases:")
print(tfidf_table.head(20))

# ----------------------------
# Save artefacts (CRITICAL)
# ----------------------------
job_docs.to_csv("job_phrase_documents_filtered.csv", index=False)
tfidf_table.to_csv("tfidf_phrase_scores.csv", index=False)

print("\nSaved:")
print("- job_phrase_documents_filtered.csv")
print("- tfidf_phrase_scores.csv")
