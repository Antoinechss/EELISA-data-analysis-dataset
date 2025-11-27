import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from config import SEARCH_KEYWORDS_TR

BASE_URL = "https://www.yenibiris.com/is-ilanlari"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Target count 
TARGET_TURKEY = 700
JOBS_PER_KEYWORD = 15

# ============================================================
# SCRAPE ONE KEYWORD
# ============================================================
def scrape_keyword(keyword, max_per_keyword=JOBS_PER_KEYWORD):
    print(f"\n=== SCRAPING KEYWORD: {keyword} ===")
    all_jobs = []
    seen_urls = set()
    page = 1

    while len(all_jobs) < max_per_keyword:
        url = f"{BASE_URL}?q={keyword}&sayfa={page}"
        print(f"[Yenibiris] {keyword} | Page {page}")

        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            print("Connection error, stopping this keyword.")
            break

        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select(".listViewRows")

        start_len = len(all_jobs)  # count before parsing this page

        for row in rows:
            title_tag = row.select_one("a.gtmTitle")
            if not title_tag:
                continue

            job_url = title_tag["href"]
            if job_url in seen_urls:
                continue

            seen_urls.add(job_url)

            company_tag = row.select_one(".jobCompanyLnk")
            location_tag = row.select_one(".fs16.gtmLocation")

            all_jobs.append({
                "keyword": keyword,
                "title": title_tag.get_text(strip=True),
                "company": company_tag.get_text(strip=True) if company_tag else None,
                "location": location_tag.get_text(strip=True) if location_tag else None,
                "url": job_url,
                "country": "TR",
                "source": "Yenibiris"
            })

            if len(all_jobs) >= max_per_keyword:
                break

        # STOP if no new jobs were added
        if len(all_jobs) == start_len:
            print("No new jobs found — stopping.")
            break

        page += 1
        time.sleep(0.8)

    print(f"Collected {len(all_jobs)} jobs for '{keyword}'\n")
    return all_jobs


# ============================================================
# SCRAPE ALL KEYWORDS
# ============================================================

def scrape_all_keywords(keywords):
    all_results = []
    for kw in keywords:
        jobs = scrape_keyword(kw)
        all_results.extend(jobs)

    df = pd.DataFrame(all_results)
    df = df.drop_duplicates(subset=["url"])
    return df


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":

    # 1. Scrape all Turkish keywords
    df = scrape_all_keywords(SEARCH_KEYWORDS_TR)
    df = df.drop_duplicates(subset=["url"])
    current_count = len(df)

    print(f"\nAfter keyword scraping: {current_count} jobs")
    print(f"Target was: {TARGET_TURKEY}")

    # 2. If still under target, try to fill in with "mühendis"
    remaining = TARGET_TURKEY - current_count

    if remaining > 0:
        print(f"\n=== Attempting to fill {remaining} more jobs with 'mühendis' ===\n")

        existing_urls = set(df["url"])

        # Scrape mühendis only once (we won't loop infinitely)
        extra_jobs = scrape_keyword("mühendis", max_per_keyword=remaining)

        # Filter only NEW URLs
        filtered = [job for job in extra_jobs if job["url"] not in existing_urls]

        print(f"Found {len(filtered)} NEW mühendis jobs")

        if len(filtered) > 0:
            df = pd.concat([df, pd.DataFrame(filtered)], ignore_index=True)
            df = df.drop_duplicates(subset=["url"])

    # 3. Final result (may be < 700 if insufficient jobs exist)
    final_count = len(df)
    print(f"\n🎯 FINAL JOB COUNT FOR TURKEY: {final_count} jobs (target was 700)")
    print("If fewer than 700 jobs were found, that is acceptable.\n")

    # 4. Save output
    df.to_csv("turkey_yenibiris_all_keywords.csv", index=False)
    print("Saved to turkey_yenibiris_all_keywords.csv")
