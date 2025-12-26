import os
import json
import time
import pandas as pd
from openai import OpenAI

MODEL_NAME = "gpt-4.1-mini"
SLEEP_BETWEEN_CALLS = 0.8
MAX_DESC_CHARS = 3000

JOB_EXTRACTIONS_PATH = (
    "/Users/antoinechosson/Desktop/EELISA/"
    "EELISA-Data-analysis/outputs/job_extractions.jsonl"
)

ISCED_PATH = (
    "/Users/antoinechosson/Desktop/EELISA/"
    "EELISA-Data-analysis/processing/education_classification/ISCED.csv"
)

OUTPUT_PATH = (
    "/Users/antoinechosson/Desktop/EELISA/"
    "EELISA-Data-analysis/outputs/isced_classification.jsonl"
)

client = OpenAI()

# -----------------------
# LOAD ISCED TAXONOMY
# -----------------------

isced_df = pd.read_csv(ISCED_PATH, dtype=str)
isced_df = isced_df[
    [
        "Broad field code",
        "Broad field name",
        "Narrow field code",
        "Narrow field name",
    ]
].drop_duplicates()

def build_isced_prompt_text(df: pd.DataFrame) -> str:
    return "\n".join(
        f'{r["Broad field code"]} – {r["Broad field name"]} → '
        f'{r["Narrow field code"]} – {r["Narrow field name"]}'
        for _, r in df.iterrows()
    )

ISCED_LIST_TEXT = build_isced_prompt_text(isced_df)

# -----------------------
# PROMPTS
# -----------------------

SYSTEM_PROMPT = """
You are an expert in international education classification.

Classify the required education field of a job into the
International Standard Classification of Education – Fields of Education and Training (ISCED-F).

Rules:
- Use only the provided ISCED categories.
- Do not invent categories.
- Do not guess.
- If the education field does not clearly match, return null for all fields.
- Prefer the education_field when provided.
- Use job title and description only as context.
- Return valid JSON with the specified keys only.
"""

def build_user_prompt(job_title, education_field, description, isced_list):
    return f"""
ISCED CATEGORIES (BROAD → NARROW):
{isced_list}

JOB TITLE:
{job_title}

EDUCATION FIELD (if mentioned):
{education_field if education_field else "Not specified"}

FULL JOB DESCRIPTION (context only if needed):
{description[:MAX_DESC_CHARS]}

Return JSON with:
- isced_broad_code
- isced_broad_name
- isced_narrow_code
- isced_narrow_name
"""

# -----------------------
# LOAD JOBS
# -----------------------

with open(JOB_EXTRACTIONS_PATH, "r", encoding="utf-8") as f:
    jobs = [json.loads(line) for line in f]

processed_ids = set()
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                processed_ids.add(json.loads(line)["job_id"])
            except Exception:
                pass

# -----------------------
# MAIN LOOP
# -----------------------

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "a", encoding="utf-8") as out:

    total = len(jobs)
    done = len(processed_ids)
    print(f"Starting ISCED classification: {done}/{total} completed")

    for job in jobs:

        job_id = job["job_id"]
        if job_id in processed_ids:
            continue

        print(f"Processing job_id={job_id} ({done + 1}/{total})")

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": build_user_prompt(
                            job.get("job_title", ""),
                            job.get("education_field"),
                            job.get("full_description", ""),
                            ISCED_LIST_TEXT
                        )
                    }
                ]
            )
            isced = json.loads(response.choices[0].message.content)

        except Exception:
            isced = {
                "isced_broad_code": None,
                "isced_broad_name": None,
                "isced_narrow_code": None,
                "isced_narrow_name": None
            }

        out.write(json.dumps({
            "job_id": job_id,
            "isced_broad_code": isced.get("isced_broad_code"),
            "isced_broad_name": isced.get("isced_broad_name"),
            "isced_narrow_code": isced.get("isced_narrow_code"),
            "isced_narrow_name": isced.get("isced_narrow_name")
        }, ensure_ascii=False) + "\n")

        out.flush()
        done += 1
        time.sleep(SLEEP_BETWEEN_CALLS)

print("ISCED classification finished.")
