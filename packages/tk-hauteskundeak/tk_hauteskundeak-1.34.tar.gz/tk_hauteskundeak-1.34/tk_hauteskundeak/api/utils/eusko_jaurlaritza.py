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


def import_jaurlaritza(data, hauteskundea):
    root = XML.fromstring(data)
    towns = root.findall("SalidaXML")

    candidates_json = get_candidates_json()

    for town in towns:

        lurralde_kodea = int(town.find("Ambito").text[:2])
        herri_kodea = int(town.find("Ambito").text[2:])

        if lurralde_kodea == 0:
            mota = 5
        elif herri_kodea == 0:
            mota = 4
        else:
            mota = 1

        if Tokia.objects.filter(
            lurralde_kodea=lurralde_kodea,
            herri_kodea=herri_kodea,
            mota=mota,
        ).exists():
            tokia = Tokia.objects.get(
                lurralde_kodea=lurralde_kodea,
                herri_kodea=herri_kodea,
                mota=mota,
            )
        else:
            tokia = Tokia()
            tokia.izena = town.find("Descripcion").text
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
        hauteskundeaTokian.errolda = int(town.find("Censo").text)
        hauteskundeaTokian.boto_emaileak = int(town.find("Votos").text)
        hauteskundeaTokian.baliogabeak = int(town.find("Nulos").text)
        hauteskundeaTokian.zuriak = int(town.find("Blancos").text)
        hauteskundeaTokian.eskrutinioa = float(town.find("PorcentajeEscrutado").text.replace(",", "."))
        hauteskundeaTokian.save()

        partiduak = town.find("Partidos")
        for par in partiduak.findall("Partido"):
            slug = slugify(par.find("Siglas").text)
            if slug in candidates_json:
                alderdia = Alderdia.objects.get(slug=candidates_json[slug])
            else:
                alderdia = Alderdia()
                alderdia.izena = par.find("Siglas").text
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
            hauteskundeEmaitzakTokian.botoak = par.find("Votos").text
            hauteskundeEmaitzakTokian.jarlekuak = par.find("Escanios").text
            hauteskundeEmaitzakTokian.save()
