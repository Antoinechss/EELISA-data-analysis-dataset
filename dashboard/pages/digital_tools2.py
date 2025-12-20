def extract_tech_tools(text, tech_dict):
    """Extract technical tools mentioned in text with context-aware matching"""
    text = str(text).lower()
    found_tools = set()

    # Special handling for ambiguous terms
    ambiguous_terms = {
        "r": {
            "variants": ["r programming", "rstudio", "r language", "r statistical", "r software"],
            "context_required": True,
            "negative_context": ["or", "for", "are", "your", "our", "error", "mr", "dr"]
        },
        "c": {
            "variants": ["c programming", "language c", "c language", "c/c++"],
            "context_required": True
        },
        "go": {
            "variants": ["golang", "go programming", "go language"],
            "context_required": True,
            "negative_context": ["to go", "will go", "can go", "let's go", "must go"]
        }
    }

    for tool, variants in tech_dict.items():
        for v in variants:
            # Special handling for ambiguous single-letter/word terms
            if tool in ambiguous_terms:
                config = ambiguous_terms[tool]
                
                if v in ["r", "c", "go"] and len(v) <= 2:
                    # Look for programming context around the term
                    pattern = r"\b" + re.escape(v) + r"\b"
                    matches = list(re.finditer(pattern, text))
                    
                    for match in matches:
                        start, end = match.span()
                        # Get surrounding context (50 chars before and after)
                        context_start = max(0, start - 50)
                        context_end = min(len(text), end + 50)
                        context = text[context_start:context_end]
                        
                        # Check for programming-related keywords in context
                        programming_keywords = [
                            "programming", "language", "code", "coding", "developer", 
                            "software", "script", "statistical", "analysis", "data",
                            "experience", "knowledge", "proficient", "skilled",
                            "years", "experience in", "using", "with"
                        ]
                        
                        # Check if any programming keywords are in context
                        has_programming_context = any(keyword in context for keyword in programming_keywords)
                        
                        # Check for negative context that suggests it's not the programming language
                        if "negative_context" in config:
                            has_negative_context = any(neg in context for neg in config["negative_context"])
                        else:
                            has_negative_context = False
                        
                        # Only add if we have programming context and no negative context
                        if has_programming_context and not has_negative_context:
                            found_tools.add(tool)
                            break
                else:
                    # For longer, more specific variants, use normal matching
                    pattern = r"\b" + re.escape(v) + r"\b"
                    if re.search(pattern, text):
                        found_tools.add(tool)
                        break
            else:
                # Normal matching for non-ambiguous terms
                pattern = r"\b" + re.escape(v) + r"\b"
                if re.search(pattern, text):
                    found_tools.add(tool)
                    break

    return list(found_tools)