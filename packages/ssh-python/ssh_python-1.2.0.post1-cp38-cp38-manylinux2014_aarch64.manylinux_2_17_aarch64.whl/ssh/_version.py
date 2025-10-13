
import json

version_json = '''
{"date": "2025-10-12T13:14:15.054642", "dirty": false, "error": null, "full-revisionid": "87a0b44c4d2d94b66684f2e9479e2932eb2661ea", "version": "1.2.0.post1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

