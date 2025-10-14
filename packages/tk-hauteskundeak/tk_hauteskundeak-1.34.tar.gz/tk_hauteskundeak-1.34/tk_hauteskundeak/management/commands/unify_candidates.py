from django.core.management.base import BaseCommand
from tk_hauteskundeak.models import (
    Alderdia,
)
import csv
import os
import json
from django.utils.text import slugify
from django.conf import settings

CANDIDATES_CSV = "/home/csmant/django/buildout/csv/candidaturas.csv"


class Command(BaseCommand):
    help = "Alderdien zerrenda bateratua sortzeko"

    def handle(self, *args, **options):
        alderdia_ids = {}
        with open(CANDIDATES_CSV) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=";")
            for row in spamreader:
                print("%s, %s, %s" % (row[1], row[2].strip(), row[3].strip()))
                if row[1] not in alderdia_ids:
                    alderdia = Alderdia()
                    alderdia.izena = row[3].strip()
                    alderdia.akronimoa = row[2][:30]
                    alderdia.slug = slugify(alderdia.izena)
                    alderdia.slug_list = alderdia.slug
                    alderdia_ids.update({row[1]: alderdia.slug})
                else:
                    alderdia = Alderdia.objects.filter(slug=alderdia_ids[row[1]]).first()
                    slug_list = alderdia.slug_list.split(",")
                    slug = slugify(row[3].strip())
                    if slug not in slug_list:
                        alderdia.slug_list = alderdia.slug_list + "," + slug

                alderdia.save()
