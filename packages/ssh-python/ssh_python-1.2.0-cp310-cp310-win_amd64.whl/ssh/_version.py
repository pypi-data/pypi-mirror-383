
import json

version_json = '''
{"date": "2025-10-11T15:39:00.896214", "dirty": false, "error": null, "full-revisionid": "159d04f10353a6613136799a0409d9f06c1295af", "version": "1.2.0"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

