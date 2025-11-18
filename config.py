MODE = "test"

EURES_URL = "https://europa.eu/eures/api/jv-searchengine/public/jv-search/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://europa.eu",
    "Referer": "https://europa.eu/eures/portal/jv-se/search"
}

COUNTRY_CODES = [
    "be", "bg", "cz", "dk", "de", "ee", "ie", "el", "es", "fr",
    "hr", "it", "cy", "lv", "lt", "lu", "hu", "mt", "nl", "at",
    "pl", "pt", "ro", "si", "sk", "fi", "se", "no", "ch"
]

EELISA_COUNTRIES = {"fr", "hu", "ro", "de", "it", "tr", "ch"}

# Limits
RESULTS_PER_PAGE = 15
MAX_JOBS_PER_COUNTRY = 100    
JOBS_PER_KEYWORD = 2  
REQUEST_DELAY = 1.0             

OUTPUT_CSV = "eures_jobs_full.csv"

SEARCH_KEYWORDS = [
    # Engineering — general and specific
    "engineer", "engineering", "mechanical", "electrical", 
    "automation", "robotics", "mechatronics",

    # Digital & Computing
    "software", "developer", "programmer", 
    "cloud", "devops", "cybersecurity", "network",

    # Data, AI & ML
    "data", "data science", "data analyst", 
    "machine learning", "ai", "artificial intelligence",
    "deep learning",

    # Research & Academia
    "research", "scientist", "laboratory", 
    "PhD", "postdoc", "quantitative", "mathematics",

    # Sustainability & Green Transition
    "sustainability", "renewable", "solar", 
    "wind", "energy", "environmental", "climate",

    # Industry & Advanced Manufacturing
    "manufacturing", "industrial", "quality",
    "chemistry", "materials", "biomedical",

    # Business & Innovation
    "innovation", "product manager", "project manager",
]

DOMAIN_PATTERNS = [
    ("Data Science", [
        "data scientist", "data science", "data analyst", "big data", "data mining"
    ]),
    ("Artificial Intelligence", [
        "artificial intelligence", "ai engineer", "ai researcher", "ai developer"
    ]),
    ("Machine Learning", [
        "machine learning", "ml engineer", "ml scientist", "deep learning"
    ]),
    ("Software Engineering", [
        "software engineer", "software developer", "fullstack", "full-stack",
        "backend developer", "front-end developer", "frontend developer",
        "dev software", "embedded software", "software development"
    ]),
    ("Cybersecurity & Information Security", [
        "cybersecurity", "cyber security", "information security", "infosec",
        "security engineer", "soc analyst", "penetration tester", "pentester"
    ]),
    ("Cloud, DevOps & Systems Engineering", [
        "devops", "site reliability engineer", "sre", "cloud engineer",
        "cloud architect", "systems engineer", "system engineer", "kubernetes",
        "docker", "platform engineer"
    ]),
    ("Telecommunications & Networking", [
        "network engineer", "networking", "telecom", "telecommunications",
        "5g", "radio access", "rf engineer"
    ]),
    ("Robotics & Automation", [
        "robotics", "robot engineer", "automation engineer",
        "industrial automation", "cobot", "mechatronics"
    ]),
    ("Mechanical & Materials Engineering", [
        "mechanical engineer", "mechanical engineering",
        "design engineer", "cae engineer", "cad engineer",
        "materials engineer", "material engineer", "mechanical design"
    ]),
    ("Electrical & Electronics Engineering", [
        "electrical engineer", "electronics engineer", "power electronics",
        "hw engineer", "hardware engineer", "analog design", "fpga", "asics"
    ]),
    ("Civil Engineering", [
        "civil engineer", "civil engineering", "structural engineer",
        "urban planning", "geotechnical", "construction engineer"
    ]),
    ("Chemical & Process Engineering", [
        "chemical engineer", "process engineer", "process engineering",
        "chemistry", "process design", "downstream processing"
    ]),
    ("Aeronautics & Aerospace Engineering", [
        "aerospace", "aeronautical", "avionics", "satellite", "spacecraft",
        "airbus", "boeing", "helicopter"
    ]),
    ("Energy Engineering", [
        "energy engineer", "renewable energy", "wind farm", "solar pv",
        "energy systems", "power plant", "grid integration"
    ]),
    ("Industrial & Operations Engineering", [
        "industrial engineer", "operations engineer", "process improvement",
        "lean manufacturing", "supply chain", "logistics engineer"
    ]),
    ("Biomedical Engineering", [
        "biomedical engineer", "medical device", "medtech", "bioengineering",
        "healthcare technology"
    ]),
    ("Sustainability & Green Technologies", [
        "sustainability", "sustainable", "green tech", "climate", "esg",
        "environmental impact", "carbon footprint"
    ]),
    ("Earth & Environmental Systems", [
        "environmental engineer", "geoscience", "earth observation",
        "hydrology", "ecosystem", "climate scientist", "meteorology"
    ]),
    ("Business & Innovation", [
        "product manager", "project manager", "innovation manager",
        "business analyst", "strategy consultant", "business development"
    ]),
    ("Research & Academia", [
        "phd", "postdoc", "post-doctoral", "research fellow",
        "assistant professor", "research associate", "laboratory researcher",
        "inria", "cnrs", "fraunhofer", "university"
    ]),
    ("Mathematics, Statistics & Quantitative Sciences", [
        "statistician", "quantitative analyst", "quant", "applied mathematics",
        "stochastic", "probability", "operations research"
    ]),
    ("Finance, Economics & Decision Science", [
        "financial engineer", "risk analyst", "portfolio", "asset management",
        "economist", "derivatives", "market risk"
    ]),
]