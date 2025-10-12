
import json

version_json = '''
{"date": "2025-10-11T15:24:03.988961", "dirty": false, "error": null, "full-revisionid": "ca6af52e5d1a8b081bc371544628af9e448f1336", "version": "1.2.0"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

