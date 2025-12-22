import pandas as pd

# ============================================================
# LOAD INPUT (ISCO-level TF-IDF phrases)
# ============================================================
isco_phrases = pd.read_csv("isco_top_phrases.csv")

# ============================================================
# OFFICIAL FRAMEWORK STRUCTURES (UNCHANGED)
# ============================================================

GREENCOMP_FRAMEWORK = [
    ("Embodying sustainability values",
     ["Valuing sustainability", "Supporting fairness", "Promoting nature"]),
    ("Embracing complexity in sustainability",
     ["Systems thinking", "Problem framing", "Critical thinking"]),
    ("Envisioning sustainable futures",
     ["Futures literacy", "Adaptability", "Exploratory thinking"]),
    ("Acting for sustainability",
     ["Political agency", "Collective action", "Individual initiative"])
]

DIGCOMP_FRAMEWORK = [
    ("Information and digital literacy",
     ["Browsing, searching and filtering data, information and digital content",
      "Evaluating data, information and digital content",
      "Managing data, information and digital content"]),
    ("Communication and collaboration",
     ["Interacting through digital technologies",
      "Sharing through digital technologies",
      "Engaging in citizenship through digital technologies",
      "Collaborating through digital technologies",
      "Netiquette",
      "Managing digital identity"]),
    ("Digital content creation",
     ["Programming",
      "Copyright and licences",
      "Integrating and re-elaborating digital content",
      "Developing digital content"]),
    ("Safety",
     ["Protecting devices",
      "Protecting personal data and privacy",
      "Protecting health and well-being",
      "Protecting the environment"]),
    ("Problem-solving",
     ["Solving technical problems",
      "Identifying needs and technological responses",
      "Creatively using digital technologies",
      "Identifying digital competence gaps"])
]

# ============================================================
# COMPETENCE-LEVEL KEYWORD OPERATIONALISATION
# ============================================================

GREENCOMP_COMPETENCE_KEYWORDS = {
    "Valuing sustainability": {"sustainability", "environment", "environmental"},
    "Supporting fairness": {"fairness", "equity", "inclusion"},
    "Promoting nature": {"nature", "biodiversity", "ecosystem"},

    "Systems thinking": {"systems", "processes", "interdependencies"},
    "Problem framing": {"problem", "analysis", "evaluation"},
    "Critical thinking": {"critical", "assessment", "judgement"},

    "Futures literacy": {"future", "forecast", "scenario"},
    "Adaptability": {"adaptability", "flexibility", "change"},
    "Exploratory thinking": {"innovation", "research", "experimentation"},

    "Political agency": {"policy", "regulation", "governance"},
    "Collective action": {"collaboration", "collective", "coordination"},
    "Individual initiative": {"initiative", "autonomy", "responsibility"}
}

DIGCOMP_COMPETENCE_KEYWORDS = {
    "Browsing, searching and filtering data, information and digital content":
        {"data", "information", "search"},
    "Evaluating data, information and digital content":
        {"analysis", "evaluation", "quality"},
    "Managing data, information and digital content":
        {"data_management", "databases", "documentation"},

    "Interacting through digital technologies":
        {"communication", "platforms"},
    "Sharing through digital technologies":
        {"sharing", "collaboration"},
    "Engaging in citizenship through digital technologies":
        {"citizenship", "participation"},
    "Collaborating through digital technologies":
        {"collaboration", "teamwork"},
    "Netiquette":
        {"netiquette", "online_behaviour"},
    "Managing digital identity":
        {"identity", "profile", "account"},

    "Programming":
        {"programming", "coding", "software_development"},
    "Copyright and licences":
        {"copyright", "licence"},
    "Integrating and re-elaborating digital content":
        {"integration", "re_elaboration"},
    "Developing digital content":
        {"development", "design", "content_creation"},

    "Protecting devices":
        {"security", "devices"},
    "Protecting personal data and privacy":
        {"privacy", "gdpr", "compliance"},
    "Protecting health and well-being":
        {"wellbeing", "health"},
    "Protecting the environment":
        {"environment", "energy"},

    "Solving technical problems":
        {"maintenance", "troubleshooting"},
    "Identifying needs and technological responses":
        {"needs", "solutions"},
    "Creatively using digital technologies":
        {"innovation", "creative"},
    "Identifying digital competence gaps":
        {"training", "skills_gap"}
}

# ============================================================
# MAPPING FUNCTIONS
# ============================================================

def map_competences(phrase, competence_dict):
    tokens = set(phrase.split("_"))
    return [
        comp for comp, kws in competence_dict.items()
        if tokens & kws
    ]

def competences_to_domains(competences, framework):
    domains = []
    for domain, comp_list in framework:
        if any(c in comp_list for c in competences):
            domains.append(domain)
    return domains

# ============================================================
# APPLY MAPPING
# ============================================================

isco_phrases["greencomp_competences"] = isco_phrases["noun_phrase"].apply(
    lambda p: map_competences(p, GREENCOMP_COMPETENCE_KEYWORDS)
)

isco_phrases["greencomp_domains"] = isco_phrases["greencomp_competences"].apply(
    lambda comps: competences_to_domains(comps, GREENCOMP_FRAMEWORK)
)

isco_phrases["digcomp_competences"] = isco_phrases["noun_phrase"].apply(
    lambda p: map_competences(p, DIGCOMP_COMPETENCE_KEYWORDS)
)

isco_phrases["digcomp_domains"] = isco_phrases["digcomp_competences"].apply(
    lambda comps: competences_to_domains(comps, DIGCOMP_FRAMEWORK)
)

# ============================================================
# SAVE OUTPUT
# ============================================================

isco_phrases.to_csv("isco_phrases_mapped_frameworks.csv", index=False)

print("Saved: isco_phrases_mapped_frameworks.csv")
print("Rows:", isco_phrases.shape[0])
print("\nExample rows:")
print(isco_phrases.head(5))
