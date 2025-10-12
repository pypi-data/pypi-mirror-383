import json
import os

with open(os.path.join(os.path.dirname(__file__), "licenses.json")) as f:
    LICENSES = json.load(f)
