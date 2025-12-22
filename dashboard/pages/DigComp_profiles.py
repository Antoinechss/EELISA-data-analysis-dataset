import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import ast

# ----------------------------
# Load data
# ----------------------------
df = pd.read_csv("isco_phrases_mapped_frameworks.csv")

# Fix list columns
df["digcomp_domains"] = df["digcomp_domains"].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else []
)

# Explode
df = df.explode("digcomp_domains")
df = df[df["digcomp_domains"].notna() & (df["digcomp_domains"] != "")]

# Aggregate
agg = (
    df.groupby(["isco_3_digit_label", "digcomp_domains"])["mean_tfidf"]
    .sum()
    .reset_index()
)

# Pivot
matrix = agg.pivot(
    index="isco_3_digit_label",
    columns="digcomp_domains",
    values="mean_tfidf"
).fillna(0)

# ----------------------------
# NORMALIZATION (row-wise)
# ----------------------------
matrix_norm = matrix.div(matrix.sum(axis=1), axis=0).fillna(0)

# ----------------------------
# Plot
# ----------------------------
plt.figure(figsize=(14, 10))
sns.heatmap(
    matrix_norm,
    cmap="Blues",
    linewidths=0.4
)

plt.title("Normalized ISCO × DigComp Domain Heatmap")
plt.xlabel("DigComp Domains")
plt.ylabel("ISCO Occupations")
plt.tight_layout()
plt.show()
