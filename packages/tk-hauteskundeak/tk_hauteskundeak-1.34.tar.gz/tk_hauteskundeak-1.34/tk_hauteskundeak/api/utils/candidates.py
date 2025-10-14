import json
import os
from django.conf import settings

FILE_PATH = os.path.join(
    settings.STATIC_ROOT, "tk_hauteskundeak/alderdiak_list.json"
)


def get_candidates_json():
    with open(FILE_PATH, "r") as fp:
        return json.loads(fp.read())


def update_candidates_json(candidates_json):
    with open(FILE_PATH, "w") as fp:
        fp.write(json.dumps(candidates_json))
