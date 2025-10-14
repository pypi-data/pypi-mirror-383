from django.core.management.base import BaseCommand
from django.db.models import Q
from tk_hauteskundeak.models import (
    Alderdia,
    Hauteskundea,
    HauteskundeaTokian,
    HauteskundeEmaitzakTokian,
    HauteskundeEserlekuakTokian,
)
from tk_hauteskundeak.views import sortu_eskualdeko_datuak
from django.utils import timezone

DB2 = "tokikom_zerbitzuak"
TOKI_MOTAK = [
    1,  # Herriak
    4,  # Herrialdeak
    5,  # Erkidegoak
    6,  # Estatuak
]


class Command(BaseCommand):
    args = "Hauteskunde datuen biltegiratzea"
    help = "Hauteskunde datuen biltegiratzea zuzenean egiteko"

    def handle(self, *args, **options):
        hauteskundeak = Hauteskundea.objects.filter(auto_import=True)

        for hauteskundea in hauteskundeak:
            hauteskundeakTokian = HauteskundeaTokian.objects.filter(
                tokia__mota__in=TOKI_MOTAK, hauteskundea=hauteskundea
            )

            for haTokian in hauteskundeakTokian:
                hauteskunde_mota = haTokian.hauteskundea.mota.akronimoa
                lurralde_kodea = haTokian.tokia.lurralde_kodea
                herri_kodea = haTokian.tokia.herri_kodea

                haTokianDB2 = (
                    HauteskundeaTokian.objects.using(DB2)
                    .filter(
                        hauteskundea__mota__akronimoa=hauteskunde_mota,
                        tokia__lurralde_kodea=lurralde_kodea,
                        tokia__herri_kodea=herri_kodea,
                    )
                    .values(
                        "id",
                        "jarlekuen_kopurua",
                        "errolda",
                        "boto_emaileak",
                        "baliogabeak",
                        "zuriak",
                        "eskrutinioa",
                    )
                    .first()
                )

                if not haTokianDB2:
                    continue
                haTokianDB2_id = haTokianDB2.pop("id")

                for attr, value in haTokianDB2.items():
                    setattr(haTokian, attr, value)
                haTokian.save()

                emaitzakDB2 = (
                    HauteskundeEmaitzakTokian.objects.using(DB2)
                    .filter(hauteskundeatokian__id=haTokianDB2_id)
                    .values(
                        "alderdia__slug",
                        "alderdia__akronimoa",
                        "alderdia__izena",
                        "botoak",
                        "jarlekuak",
                    )
                )

                HauteskundeEmaitzakTokian.objects.filter(
                    hauteskundeatokian=haTokian,
                ).delete()

                for emaitzaDB2 in emaitzakDB2:
                    if Alderdia.objects.filter(
                        Q(import_kodea=emaitzaDB2["alderdia__slug"])
                        | Q(slug=emaitzaDB2["alderdia__slug"])
                    ).exists():
                        alderdia = Alderdia.objects.get(
                            Q(import_kodea=emaitzaDB2["alderdia__slug"])
                            | Q(slug=emaitzaDB2["alderdia__slug"])
                        )
                    else:
                        alderdia = Alderdia()
                        alderdia.slug = emaitzaDB2["alderdia__slug"]
                        alderdia.akronimoa = emaitzaDB2["alderdia__akronimoa"]
                        alderdia.izena = emaitzaDB2["alderdia__izena"]
                        alderdia.save()
                    emaitza = HauteskundeEmaitzakTokian()
                    emaitza.hauteskundeatokian = haTokian
                    emaitza.alderdia = alderdia

                    emaitza.botoak = emaitzaDB2["botoak"]
                    emaitza.jarlekuak = emaitzaDB2["jarlekuak"]
                    emaitza.save()

                zinegotziakTokian = haTokian.hauteskundeeserlekuaktokian_set.all()

                if haTokian.eskrutinioa > 0 and zinegotziakTokian:
                    # ZINEGOTZIAK KALKULATU
                    # Zinegotziak hasieratu
                    zinegotziakTokian.update(is_selected=False)

                    # Zinegotzien kalkulua eserlekuen arabera
                    e = 0
                    for (
                        emaitza
                    ) in haTokian.hauteskundeemaitzaktokian_set.all().order_by(
                        "-botoak",
                        "-jarlekuak",
                    ):
                        # Aurrez sortutako eserlekuak baino gehiago behar badira, hutsak sortzeko
                        eserleku_kop = haTokian.hauteskundeeserlekuaktokian_set.filter(
                            alderdia=emaitza.alderdia
                        ).count()
                        if eserleku_kop < emaitza.jarlekuak:
                            eserlekuak = emaitza.jarlekuak - eserleku_kop
                            ordena = eserleku_kop + 1
                            for i in range(1, eserlekuak + 1):
                                het = HauteskundeEserlekuakTokian()
                                het.hauteskundeatokian = haTokian
                                het.alderdia = emaitza.alderdia
                                het.ordena_alderdian = ordena
                                het.izena = "Izen Abizena"
                                het.is_selected = False
                                het.save()
                                ordena += 1

                        for z in haTokian.hauteskundeeserlekuaktokian_set.filter(
                            alderdia=emaitza.alderdia,
                            ordena_alderdian__lte=emaitza.jarlekuak,
                        ):
                            z.is_selected = True
                            z.ordena = e * 100 + z.ordena_alderdian
                            z.save()
                        e += 1

            sortu_eskualdeko_datuak(hauteskundea)
            print("Eskualdeko datuak kalkulatuta")
