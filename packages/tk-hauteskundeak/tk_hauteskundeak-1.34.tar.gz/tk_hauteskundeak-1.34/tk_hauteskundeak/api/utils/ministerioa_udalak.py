import csv
import json
from io import StringIO
from tk_hauteskundeak.models import (
    Tokia,
    HauteskundeaTokian,
    Alderdia,
    HauteskundeEmaitzakTokian,
)
from django.db.models import Q
from django.utils.text import slugify
from tk_hauteskundeak.api.utils.candidates import (
    get_candidates_json,
    update_candidates_json,
)


LURRALDE_KODEAK = ["01", "20", "31", "48"]
REMOVE_COLUMN_QTY = 3


def import_ministerio_udalak(data, hauteskundea, total):
    f = StringIO(data)
    dialect = csv.Sniffer().sniff(data, delimiters=";")
    reader = csv.reader(f, dialect)

    candidates_json = get_candidates_json()

    for row in reader:

        if not total:
            if int(row[5]) != 99:
                continue
            TOWN_INFO_COLUMN_QTY = 21
            PARTY_INFO_COLUMN_BLOCK = 5
            lurralde_kodea = int(row[2])
            herri_kodea = int(row[4])
            mota = 1
            toki_izena = row[6]
            jarlekuak = int(row[21])
            errolda = int(row[10])
            boto_emaileak = int(row[13])
            baliogabeak = int(row[19])
            zuriak = int(row[17])
            eskrutinioa = int(row[12])
            alderdi_izena_index = 1
            alderdi_botoak_index = 2
            alderdi_jarlekuak_index = 4
        else:
            if row[1] != "PR" or (
                row[1] == "PR" and row[3] not in LURRALDE_KODEAK
            ):
                continue
            TOWN_INFO_COLUMN_QTY = 19
            PARTY_INFO_COLUMN_BLOCK = 8
            lurralde_kodea = int(row[3])
            herri_kodea = 0
            mota = 4
            toki_izena = row[5]
            jarlekuak = int(row[19])
            errolda = int(row[7])
            boto_emaileak = int(row[10])
            baliogabeak = int(row[16])
            zuriak = int(row[14])
            eskrutinioa = int(row[9])
            alderdi_izena_index = 1
            alderdi_botoak_index = 2
            alderdi_jarlekuak_index = 4

        if Tokia.objects.filter(
            lurralde_kodea=lurralde_kodea, herri_kodea=herri_kodea, mota=mota
        ).exists():
            tokia = Tokia.objects.get(
                lurralde_kodea=lurralde_kodea,
                herri_kodea=herri_kodea,
                mota=mota,
            )
        else:
            tokia = Tokia()
            tokia.izena = toki_izena.strip()
            tokia.slug = slugify(tokia.izena)
            tokia.lurralde_kodea = lurralde_kodea
            tokia.herri_kodea = herri_kodea
            tokia.mota = mota
            tokia.is_public = True
            tokia.save()

        if HauteskundeaTokian.objects.filter(
            hauteskundea=hauteskundea, tokia=tokia
        ).exists():
            hauteskundeaTokian = HauteskundeaTokian.objects.get(
                hauteskundea=hauteskundea, tokia=tokia
            )
        else:
            hauteskundeaTokian = HauteskundeaTokian()
            hauteskundeaTokian.hauteskundea = hauteskundea
            hauteskundeaTokian.tokia = tokia
        hauteskundeaTokian.errolda = errolda
        hauteskundeaTokian.boto_emaileak = boto_emaileak
        hauteskundeaTokian.baliogabeak = baliogabeak
        hauteskundeaTokian.zuriak = zuriak
        hauteskundeaTokian.eskrutinioa = float(eskrutinioa) / 100
        hauteskundeaTokian.jarlekuen_kopurua = jarlekuak
        hauteskundeaTokian.save()

        total_rows = len(row)
        if not total:
            total_rows -= REMOVE_COLUMN_QTY
        iterations = int(
            (total_rows - TOWN_INFO_COLUMN_QTY) / PARTY_INFO_COLUMN_BLOCK
        )
        index = TOWN_INFO_COLUMN_QTY + 1
        for iter in range(iterations):
            if row[index + alderdi_izena_index].strip() == "":
                index += PARTY_INFO_COLUMN_BLOCK
                continue
            slug = slugify(row[index + alderdi_izena_index].strip())
            if slug in candidates_json:
                alderdia = Alderdia.objects.get(slug=candidates_json[slug])
            else:
                alderdia = Alderdia()
                alderdia.izena = row[index + alderdi_izena_index].strip()
                alderdia.akronimoa = alderdia.izena[:30]
                alderdia.slug = slug
                alderdia.slug_list = slug
                alderdia.save()

                candidates_json.update({slug: slug})
                update_candidates_json(candidates_json)

            HauteskundeEmaitzakTokian.objects.filter(
                hauteskundeatokian=hauteskundeaTokian, alderdia=alderdia
            ).delete()
            hauteskundeEmaitzakTokian = HauteskundeEmaitzakTokian(
                hauteskundeatokian=hauteskundeaTokian, alderdia=alderdia
            )
            hauteskundeEmaitzakTokian.botoak = int(
                row[index + alderdi_botoak_index]
            )
            hauteskundeEmaitzakTokian.jarlekuak = int(
                row[index + alderdi_jarlekuak_index]
            )
            hauteskundeEmaitzakTokian.save()
            index += PARTY_INFO_COLUMN_BLOCK
