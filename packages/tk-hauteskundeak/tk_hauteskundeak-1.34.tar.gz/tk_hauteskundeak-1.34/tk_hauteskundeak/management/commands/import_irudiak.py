# -*- coding: utf-8 -*-

import csv
from django.core.management.base import BaseCommand, CommandError
from tk_hauteskundeak.models import HauteskundeMota, Hauteskundea, Alderdia
from django.template.defaultfilters import slugify
from photologue.models import Photo
from datetime import datetime
from tokikom.utils.load_images import loadUrlImage



PLAENTXIA_ARGAZKIA_URL="https://plaentxia.eus/argazkia/%d"

# mysqldump -u root -p plaentxia_tokikom tk_hauteskundeak_alderdia tk_hauteskundeak_hauteskundea tk_hauteskundeak_hauteskundeatokian tk_hauteskundeak_hauteskundeemaitzaktokian tk_hauteskundeak_hauteskundekp tk_hauteskundeak_hauteskundemota tk_hauteskundeak_hauteskundeoharrak tk_hauteskundeak_hauteskundeoharrak_hauteskundeak tk_hauteskundeak_tokia > hauteskundeak.sql
def plaentxiatik_irudiak_ekarri():

    for hmota in HauteskundeMota.objects.all():
        print hmota
        ida = hmota.irudia_id
        if ida:
            try:
                photo = loadUrlImage(PLAENTXIA_ARGAZKIA_URL%ida, format='png')
                if photo:
                    hmota.irudia = photo
                    hmota.save()
            except:
                print '#############ERROREA#########################3'
                print PLAENTXIA_ARGAZKIA_URL%ida
                hmota.irudia = None
                hmota.save()

    for ald in Alderdia.objects.all():
        ida = ald.logoa_id
        if ida:
            try:
                photo = loadUrlImage(PLAENTXIA_ARGAZKIA_URL%ida, format='png')
                if photo:
                    ald.logoa = photo
                    ald.save()
            except:
                print '#############ERROREA#########################3'
                print PLAENTXIA_ARGAZKIA_URL%ida
                ald.logoa = None
                ald.save()

    for haut in Hauteskundea.objects.all():
        ida = haut.irudia_id
        if ida:
            photo = loadUrlImage(PLAENTXIA_ARGAZKIA_URL%ida, format='png')
            try:
                if photo:
                    haut.irudia = photo
                    haut.save()
            except:
                print '#############ERROREA#########################3'
                print PLAENTXIA_ARGAZKIA_URL%ida
                haut.irudia = None
                haut.save()



class Command(BaseCommand):
    args = 'Irekiako datuak import'
    help = 'Irekiako csvak irakurtzeko'


    def handle(self, *args, **options):
        plaentxiatik_irudiak_ekarri()
