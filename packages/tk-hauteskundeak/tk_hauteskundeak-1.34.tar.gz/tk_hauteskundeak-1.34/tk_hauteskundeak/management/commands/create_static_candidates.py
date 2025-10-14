from django.core.management.base import BaseCommand
from tk_hauteskundeak.models import (
    Alderdia,
)
import os
import json
from django.conf import settings


def create_candidates_file():
    alderdiak_json = {}
    for alderdia in Alderdia.objects.all():
        if alderdia.slug_list:
            slug_list = alderdia.slug_list.split(",")
        else:
            slug_list = [alderdia.slug]
        for slug in slug_list:
            alderdiak_json.update({slug: alderdia.slug})

    directory = os.path.join(settings.STATIC_ROOT, "tk_hauteskundeak")
    if not os.path.exists(directory):
        os.mkdir(directory)
    path = os.path.join(directory, "alderdiak_list.json")
    with open(path, "w") as fp:
        fp.write(json.dumps(alderdiak_json))


class Command(BaseCommand):
    help = "Alderdien json zerrenda zerrenda estatikoa sortzeko"

    def handle(self, *args, **options):
        create_candidates_file()
