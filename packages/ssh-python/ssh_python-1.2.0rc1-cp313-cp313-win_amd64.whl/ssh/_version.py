
import json

version_json = '''
{"date": "2025-10-11T12:45:16.618229", "dirty": false, "error": null, "full-revisionid": "e3d584ead70f913c84c0a5cd2a387f487d189904", "version": "1.2.0rc1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

