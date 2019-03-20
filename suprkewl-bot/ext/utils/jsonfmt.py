import json

def format_json(string: str):
    return json.dumps(string, indent=2, ensure_ascii=False, sort_keys=True)
