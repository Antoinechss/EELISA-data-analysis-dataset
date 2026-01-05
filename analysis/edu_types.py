import pandas as pd
import re
import os
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Use relative paths for production readiness
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
datasets_dir = os.path.join(project_root, "datasets")

extractions = pd.read_csv(os.path.join(datasets_dir, "extractions.csv"))
eur_jobs = pd.read_csv(os.path.join(datasets_dir, "european_jobs.csv"))


PHD_REGEX = r"""
\b(phd|doctorate|doctoral)\b
\s*(in|of)?\s*
(?P<field>[A-Za-z][A-ZaZ\s/&-]{3,60})
"""

MASTER_REGEX = r"""
\b(master|msc|m\.sc)\b
(\s+degree)?\s*
(in|of)?\s*
(?P<field>[A-Za-z][A-ZaZ\s/&-]{3,60})
"""

FIELD_REGEX = r"""
(?:in|of|specializing\s+in)\s+
(?P<field>[A-Za-z][A-ZaZ\s,&/\-\(\)]{3,100})
"""

# ------------------------
# Semantic filtering of valid degree requirements
# ------------------------

INVALID_CONTEXT = [
    "students", "student", "craftsman", "craftsmen",
    "mastery", "certificate", "card", "workmaster",
    "mastercard"
]

REQUIRED_TOKENS = ["degree", " in ", " or ", " of "]

REQUIREMENT_PATTERNS = [
    "degree in",
    "degree or",
    "completed phd",
    "holding a master",
    "phd in",
    "master's degree",
    "masters degree",
    "bachelor or master",
    "phd or msc",
    "doctorate degree"
]

REJECT_PATTERNS = [
    "student",
    "studies",
    "position",
    "funded",
    "school",
    "program",
    "scrum master",
    "master the",
    "master cam",
    "master teams",
    "phd position",
    "doctoral school",
    "ing."
]

FIELD_STOP_TOKENS = [
    "ability", "experience", "skills", "knowledge",
    "working language", "are you", "you will",
    "applicants", "profile", "requirements",
    "location", "office", "salary"
]

def is_valid_degree_requirement(ctx):
    if not isinstance(ctx, str):
        return False

    t = ctx.lower()

    if not any(p in t for p in REQUIREMENT_PATTERNS):
        return False

    if any(p in t for p in REJECT_PATTERNS):
        return False

    return True

def clean_extracted_field(field):
    if not isinstance(field, str):
        return None

    f = field.strip(" ,.-")

    # Remove placeholders
    PLACEHOLDERS = [
        "relevant field",
        "one of the following fields",
        "the field of",
        "a master"
    ]
    if f.lower() in PLACEHOLDERS:
        return None

    # Cut at stop tokens
    for stop in FIELD_STOP_TOKENS:
        idx = f.lower().find(stop)
        if idx != -1:
            f = f[:idx].strip(" ,.-")

    # Too short or meaningless
    if len(f) < 4:
        return None

    return f

def extract_education_field(ctx):
    if not isinstance(ctx, str):
        return None

    match = re.search(FIELD_REGEX, ctx, re.IGNORECASE | re.VERBOSE)
    if not match:
        return None

    field = match.group("field")
    cleaned_field = clean_extracted_field(field)
    return cleaned_field

def extract_valid_degree_context(text, keyword):
    if not isinstance(text, str):
        return None

    text_lower = text.lower()

    # must contain degree syntax
    if not any(tok in text_lower for tok in REQUIRED_TOKENS):
        return None

    # reject obvious false positives
    for bad in INVALID_CONTEXT:
        if bad in text_lower:
            return None

    # extract window
    tokens = text.split()
    for i, tok in enumerate(tokens):
        if keyword.lower() in tok.lower():
            start = max(0, i - 5)
            end = min(len(tokens), i + 10)
            context = " ".join(tokens[start:end])
            
            # Apply refined filtering
            if is_valid_degree_requirement(context):
                return context
            
    return None


# Extract contexts and fields
eur_jobs["phd_context_valid"] = eur_jobs["full_description"].apply(
    lambda x: extract_valid_degree_context(x, "phd")
)

eur_jobs["master_context_valid"] = eur_jobs["full_description"].apply(
    lambda x: extract_valid_degree_context(x, "master")
)

# Extract fields from contexts
eur_jobs["phd_field"] = eur_jobs["phd_context_valid"].apply(extract_education_field)
eur_jobs["master_field"] = eur_jobs["master_context_valid"].apply(extract_education_field)

# Create clean field columns for dashboard integration
eur_jobs["education_field_phd_clean"] = eur_jobs["phd_field"]
eur_jobs["education_field_master_clean"] = eur_jobs["master_field"]

