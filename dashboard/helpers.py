import json 

def restore_list_json(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return []
    return []

import ast
import json
import pandas as pd

def restore_list_safe(x):
    if isinstance(x, list):
        return x

    if isinstance(x, str):
        x = x.strip()
        if x == "":
            return []

        # Try Python literal (your case)
        try:
            return ast.literal_eval(x)
        except Exception:
            pass

        # Try JSON as fallback
        try:
            return json.loads(x)
        except Exception:
            return []

    return []
