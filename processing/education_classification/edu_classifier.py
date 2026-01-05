import os
import json
import time
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Use absolute paths to avoid issues
PROJECT_ROOT = "/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis"

MODEL_NAME = "gpt-4o-mini"  # Fixed model name
SLEEP_BETWEEN_CALLS = 0.8
MAX_DESC_CHARS = 3000

# Use the enhanced European jobs dataset with education fields
JOB_DATA_PATH = (
    f"{PROJECT_ROOT}/datasets/european_jobs_with_education_fields.csv"
)
ISCED_PATH = f"{PROJECT_ROOT}/processing/education_classification/ISCED.csv"
OUTPUT_PATH = f"{PROJECT_ROOT}/outputs/isced_classification.jsonl"

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Check if API key exists
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# -----------------------
# LOAD ISCED TAXONOMY
# -----------------------

try:
    isced_df = pd.read_csv(ISCED_PATH, dtype=str)
    
    # Debug: Check actual columns
    print("Actual columns in ISCED.csv:")
    print(isced_df.columns.tolist())
    
    # Use the correct column names from the CSV
    isced_df = isced_df[
        [
            "isced_2_digits",
            "isced_2_digits_field",
            "isced_3_digits",
            "isced_3_digits_field",
        ]
    ].drop_duplicates()
    
    # Rename columns for consistency with the rest of the code
    isced_df.columns = [
        "Broad field code",
        "Broad field name",
        "Narrow field code",
        "Narrow field name"
    ]
    
    print(f"Loaded {len(isced_df)} ISCED categories")
    
except FileNotFoundError:
    raise FileNotFoundError(f"ISCED file not found at {ISCED_PATH}")
except Exception as e:
    raise Exception(f"Error loading ISCED file: {e}")

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

try:
    # Load European jobs CSV with education fields
    jobs_df = pd.read_csv(JOB_DATA_PATH, dtype=str)
    print(f"Loaded {len(jobs_df)} European jobs from CSV")
    
    # Convert to list of dictionaries for compatibility with existing code
    jobs = jobs_df.to_dict('records')
    
    # Check what education field columns are available
    education_cols = [col for col in jobs_df.columns if 'education' in col.lower()]
    print(f"Available education columns: {education_cols}")
    
except FileNotFoundError:
    raise FileNotFoundError(f"European jobs file not found at {JOB_DATA_PATH}")
except Exception as e:
    raise Exception(f"Error loading European jobs file: {e}")

processed_ids = set()
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                processed_ids.add(json.loads(line)["job_id"])
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not parse line in output file: {e}")
                continue

# -----------------------
# MAIN LOOP
# -----------------------

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "a", encoding="utf-8") as out:

    total = len(jobs)
    done = len(processed_ids)
    print(f"Starting ISCED classification: {done}/{total} completed")

    for job in jobs:

        job_id = job.get("job_id")
        if not job_id:
            print("Warning: Job missing job_id, skipping")
            continue
            
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
                            # Try different education field columns
                            job.get("education_field_phd_clean") or
                            job.get("education_field_master_clean") or
                            job.get("education_field"),
                            job.get("full_description", ""),
                            ISCED_LIST_TEXT
                        )
                    }
                ]
            )
            isced = json.loads(response.choices[0].message.content)

        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON response for job {job_id}: {e}")
            isced = {
                "isced_broad_code": None,
                "isced_broad_name": None,
                "isced_narrow_code": None,
                "isced_narrow_name": None
            }
        except Exception as e:
            print(f"Error processing job {job_id}: {e}")
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