# Save the enhanced dataset
output_path = os.path.join(datasets_dir, "european_jobs_with_education_fields.csv")
eur_jobs.to_csv(output_path, index=False)
print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ Enhanced dataset saved to:")
print(f"{Fore.CYAN}{output_path}")


# Attractive output
print(f"{Fore.CYAN}{Style.BRIGHT}{'='*60}")
print(f"{Fore.CYAN}{Style.BRIGHT}🎓 EDUCATION TYPES ANALYSIS WITH FIELD EXTRACTION")
print(f"{Fore.CYAN}{Style.BRIGHT}{'='*60}")

print(f"\n{Fore.GREEN}{Style.BRIGHT}PHD Context Analysis:")
print(f"{Fore.YELLOW}{'─'*40}")
phd_results = eur_jobs["phd_context_valid"].dropna().value_counts().head(20)

for i, (context, count) in enumerate(phd_results.items(), 1):
    print(f"{Fore.WHITE}{i:2d}. {Fore.CYAN}{context:<50} {Fore.MAGENTA}({count})")

print(f"\n{Fore.GREEN}{Style.BRIGHT}PHD Fields Extracted:")
print(f"{Fore.YELLOW}{'─'*40}")
phd_fields = eur_jobs["phd_field"].dropna().value_counts().head(15)

for i, (field, count) in enumerate(phd_fields.items(), 1):
    print(f"{Fore.WHITE}{i:2d}. {Fore.LIGHTBLUE_EX}{field:<40} {Fore.MAGENTA}({count})")

print(f"\n{Fore.GREEN}{Style.BRIGHT}Master Context Analysis:")
print(f"{Fore.YELLOW}{'─'*40}")
master_results = eur_jobs["master_context_valid"].dropna().value_counts().head(20)

for i, (context, count) in enumerate(master_results.items(), 1):
    print(f"{Fore.WHITE}{i:2d}. {Fore.CYAN}{context:<50} {Fore.MAGENTA}({count})")

print(f"\n{Fore.GREEN}{Style.BRIGHT}Master Fields Extracted:")
print(f"{Fore.YELLOW}{'─'*40}")
master_fields = eur_jobs["master_field"].dropna().value_counts().head(15)

for i, (field, count) in enumerate(master_fields.items(), 1):
    print(f"{Fore.WHITE}{i:2d}. {Fore.LIGHTBLUE_EX}{field:<40} {Fore.MAGENTA}({count})")

print(f"\n{Fore.BLUE}{Style.BRIGHT}Summary Statistics:")
print(f"{Fore.WHITE}Total PHD contexts found: {Fore.GREEN}{len(phd_results)}")
print(f"{Fore.WHITE}PHD fields extracted: {Fore.GREEN}{len(phd_fields)}")
print(f"{Fore.WHITE}Total Master contexts found: {Fore.GREEN}{len(master_results)}")
print(f"{Fore.WHITE}Master fields extracted: {Fore.GREEN}{len(master_fields)}")

# Field extraction success rate
phd_extraction_rate = (len(phd_fields) / len(phd_results) * 100) if len(phd_results) > 0 else 0
master_extraction_rate = (len(master_fields) / len(master_results) * 100) if len(master_results) > 0 else 0

print(f"\n{Fore.YELLOW}{Style.BRIGHT}Field Extraction Success Rates:")
print(f"{Fore.WHITE}PHD field extraction rate: {Fore.GREEN}{phd_extraction_rate:.1f}%")
print(f"{Fore.WHITE}Master field extraction rate: {Fore.GREEN}{master_extraction_rate:.1f}%")

# Show some examples of context -> field mapping
print(f"\n{Fore.CYAN}{Style.BRIGHT}Sample Context -> Field Mappings:")
print(f"{Fore.YELLOW}{'─'*60}")

# PHD examples
phd_with_fields = eur_jobs[eur_jobs["phd_field"].notna()][["phd_context_valid", "phd_field"]].head(5)
for _, row in phd_with_fields.iterrows():
    print(f"{Fore.WHITE}Context: {Fore.CYAN}{row['phd_context_valid']}")
    print(f"{Fore.WHITE}Field:   {Fore.LIGHTBLUE_EX}{row['phd_field']}")
    print()

# Master examples
master_with_fields = eur_jobs[eur_jobs["master_field"].notna()][["master_context_valid", "master_field"]].head(5)
for _, row in master_with_fields.iterrows():
    print(f"{Fore.WHITE}Context: {Fore.CYAN}{row['master_context_valid']}")
    print(f"{Fore.WHITE}Field:   {Fore.LIGHTBLUE_EX}{row['master_field']}")
    print()
