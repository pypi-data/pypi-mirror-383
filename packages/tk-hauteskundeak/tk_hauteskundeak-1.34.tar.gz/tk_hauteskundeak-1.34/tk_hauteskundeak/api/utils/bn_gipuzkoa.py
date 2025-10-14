import csv
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

TOWN_INFO_COLUMN_QTY = 11
PARTY_INFO_COLUMN_BLOCK = 4
PARTY_STATS_TO_EXCLUDE = 6
LURRALDE_KODEA = 20
ESKUALDE_KODEAK = [991, 992, 993, 994, 999]

# 0 ORDUA-HORA
# 1 ZENB-ESCRUT.
# 2 ESPARRUARREN KOD.-COD.AMBITO
# 3 ESPARRUAREN IZENA-NOMBRE AMBITO
# 4 ZENTSUA-CENSO
# 5 HAUTETSIAK-ELECTOS
# 6 PARTE HARTZE %-% PARTICIPACION
# 7 HAUTESLEAK-VOTANTES
# 8 BALIOGABEAK-NULOS
# 9 BALIOZKOAK-VALIDOS
# 10 ZURIAK-BLANCOS
# 11 AURKEZTUTAKO HAUTAGAIAK


ESKUALDEAK = [991, 992, 993, 994]
HERRIALDEA = 999


def import_gipuzkoa(data, hauteskundea):
    f = StringIO(data)
    dialect = csv.Sniffer().sniff(data, delimiters="|")
    reader = csv.reader(f, dialect)

    candidates_json = get_candidates_json()

    for row in reader:
        if row[0] == "ORDUA-HORA":
            continue

        herri_kodea = int(row[2])

        if int(row[2]) in ESKUALDEAK:
            mota = 2
        elif int(row[2]) == HERRIALDEA:
            herri_kodea = 0
            mota = 4
        else:
            mota = 1

        if Tokia.objects.filter(
            lurralde_kodea=LURRALDE_KODEA,
            herri_kodea=herri_kodea,
            mota=mota,
        ).exists():
            tokia = Tokia.objects.get(
                lurralde_kodea=LURRALDE_KODEA,
                herri_kodea=herri_kodea,
                mota=mota,
            )
        else:
            tokia = Tokia()
            tokia.izena = row[3].strip()
            tokia.slug = slugify(tokia.izena)
            tokia.lurralde_kodea = LURRALDE_KODEA
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
        hauteskundeaTokian.errolda = int(row[4])
        hauteskundeaTokian.boto_emaileak = int(row[7])
        hauteskundeaTokian.baliogabeak = int(row[8])
        hauteskundeaTokian.zuriak = int(row[10])
        hauteskundeaTokian.eskrutinioa = float(row[1])
        hauteskundeaTokian.jarlekuen_kopurua = int(row[5])
        hauteskundeaTokian.save()

        total_rows = len(row) - PARTY_STATS_TO_EXCLUDE
        iterations = int(
            (total_rows - TOWN_INFO_COLUMN_QTY) / PARTY_INFO_COLUMN_BLOCK
        )
        index = TOWN_INFO_COLUMN_QTY + 1

        for iter in range(iterations):
            if row[index].strip() == "":
                index += 4
                continue
            slug = slugify(row[index].strip())
            if slug in candidates_json:
                alderdia = Alderdia.objects.get(slug=candidates_json[slug])
            else:
                alderdia = Alderdia()
                alderdia.izena = row[index].strip()
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
            hauteskundeEmaitzakTokian.botoak = int(row[index + 2])
            hauteskundeEmaitzakTokian.jarlekuak = int(row[index + 3])
            hauteskundeEmaitzakTokian.save()
            index += 4
