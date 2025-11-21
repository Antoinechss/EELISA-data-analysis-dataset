import pandas as pd
from scraping.config import FIELD_KEYWORDS

jobs_dataset = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/eures_jobs_full.csv'
df = pd.read_csv(jobs_dataset)

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


