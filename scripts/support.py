import json


def get_json(path):
    with open(path) as f:
        return json.loads(f.read())

