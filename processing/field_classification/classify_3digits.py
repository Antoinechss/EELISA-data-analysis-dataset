import pandas as pd
from openai import OpenAI
import os
import time
import json
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Load data
isco_classification = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/processing/field_classification/ISCO_3_digits.csv'
dataset = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/datasets/european_jobs.csv'
cache_file = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/processing/field_classification/classification_cache.json'

isco = pd.read_csv(isco_classification)
df = pd.read_csv(dataset)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create ISCO reference text for the prompt
isco_reference = "\n".join([f"{row['3_digit_code']}: {row['3_digit_label']}" for _, row in isco.iterrows()])

# Create ISCO lookup dictionary for labels
isco_lookup = dict(zip(isco['3_digit_code'], isco['3_digit_label']))

# Load cache if it exists
try:
    with open(cache_file, 'r') as f:
        cache = json.load(f)
    print(f"Loaded cache with {len(cache)} previously classified jobs")
except FileNotFoundError:
    cache = {}
    print("No cache found, starting fresh")

def save_cache():
    """Save current cache to file"""
    with open(cache_file, 'w') as f:
        json.dump(cache, f, indent=2)

def get_cache_key(job):
    """Generate unique cache key for a job"""
    return f"{job['job_title']}||{str(job['full_description'])[:500]}"

def classify_jobs_batch(jobs_batch):
    """
    Classify a batch of jobs using ISCO 3-digit codes
    """
    
    # Check cache first
    cached_results = []
    uncached_jobs = []
    uncached_indices = []
    
    for i, job in enumerate(jobs_batch):
        cache_key = get_cache_key(job)
        if cache_key in cache:
            cached_results.append((i, cache[cache_key]))
        else:
            uncached_jobs.append(job)
            uncached_indices.append(i)
    
    # If all jobs are cached, return cached results
    if not uncached_jobs:
        result = [None] * len(jobs_batch)
        for idx, classification in cached_results:
            result[idx] = classification
        return result
    
    # Prepare job descriptions for uncached jobs
    job_descriptions = []
    for i, job in enumerate(uncached_jobs):
        title = job['job_title']
        description = job['full_description']
        description_text = str(description)[:1500] if pd.notna(description) else "No description provided"
        job_text = f"{i+1}. Title: {title}\n   Description: {description_text}"
        job_descriptions.append(job_text)
    
    jobs_text = "\n\n".join(job_descriptions)
    
    prompt = f"""You are an expert job classifier. Classify these jobs according to ISCO-08 3-digit occupation codes.

ISCO-08 3-digit codes available:
{isco_reference}

Jobs to classify:
{jobs_text}

For each job, analyze BOTH the job title AND the full description carefully to determine the most appropriate ISCO 3-digit code.
Pay special attention to:
- Required skills and qualifications
- Job responsibilities 
- Industry context
- Level of expertise required

Respond with ONLY a JSON array of ISCO codes in the same order as the jobs, like:
["214", "351", "242", "131"]

Use only the 3-digit codes from the list above. If uncertain, choose the closest match.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean response if it has markdown formatting
        if result.startswith("```"):
            lines = result.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('['):
                    result = '\n'.join(lines[i:])
                    break
            if result.endswith("```"):
                result = result[:-3]
        
        new_classifications = json.loads(result)
        
        # Validate we have the right number of classifications
        if len(new_classifications) != len(uncached_jobs):
            print(f"Warning: Expected {len(uncached_jobs)} classifications, got {len(new_classifications)}")
            return ["999"] * len(jobs_batch)
        
        # Cache the new results
        for job, classification in zip(uncached_jobs, new_classifications):
            cache_key = get_cache_key(job)
            cache[cache_key] = classification
        
        # Combine cached and new results
        result = [None] * len(jobs_batch)
        
        # Add cached results
        for idx, classification in cached_results:
            result[idx] = classification
        
        # Add new results
        for i, classification in enumerate(new_classifications):
            result[uncached_indices[i]] = classification
        
        return result
    
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return ["999"] * len(jobs_batch)
    except Exception as e:
        print(f"Error classifying batch: {e}")
        return ["999"] * len(jobs_batch)

# Initialize ISCO columns
if 'isco_3_digit' not in df.columns:
    df['isco_3_digit'] = ""
if 'isco_3_digit_label' not in df.columns:
    df['isco_3_digit_label'] = ""

# Check which jobs are already classified
already_classified = df['isco_3_digit'].notna() & (df['isco_3_digit'] != "")
start_index = 0

if already_classified.any():
    last_classified = df[already_classified].index.max()
    start_index = last_classified + 1
    print(f"Found {already_classified.sum()} already classified jobs. Resuming from job {start_index + 1}")

# Process in batches
batch_size = 5
remaining_jobs = len(df) - start_index
total_batches = (remaining_jobs - 1) // batch_size + 1 if remaining_jobs > 0 else 0

print(f"Classifying {remaining_jobs} remaining jobs into ISCO 3-digit codes...")
print(f"Processing {total_batches} batches of {batch_size} jobs each")

for i in range(start_index, len(df), batch_size):
    batch_jobs = df.iloc[i:i+batch_size].to_dict('records')
    batch_num = ((i - start_index) // batch_size) + 1
    
    print(f"\nBatch {batch_num}/{total_batches}")
    print(f"Processing jobs {i+1} to {min(i+batch_size, len(df))}")
    
    classifications = classify_jobs_batch(batch_jobs)
    
    # Apply classifications to dataframe
    for j, isco_code in enumerate(classifications):
        if i + j < len(df):
            df.loc[i + j, 'isco_3_digit'] = isco_code
            # Add the label
            label = isco_lookup.get(isco_code, "Unknown")
            df.loc[i + j, 'isco_3_digit_label'] = label
    
    # Save progress every 10 batches
    if batch_num % 10 == 0:
        df.to_csv(dataset, index=False)
        save_cache()
        print(f"Saved progress... ({batch_num * batch_size} jobs processed)")
    
    # Rate limiting delay
    time.sleep(2)

# Save final results
df.to_csv(dataset, index=False)
save_cache()

print(f"\n" + "="*50)
print("CLASSIFICATION COMPLETE!")
print("="*50)

# Show classification statistics
isco_counts = df['isco_3_digit'].value_counts()
print(f"Classified {len(df)} jobs into {len(isco_counts)} different ISCO codes")

print("\nTop 10 ISCO classifications:")
for code, count in isco_counts.head(10).items():
    label = isco_lookup.get(code, "Unknown")
    print(f"  {code}: {label} ({count} jobs)")

print(f"\nSaved classified dataset to: {dataset}")
print(f"Cache saved to: {cache_file}")