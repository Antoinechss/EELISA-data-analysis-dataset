import pandas as pd
from config import FIELD_KEYWORDS
from rapidfuzz import fuzz

# ------------------------
# Loading Dataset 
# ------------------------

jobs_dataset = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/eures_jobs_full.csv'

df = pd.read_csv(jobs_dataset)

# ------------------------
# Timestamp to proper date formating 
# ------------------------

# def parse_date(val):
#     try:
#         # Try to parse as integer timestamp (milliseconds)
#         if pd.notnull(val) and str(val).isdigit() and len(str(val)) > 10:
#             return pd.to_datetime(int(val), unit='ms')
#         # Try to parse as normal date string
#         return pd.to_datetime(val, errors='coerce')
#     except Exception:
#         return pd.NaT

# df['date'] = df['date'].apply(parse_date).dt.strftime('%Y-%m-%d')
# df.to_csv('/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/eures_jobs_full.csv', index=False)


# Convert 'date' to datetime first (handles both strings and timestamps)
def parse_date(val):
    try:
        if pd.notnull(val) and str(val).isdigit() and len(str(val)) > 10:
            return pd.to_datetime(int(val), unit='ms')
        return pd.to_datetime(val, errors='coerce')
    except Exception:
        return pd.NaT

df['date'] = df['date'].apply(parse_date)

# Now filter for posts from 2022 and later
df = df[df['date'] >= pd.to_datetime("2022-01-01")]

# Calculate the average date
average_timestamp = df['date'].dropna().astype(int).mean()
average_date = pd.to_datetime(average_timestamp)

print("Average date:", average_date.strftime('%Y-%m-%d'))
print(df.shape)
print(df['date'].min())
print(df['date'].max())
print(df.shape)

# ------------------------
# Translation to eng default lang 
# ------------------------

# ------------------------
# Infering field from job description
# ------------------------

# def infer_field(description):
#     desc = str(description).lower()
#     for field, keywords in FIELD_KEYWORDS.items():
#         for kw in keywords:
#             if kw in desc:
#                 return field
#     return "Other / Undefined"


# mask = df['field'] == "Other / Undefined"
# df.loc[mask, 'field'] = df.loc[mask, 'full_description'].apply(infer_field)

# df.to_csv('/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/eures_jobs_full.csv', index=False)

# ------------------------
# Removing duplicate job offers
# ------------------------

# df = df.drop_duplicates(subset=["job_title", "company_name", "full_description"])

# df["block"] = df["job_title"].str[:10] + df["company_name"].str[:10]  

# to_drop = set()
# for block_val, block_df in df.groupby("block"):
#     idxs = block_df.index.tolist()
#     for i, idx_i in enumerate(idxs):
#         if idx_i in to_drop:
#             continue
#         for idx_j in idxs[i+1:]:
#             if idx_j in to_drop:
#                 continue
#             score = fuzz.token_set_ratio(
#                 str(df.at[idx_i, 'job_title']) + str(df.at[idx_i, 'company_name']) + str(df.at[idx_i, 'full_description']),
#                 str(df.at[idx_j, 'job_title']) + str(df.at[idx_j, 'company_name']) + str(df.at[idx_j, 'full_description'])
#             )
#             if score > 95:
#                 to_drop.add(idx_j)
# df = df.drop(list(to_drop))
# df = df.drop(columns="block")
# df.to_csv("eures_jobs_full_deduped.csv", index=False)

