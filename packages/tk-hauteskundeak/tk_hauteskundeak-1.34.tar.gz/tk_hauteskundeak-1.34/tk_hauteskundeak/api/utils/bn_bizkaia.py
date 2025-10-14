import xml.etree.ElementTree as XML
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

LURRALDE_KODEA = 48

ESKUALDEAK = [991, 992, 993, 994]
HERRIALDEA = 999


def import_bizkaia(data, hauteskundea):
    root = XML.fromstring(data)
    towns = root[1].findall("amb")

    candidates_json = get_candidates_json()

    for town in towns:

        herri_kodea = int(town.attrib["codamb"])

        if int(town.attrib["codamb"]) in ESKUALDEAK:
            mota = 2
        elif int(town.attrib["codamb"]) == HERRIALDEA:
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
            tokia.izena = town.attrib["nomamb"]
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
        hauteskundeaTokian.errolda = int(town.attrib["cenrea"])
        hauteskundeaTokian.boto_emaileak = int(town.attrib["votantes"])
        hauteskundeaTokian.baliogabeak = int(town.attrib["nulos"])
        hauteskundeaTokian.zuriak = int(town.attrib["blancos"])
        hauteskundeaTokian.eskrutinioa = float(town.attrib["pescr"])
        hauteskundeaTokian.jarlekuen_kopurua = int(town.attrib["escan"])
        hauteskundeaTokian.save()

        partiduak = town.findall("par")
        for par in partiduak:
            slug = slugify(par.attrib["sigpar"])
            if slug in candidates_json:
                alderdia = Alderdia.objects.get(slug=candidates_json[slug])
            else:
                alderdia = Alderdia()
                alderdia.izena = par.attrib["sigpar"]
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
            hauteskundeEmaitzakTokian.botoak = par.attrib["votos"]
            hauteskundeEmaitzakTokian.jarlekuak = par.attrib["numesc"]
            hauteskundeEmaitzakTokian.save()
