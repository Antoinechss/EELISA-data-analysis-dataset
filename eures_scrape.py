import requests
import pandas as pd
import time
import math
from bs4 import BeautifulSoup
from nuts import COUNTRY_CODE_TO_NAME, NUTS_REGIONS
from config import MODE, EURES_URL, HEADERS, COUNTRY_CODES, EELISA_COUNTRIES, RESULTS_PER_PAGE, MAX_JOBS_PER_COUNTRY, REQUEST_DELAY, OUTPUT_CSV, DOMAIN_PATTERNS, SEARCH_KEYWORDS

# -----------------------------
# CONFIGS
# -----------------------------

if MODE == "test":
    print("\n=== RUNNING IN TEST MODE ===\n")
    SELECTED_COUNTRIES = ["fr"]     
    SELECTED_KEYWORDS = ["engineer"]
else:
    print("\n=== RUNNING FULL SCRAPER ===\n")
    SELECTED_COUNTRIES = COUNTRY_CODES
    SELECTED_KEYWORDS = SEARCH_KEYWORDS


# -----------------------------
# DOMAIN CLASSIFIER
# -----------------------------


def classify_domain(title: str | None, description: str | None) -> str:
    text = (title or "").lower() + " " + (description or "").lower()

    for domain, patterns in DOMAIN_PATTERNS:
        if any(p in text for p in patterns):
            return domain

    # Fallback: Research & Academia if clearly academic
    if any(w in text for w in ["phd", "postdoc", "thesis", "doctoral", "university"]):
        return "Research & Academia"

    return "Other / Undefined"


# -----------------------------
# HELPERS
# -----------------------------

def clean_html(html_text: str | None) -> str:
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(" ", strip=True)

def infer_country_from_location_map(location_map: dict | None) -> str | None:
    if not location_map:
        return None
    try:
        code = next(iter(location_map.keys()))
        return COUNTRY_CODE_TO_NAME.get(code.lower(), code.upper())
    except StopIteration:
        return None
    
def extract_region_from_location_map(location_map: dict | None) -> str | None:
    """
    Convert NUTS location code (FRL04) to Region name (Provence-Alpes-Côte d'Azur).
    """
    if not location_map:
        return None

    try:
        country_code = next(iter(location_map.keys()))
        nuts_list = location_map[country_code]

        if not nuts_list:
            return None

        # reads the first 3 characters of the string
        nuts_code = nuts_list[0]       
        nuts_prefix = nuts_code[:3]   

        return NUTS_REGIONS.get(nuts_prefix, nuts_prefix)
    except Exception:
        return None

# -----------------------------
# CORE SCRAPING LOGIC
# -----------------------------

def fetch_page(country_code: str | None,
               keyword: str,
               page: int,
               results_per_page: int = RESULTS_PER_PAGE) -> dict | None:
    """
    Fetch one page of results for a given country & keyword.
    """
    payload = {
        "resultsPerPage": results_per_page,
        "page": page,
        "sortSearch": "BEST_MATCH",
        "keywords": [
            {
                "keyword": keyword,
                "specificSearchCode": "EVERYWHERE"
            }
        ],
        "locationCodes": [country_code] if country_code else [],
        "educationAndQualificationLevelCodes": [],
        "euresFlagCodes": [],
        "occupationUris": [],
        "otherBenefitsCodes": [],
        "positionOfferingCodes": [],
        "positionScheduleCodes": [],
        "publicationPeriod": None,
        "requiredExperienceCodes": [],
        "requiredLanguages": [],
        "sectorCodes": [],
        "skillUris": []
    }

    r = requests.post(EURES_URL, json=payload, headers=HEADERS, timeout=20)
    print(f"[{country_code or 'ALL'} | {keyword} | page {page}] Status: {r.status_code}")

    if r.status_code != 200:
        print("  -> Error response (first 300 chars):", r.text[:300])
        return None

    try:
        return r.json()
    except Exception as e:
        print("  -> JSON decode error:", e)
        print(r.text[:300])
        return None


def fetch_jobs_for_country(country_code: str,
                           max_jobs: int = MAX_JOBS_PER_COUNTRY) -> list[dict]:
    """
    Fetch up to max_jobs for a given country across all SEARCH_KEYWORDS.
    """
    all_jobs = []
    seen_ids = set()

    for kw in SEARCH_KEYWORDS:
        page = 1
        while len(all_jobs) < max_jobs:
            data = fetch_page(country_code, kw, page, RESULTS_PER_PAGE)
            time.sleep(REQUEST_DELAY)

            if not data:
                break

            jvs = data.get("jvs", [])
            if not jvs:
                break

            for job in jvs:
                job_id = job.get("id")
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                raw_desc = job.get("description", "")
                clean_desc = clean_html(raw_desc)
                title = job.get("title", "")

                country_name = infer_country_from_location_map(job.get("locationMap"))
                domain = classify_domain(title, clean_desc)

                # employer may be None
                employer = job.get("employer")
                company_name = employer.get("name") if isinstance(employer, dict) else None

                all_jobs.append({
                    "job_id": job_id,
                    "job_title": title,
                    "date": job.get("dateOfPublication") or job.get("creationDate"),
                    "company_name": company_name,
                    "country": country_name,
                    "country_code": country_code.upper(),
                    "region": extract_region_from_location_map(job.get("locationMap")),
                    "field": domain,
                    "full_description": clean_desc,
                })



                if len(all_jobs) >= max_jobs:
                    break

            # Stop if fewer results than page size → last page
            if len(jvs) < RESULTS_PER_PAGE:
                break

            page += 1

    return all_jobs


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    all_rows = []

    for code in SELECTED_COUNTRIES:
        print(f"\n========== Scraping country: {code.upper()} ==========")
        jobs = fetch_jobs_for_country(code, max_jobs=MAX_JOBS_PER_COUNTRY)
        print(f"  -> Collected {len(jobs)} jobs for {code.upper()}")
        all_rows.extend(jobs)

    print(f"\nTotal jobs collected: {len(all_rows)}")

    # Load existing file if it exists (to preserve past scraping)

    try:
        existing_df = pd.read_csv(OUTPUT_CSV)
    except FileNotFoundError:
        existing_df = pd.DataFrame()

    # Combine old + new
    df = pd.concat([existing_df, pd.DataFrame(all_rows)], ignore_index=True)

    # Remove duplicates based on job_id
    df.drop_duplicates(subset="job_id", inplace=True)

    # Save
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved dataset to {OUTPUT_CSV} (unique jobs: {len(df)})")


