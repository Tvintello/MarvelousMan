import json


def get_json(path):
    with open(path, encoding="utf8") as f:
        f = f.read()
        return json.loads(f)

