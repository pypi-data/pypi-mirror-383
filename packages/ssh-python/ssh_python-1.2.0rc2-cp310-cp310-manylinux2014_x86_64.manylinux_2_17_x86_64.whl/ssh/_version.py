
import json

version_json = '''
{"date": "2025-10-11T13:37:03.939399", "dirty": false, "error": null, "full-revisionid": "65890f1116eb321ed8b73aeab67108d74f1179ec", "version": "1.2.0rc2"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

