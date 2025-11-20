import pandas as pd
from config import FIELD_KEYWORDS

# ------------------------
# Loading Dataset 
# ------------------------

jobs_dataset = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/eures_jobs_full.csv'

df = pd.read_csv(jobs_dataset)

# ------------------------
# Translation to eng default lang 
# ------------------------

# ------------------------
# Infering field from job description
# ------------------------

def infer_field(description):
    desc = str(description).lower()
    for field, keywords in FIELD_KEYWORDS.items():
        for kw in keywords:
            if kw in desc:
                return field
    return "Other / Undefined"


mask = df['field'] == "Other / Undefined"
df.loc[mask, 'field'] = df.loc[mask, 'full_description'].apply(infer_field)

df.to_csv('/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/eures_jobs_full.csv', index=False)

# ------------------------
# Removing duplicate job offers
# Different ID but same job posted twice 
# ------------------------