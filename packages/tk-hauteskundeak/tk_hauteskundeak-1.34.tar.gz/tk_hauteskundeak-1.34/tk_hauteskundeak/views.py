from django.views.generic import (
    ListView,
    DetailView,
    FormView,
    TemplateView,
    RedirectView,
)
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from .models import (
    Tokia,
    HauteskundeaTokian,
    Alderdia,
    Hauteskundea,
    HauteskundeEmaitzakTokian,
    HauteskundeMota,
    HauteskundeOharrak,
    HauteskundeKP,
    HauteskundeaIframe,
    HauteskundeEserlekuakTokian,
)
from .meta import Meta
import collections
from highcharts.views import HighChartsBarView

from highcharts.views.line import HighChartsLineView
from highcharts.views.area import HighChartsAreaView
from highcharts.views.multiple_axes import HighChartsMultiAxesView
from highcharts.views.pie import HighChartsPieView
from highcharts.views.speedometer import HighChartsSpeedometerView
from highcharts.views.multiple_axes import HighChartsStockView
from highcharts.views.heatmap import HighChartsHeatMapView
from highcharts.views.polar import HighChartsPolarView
from django.db.models import Sum, Count, Max

from django.utils.html import escapejs
import random
from django.db.models import Q, Case, When, F, IntegerField, FloatField


def get_tokiak():
    return Tokia.objects.filter(is_public=True).order_by(
        "order_col", "order_list", "-mota", "izena"
    )


def get_tokia(kwargs):
    if kwargs.get("slug_tokia", ""):
        tokia = Tokia.objects.get(slug=kwargs.get("slug_tokia", ""))
    else:
        tokia = Tokia.objects.all().filter(is_default=True).first()
    return tokia


def get_oharrak(alderdiak=None, hauteskundeak=None):
    tor = []
    # Ohar orokorrak
    qs = HauteskundeOharrak.objects.all()
    qs = qs.filter(alderdia__isnull=True, hauteskundeak__isnull=True)
    for q in qs:
        tor.append(q)
    # Datu-baseko oharrak, alderdi eta hauteskunde hauentzat
    qs = HauteskundeOharrak.objects.all()
    if alderdiak and hauteskundeak:
        qs = qs.filter(alderdia__in=alderdiak, hauteskundeak__in=hauteskundeak)
    elif alderdiak:
        qs = qs.filter(alderdia__in=alderdiak)
    elif hauteskundeak:
        qs = qs.filter(hauteskundeak__in=hauteskundeak)

    for q in qs.distinct():
        tor.append(q)

    return tor


def get_hauteskundeak_info(tokia, mota=None, pks=[], order_by=""):
    """ """
    # children = list(tokia.get_children().values_list('pk', flat=True))
    # children.append(tokia.pk)

    qs = Hauteskundea.objects.filter(
        hauteskundeatokian__tokia=tokia,
        is_public=True,
    )

    """
    if len(children)==1:
        qs = Hauteskundea.objects.filter(is_public=True,hauteskundeatokian__tokia=children[0])
    else:
        qs = Hauteskundea.objects.filter(is_public=True,hauteskundeatokian__tokia__in=children)
    """
    if pks:
        if len(pks) == 1:
            qs = qs.filter(pk=pks[0])
        else:
            qs = qs.filter(pk__in=pks)
    if mota:
        qs = qs.filter(mota=mota)
    qs = qs.distinct()

    annotations = {}
    annotations["errolda"] = Sum("hauteskundeatokian__errolda")
    annotations["boto_emaileak"] = Sum("hauteskundeatokian__boto_emaileak")
    annotations["baliogabeak"] = Sum("hauteskundeatokian__baliogabeak")
    annotations["zuriak"] = Sum("hauteskundeatokian__zuriak")
    annotations["botoak"] = Sum("hauteskundeatokian__alderdien_botoak")
    annotations["jarlekuak"] = Sum("hauteskundeatokian__jarlekuen_kopurua")

    qs = qs.annotate(**annotations)

    if order_by:
        qs = qs.order_by(order_by)
    else:
        qs = qs.order_by("eguna")

    return qs


class IndexView(TemplateView):

    template_name = "tk_hauteskundeak/index.html"
    template_name_itxita = "tk_hauteskundeak/index_itxita.html"

    def get_template_names(self):
        kp = HauteskundeKP.objects.filter(is_public=True)
        if kp.exists():
            return [
                self.template_name,
            ]
        return [
            self.template_name_itxita,
        ]

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        tokia = get_tokia(self.kwargs)
        if not tokia:
            raise Http404
        tokiak = get_tokiak()
        try:
            context["kp"] = HauteskundeKP.objects.filter(is_public=True).first()
            context["title"] = context["kp"].title
            context["is_public"] = True
            context["title"] = "Hauteskundeak"
        except:
            context["is_public"] = False

        context["alderdiak"] = osatu_alderdiaren_lista(tokia).filter(
            logoa__isnull=False, show_in_graphs=True, botoak_azkena__gt=0
        )
        context["motak"] = HauteskundeMota.objects.filter(is_public=True).order_by(
            "order"
        )
        context["hauteskundeak"] = Hauteskundea.objects.filter(is_public=True).order_by(
            "-eguna"
        )[:8]
        context["hauteskunde_guztiak"] = Hauteskundea.objects.filter(
            is_public=True
        ).order_by("-eguna")
        context["tokiak"] = tokiak
        context["tokia"] = tokia

        context["meta"] = Meta(reverse("hauteskundeak_home"), title=context["title"])
        return context


class RedirectToCompareView(RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        slug1 = self.request.GET.get("slug1", "")
        slug2 = self.request.GET.get("slug2", "")
        slug_tokia = self.request.GET.get("tokia_slug", "")
        if slug1 and slug2 and slug_tokia:
            return reverse(
                "hauteskundeak_hauteskundea_compare_tokia",
                kwargs={
                    "slug": slug1,
                    "slug2": slug2,
                    "slug_tokia": slug_tokia,
                },
            )
        return reverse("hauteskundeak_home")


def get_hauteskundea_tokiak_irabazleak(hauteskundea, tokiak, portada=False):
    """ """
    tor = []
    for tokia in tokiak:
        h2 = {}
        h2["tokia"] = tokia

        if portada:  # POrtadan bakarrik erakusteko eskrutinioa
            hauteskundea_tokian = HauteskundeaTokian.objects.filter(
                hauteskundea=hauteskundea,
                tokia=tokia,
            )
            if hauteskundea_tokian and portada:
                h2["eskrutinioa"] = hauteskundea_tokian.first().eskrutinioa

        qs = HauteskundeEmaitzakTokian.objects.filter(
            hauteskundeatokian__hauteskundea=hauteskundea,
            hauteskundeatokian__tokia=tokia,
        ).order_by("-botoak")

        if qs.exists():
            if qs.first().botoak > 0:
                h2["irabazlea"] = qs.first().alderdia
            else:
                h2["irabazlea"] = ""
            tor.append(h2)
    return tor


def osatu_hauteskunde_baten_info_dena(hauteskundea, tokia):
    """ """
    tor = {}
    try:
        ht = HauteskundeaTokian.objects.get(hauteskundea=hauteskundea, tokia=tokia)
        tor["emaitzak_bai"] = True
    except:
        tor["emaitzak_bai"] = False
        return tor

    het = (
        HauteskundeEmaitzakTokian.objects.filter(hauteskundeatokian=ht)
        .exclude(botoak=0)
        .values(
            "alderdia__slug",
            "alderdia__akronimoa",
            "alderdia__kolorea",
            "alderdia__show_in_page",
            "alderdia__show_in_graphs",
            "alderdia__logoa",
            "botoak",
            "ehunekoa",
            "jarlekuak",
        )
        .order_by("-botoak", "alderdia__slug")
    )
    zerrenda = list(het)

    tor["info"] = ht

    if zerrenda:
        tor["taula"] = zerrenda
        tor["taula2"] = sorted(zerrenda, key=lambda x: (-x["jarlekuak"], -x["botoak"]))
        # grafikora bidali behar dira aukeratutako denak... baina tartekorik bada, hura ere bai
        min_botoak = [a for a in zerrenda if a["alderdia__show_in_graphs"]][-1][
            "botoak"
        ]
        tor["grafikoa"] = [a for a in tor["taula"] if a["botoak"] >= min_botoak]
        tor["grafikoa2"] = [a for a in tor["taula2"] if a["botoak"] >= min_botoak]
        tor["has_jarlekuak"] = zerrenda[0]["jarlekuak"] and True or False
    else:
        tor["taula"] = []
        tor["taula2"] = []
        tor["grafikoa"] = []
        tor["grafikoa2"] = []
        tor["has_jarlekuak"] = False

    herriak = tokia.get_children()
    if herriak:
        tor["show_herriak"] = True
        tor["herriak"] = get_hauteskundea_tokiak_irabazleak(hauteskundea, herriak)
    else:
        tor["show_herriak"] = False
    return tor


TAULAN_MOZTEKO_HERRIAK_KOPUTUA = 10


class HauteskundeaSimpleView(TemplateView):
    template_name = "tk_hauteskundeak/hauteskundea_simple.html"

    def get_context_data(self, **kwargs):
        context = super(HauteskundeaSimpleView, self).get_context_data(**kwargs)

        hauteskundea = get_object_or_404(
            Hauteskundea, slug=self.kwargs["slug"], is_public=True
        )
        tokia = get_tokia(self.kwargs)

        context["tokia"] = tokia
        context["tokiak"] = get_tokiak()
        context["hauteskundea"] = hauteskundea
        context["object"] = hauteskundea
        context["info"] = osatu_hauteskunde_baten_info_dena(hauteskundea, tokia)

        context["zinegotziak"] = HauteskundeEserlekuakTokian.objects.filter(
            hauteskundeatokian__tokia=tokia,
            hauteskundeatokian__hauteskundea=hauteskundea,
            is_selected=True,
        ).order_by("ordena")
        context["herriak"] = get_hauteskundea_tokiak_irabazleak(
            hauteskundea, tokia.get_children()
        )
        if len(context["herriak"]) > TAULAN_MOZTEKO_HERRIAK_KOPUTUA:
            context["herriak_taulan_mozteko"] = len(context["herriak"]) / 2 + 1
        else:
            context["herriak_taulan_mozteko"] = 0
        context["oharrak"] = get_oharrak(
            hauteskundeak=[
                hauteskundea,
            ]
        )
        context["hauteskunde_guztiak"] = Hauteskundea.objects.filter(
            is_public=True
        ).order_by("-eguna")

        meta_url = reverse(
            "hauteskundeak_hauteskundea_tokia",
            kwargs={"slug": hauteskundea.slug, "slug_tokia": tokia.slug},
        )
        meta_title = "{} - {}".format(hauteskundea.izena, tokia.izena)
        context["meta"] = Meta(meta_url, title=meta_title)
        return context


class HauteskundeaView(TemplateView):

    template_name = "tk_hauteskundeak/hauteskundea.html"

    def get_context_data(self, **kwargs):
        context = super(HauteskundeaView, self).get_context_data(**kwargs)

        tokia = get_tokia(self.kwargs)
        tokiak = get_tokiak()

        hauteskundea = get_object_or_404(Hauteskundea, slug=self.kwargs["slug"])

        emaitza2 = osatu_hauteskundeen_taula(
            [
                hauteskundea,
            ],
            tokia,
        )

        hauteskundeak = get_hauteskundeak_info(
            tokia=tokia,
            pks=[
                hauteskundea.pk,
            ],
        )
        # hauteskundeak = get_hauteskundeak_info(tokia=tokia,pks=[a.pk for a in hauteskundeak], order_by='-eguna')

        context["taula"] = emaitza2["taula"]
        context["taula_graph"] = emaitza2["taula"].filter(show_in_graphs=True)
        context["tokiak"] = tokiak
        context["tokia"] = tokia
        context["hauteskundeak"] = hauteskundeak
        context["oharrak"] = get_oharrak(hauteskundeak=hauteskundeak)
        context["object"] = hauteskundea
        if hauteskundeak:
            context["has_jarlekuak"] = hauteskundeak.first().jarlekuak
        else:
            context["has_jarlekuak"] = False

        context["zinegotziak"] = HauteskundeEserlekuakTokian.objects.filter(
            hauteskundeatokian__tokia=tokia,
            hauteskundeatokian__hauteskundea=hauteskundea,
            is_selected=True,
        ).order_by("ordena")

        context["herriak"] = get_hauteskundea_tokiak_irabazleak(
            hauteskundea, tokia.get_children()
        )
        context["hauteskunde_guztiak"] = Hauteskundea.objects.filter(
            is_public=True
        ).order_by("-eguna")

        context["emaitzak_bai"] = emaitza2["taula"].exists()

        meta_url = reverse(
            "hauteskundeak_hauteskundea_tokia",
            kwargs={"slug": hauteskundea.slug, "slug_tokia": tokia.slug},
        )
        meta_title = "{} - {}".format(hauteskundea.izena, tokia.izena)

        context["meta"] = Meta(meta_url, title=meta_title)
        return context


class HauteskundeaPortadaView(HauteskundeaView):
    def get_context_data(self, **kwargs):
        context = super(HauteskundeaPortadaView, self).get_context_data(**kwargs)
        portada = True
        context["herriak"] = get_hauteskundea_tokiak_irabazleak(
            context["object"], context["tokia"].get_children(), portada
        )
        context["portada"] = portada
        return context


def osatu_hauteskunde_bi_info_dena(hauteskundea, hauteskundea2, tokia):
    """ """
    tor = {}
    try:
        ht = HauteskundeaTokian.objects.get(hauteskundea=hauteskundea, tokia=tokia)
        ht2 = HauteskundeaTokian.objects.get(hauteskundea=hauteskundea2, tokia=tokia)
        tor["emaitzak_bai"] = True
    except:
        tor["emaitzak_bai"] = False
        return tor

    het = (
        HauteskundeEmaitzakTokian.objects.filter(
            hauteskundeatokian=ht, alderdia__show_in_table=True
        )
        .exclude(botoak=0)
        .values(
            "alderdia__pk",
            "alderdia__slug",
            "alderdia__akronimoa",
            "alderdia__kolorea",
            "alderdia__show_in_page",
            "alderdia__show_in_graphs",
            "alderdia__logoa",
            "botoak",
            "ehunekoa",
            "jarlekuak",
        )
        .order_by("-botoak", "alderdia__slug")
    )
    zerrenda = list(het)

    het2 = (
        HauteskundeEmaitzakTokian.objects.filter(
            hauteskundeatokian=ht2, alderdia__show_in_table=True
        )
        .exclude(botoak=0)
        .values(
            "alderdia__pk",
            "alderdia__slug",
            "alderdia__akronimoa",
            "alderdia__kolorea",
            "alderdia__show_in_page",
            "alderdia__show_in_graphs",
            "alderdia__logoa",
            "botoak",
            "ehunekoa",
            "jarlekuak",
        )
        .order_by("-botoak", "alderdia__slug")
    )
    zerrenda2 = list(het2)

    tor["info"] = ht
    tor["info2"] = ht2

    zerrenda_batua = []

    for alderdia in zerrenda:
        h = {}
        for k, v in alderdia.items():
            h[k] = v
        h["botoak2"] = ""
        h["ehunekoa2"] = ""
        h["jarlekuak2"] = ""
        h["botoakdif"] = ""
        h["botoakdifehunekoa"] = ""
        h["ehunekoadif"] = ""
        h["jarlekuakdif"] = ""
        zerrenda_batua.append(h)

    for alderdia2 in zerrenda2:
        gehitua = False
        for alderdia in zerrenda_batua:
            if alderdia["alderdia__pk"] == alderdia2["alderdia__pk"]:
                alderdia["botoak2"] = alderdia2["botoak"]
                alderdia["ehunekoa2"] = alderdia2["ehunekoa"]
                alderdia["jarlekuak2"] = alderdia2["jarlekuak"]
                if alderdia["botoak"] and alderdia["botoak2"]:
                    alderdia["botoakdif"] = alderdia["botoak"] - alderdia["botoak2"]
                    alderdia["botoakdifehunekoa"] = (
                        alderdia["botoak2"]
                        and alderdia["botoakdif"] * 100.0 / alderdia["botoak2"]
                    )
                if alderdia["ehunekoa"] and alderdia["ehunekoa2"]:
                    alderdia["ehunekoadif"] = (
                        alderdia["ehunekoa"] - alderdia["ehunekoa2"]
                    )
                if alderdia["jarlekuak"] and alderdia["jarlekuak2"]:
                    alderdia["jarlekuakdif"] = (
                        alderdia["jarlekuak"] - alderdia["jarlekuak2"]
                    )
                gehitua = True

        if not gehitua:
            h = {}
            for k, v in alderdia2.items():
                h[k] = v
            h["botoak2"] = alderdia2["botoak"]
            h["ehunekoa2"] = alderdia2["ehunekoa"]
            h["jarlekuak2"] = alderdia2["jarlekuak"]
            h["botoak"] = ""
            h["ehunekoa"] = ""
            h["jarlekuak"] = ""
            h["botoakdif"] = ""
            h["botoakdifehunekoa"] = ""
            h["ehunekoadif"] = ""
            h["jarlekuakdif"] = ""
            zerrenda_batua.append(h)

    if zerrenda_batua:
        tor["taula"] = zerrenda_batua
        tor["grafikoa"] = [a for a in zerrenda_batua if a["alderdia__show_in_graphs"]]
    else:
        tor["taula"] = []
        tor["grafikoa"] = []

    return tor


class HauteskundeaSimpleCompareView(TemplateView):
    template_name = "tk_hauteskundeak/hauteskundea_compare_simple.html"

    def get_context_data(self, **kwargs):
        context = super(HauteskundeaSimpleCompareView, self).get_context_data(**kwargs)

        hauteskundea = get_object_or_404(Hauteskundea, slug=self.kwargs["slug"])
        hauteskundea2 = get_object_or_404(Hauteskundea, slug=self.kwargs["slug2"])
        tokia = get_tokia(self.kwargs)

        context["tokia"] = tokia
        context["tokiak"] = get_tokiak()
        context["hauteskundea"] = hauteskundea
        context["hauteskundea2"] = hauteskundea2
        context["object"] = hauteskundea
        context["info"] = osatu_hauteskunde_bi_info_dena(
            hauteskundea, hauteskundea2, tokia
        )
        context["oharrak"] = get_oharrak(
            hauteskundeak=[
                hauteskundea,
                hauteskundea2,
            ]
        )
        context["hauteskunde_guztiak"] = Hauteskundea.objects.filter(
            is_public=True
        ).order_by("-eguna")

        if hauteskundea.mota == hauteskundea2.mota:
            context["title"] = "{} vs {}".format(
                hauteskundea.izena, hauteskundea2.get_urtea()
            )
        else:
            context["title"] = "{} vs {}".format(
                hauteskundea.izena, hauteskundea2.izena
            )

        meta_url = reverse(
            "hauteskundeak_hauteskundea_compare_tokia",
            kwargs={
                "slug": hauteskundea.slug,
                "slug2": hauteskundea2.slug,
                "slug_tokia": tokia.slug,
            },
        )
        meta_title = "{} vs {} - {}".format(
            hauteskundea.izena, hauteskundea2.izena, tokia.izena
        )
        context["meta"] = Meta(meta_url, title=meta_title)
        return context


class HauteskundeaCompareView(TemplateView):

    template_name = "tk_hauteskundeak/hauteskundea_compare.html"

    def get_context_data(self, **kwargs):
        context = super(HauteskundeaCompareView, self).get_context_data(**kwargs)

        tokia = get_tokia(self.kwargs)
        tokiak = get_tokiak()

        obj = get_object_or_404(Hauteskundea, slug=self.kwargs["slug"])
        obj1 = get_object_or_404(Hauteskundea, slug=self.kwargs["slug2"])

        context["haute_tokian"] = HauteskundeaTokian.objects.filter(
            tokia=tokia, hauteskundea=obj
        ).first()
        context["haute_tokian1"] = HauteskundeaTokian.objects.filter(
            tokia=tokia, hauteskundea=obj1
        )

        hauteskundeak = [
            obj,
            obj1,
        ]
        emaitza2 = osatu_hauteskundeen_taula(
            hauteskundeak,
            tokia,
        )

        hauteskundeak = get_hauteskundeak_info(
            tokia=tokia, pks=[a.pk for a in hauteskundeak], order_by="eguna"
        )

        context["taula"] = emaitza2["taula"]
        context["taula_graph"] = emaitza2["taula"].filter(show_in_graphs=True)
        context["taula_table"] = emaitza2["taula"].filter(show_in_table=True)
        context["tokiak"] = tokiak
        context["tokia"] = tokia
        context["hauteskundeak"] = hauteskundeak
        context["oharrak"] = get_oharrak(hauteskundeak=hauteskundeak)
        context["object"] = obj
        context["object1"] = obj1

        context["hauteskunde_guztiak"] = Hauteskundea.objects.filter(
            is_public=True
        ).order_by("-eguna")

        meta_url = reverse(
            "hauteskundeak_hauteskundea_compare_tokia",
            kwargs={
                "slug": obj.slug,
                "slug2": obj1.slug,
                "slug_tokia": tokia.slug,
            },
        )
        meta_title = "{} vs {} - {}".format(obj.izena, obj1.izena, tokia.izena)

        context["meta"] = Meta(meta_url, title=meta_title)

        return context


def osatu_hauteskundeen_taula(hauteskundeak, tokia, desc_order=True):
    """ """
    # children = [tokia.pk,]
    # children = list(tokia.get_children().values_list('pk', flat=True))
    # children.append(tokia.pk)

    annotations = {}
    annotations["botoak_guztira"] = Sum(
        Case(
            When(
                hauteskundeemaitzaktokian__hauteskundeatokian__tokia__pk=tokia.pk,
                hauteskundeemaitzaktokian__hauteskundeatokian__hauteskundea__in=hauteskundeak,
                then=F("hauteskundeemaitzaktokian__botoak"),
            ),
            default=0,
            output_field=IntegerField(),
        )
    )
    i = 0
    order_by_txt = []
    for hauteskundea in hauteskundeak:
        key = "botoak_{}".format(i)
        annotations[key] = Sum(
            Case(
                When(
                    hauteskundeemaitzaktokian__hauteskundeatokian__tokia=tokia,
                    hauteskundeemaitzaktokian__hauteskundeatokian__hauteskundea=hauteskundea,
                    then=F("hauteskundeemaitzaktokian__botoak"),
                ),
                default=0,
                output_field=IntegerField(),
            )
        )
        key2 = "jarlekuak_{}".format(i)
        annotations[key2] = Sum(
            Case(
                When(
                    hauteskundeemaitzaktokian__hauteskundeatokian__tokia=tokia,
                    hauteskundeemaitzaktokian__hauteskundeatokian__hauteskundea=hauteskundea,
                    then=F("hauteskundeemaitzaktokian__jarlekuak"),
                ),
                default=0,
                output_field=IntegerField(),
            )
        )
        key3 = "ehunekoa_{}".format(i)
        annotations[key3] = Sum(
            Case(
                When(
                    hauteskundeemaitzaktokian__hauteskundeatokian__tokia=tokia,
                    hauteskundeemaitzaktokian__hauteskundeatokian__hauteskundea=hauteskundea,
                    then=F("hauteskundeemaitzaktokian__ehunekoa"),
                ),
                default=0,
                output_field=FloatField(),
            )
        )
        order_by_txt.append("-{}".format(key))
        i += 1

    order_by_txt.reverse()

    if desc_order:
        if order_by_txt:
            het = (
                Alderdia.objects.all()
                .annotate(**annotations)
                .filter(botoak_guztira__gt=0)
                .order_by(order_by_txt[0], "-botoak_guztira")
            )
        else:
            het = (
                Alderdia.objects.all()
                .annotate(**annotations)
                .filter(botoak_guztira__gt=0)
                .order_by(
                    "-botoak_guztira",
                )
            )
    else:
        if order_by_txt:

            het = (
                Alderdia.objects.all()
                .annotate(**annotations)
                .filter(botoak_guztira__gt=0)
                .order_by(*order_by_txt)
            )
        else:
            het = (
                Alderdia.objects.all()
                .annotate(**annotations)
                .filter(botoak_guztira__gt=0)
                .order_by(
                    "-botoak_guztira",
                )
            )

    tor = {}
    tor["taula"] = het
    return tor


class HauteskundeMotaView(TemplateView):

    template_name = "tk_hauteskundeak/hauteskunde_mota.html"

    def get_context_data(self, **kwargs):
        context = super(HauteskundeMotaView, self).get_context_data(**kwargs)

        tokia = get_tokia(self.kwargs)
        obj = get_object_or_404(HauteskundeMota, slug=self.kwargs["slug"])

        hauteskundeak = get_hauteskundeak_info(tokia=tokia, mota=obj)
        emaitza2 = osatu_hauteskundeen_taula(hauteskundeak, tokia, False)

        context["taula"] = emaitza2["taula"]
        context["taula_graph"] = emaitza2["taula"].filter(show_in_graphs=True)
        context["taula_table"] = emaitza2["taula"].filter(show_in_table=True)
        context["tokiak"] = get_tokiak()
        context["tokia"] = tokia
        context["hauteskundeak"] = hauteskundeak
        context["oharrak"] = get_oharrak(hauteskundeak=hauteskundeak)
        context["object"] = obj

        meta_url = reverse(
            "hauteskundeak_hauteskunde_mota_tokia",
            kwargs={"slug": obj.slug, "slug_tokia": tokia.slug},
        )
        meta_title = "{} - {}".format(obj.izena, tokia.izena)

        context["meta"] = Meta(meta_url, title=meta_title)

        return context


def osatu_alderdiaren_taula(alderdia, tokia):
    """ """
    # children = list(tokia.get_children().values_list('pk', flat=True))
    # children.append(tokia.pk)

    annotations = {}

    annotations["botoak"] = Sum(
        Case(
            When(
                hauteskundeatokian__hauteskundeemaitzaktokian__alderdia=alderdia,
                hauteskundeatokian__tokia=tokia,
                then=F("hauteskundeatokian__hauteskundeemaitzaktokian__botoak"),
            ),
            default=0,
            output_field=IntegerField(),
        )
    )
    annotations["botoak_guztira"] = Sum(
        Case(
            When(
                hauteskundeatokian__tokia=tokia,
                then=F("hauteskundeatokian__hauteskundeemaitzaktokian__botoak"),
            ),
            default=0,
            output_field=IntegerField(),
        )
    )
    annotations["eserlekuak"] = Sum(
        Case(
            When(
                hauteskundeatokian__hauteskundeemaitzaktokian__alderdia=alderdia,
                hauteskundeatokian__tokia=tokia,
                then=F("hauteskundeatokian__hauteskundeemaitzaktokian__jarlekuak"),
            ),
            default=0,
            output_field=IntegerField(),
        )
    )
    annotations["ehunekoa"] = Sum(
        Case(
            When(
                hauteskundeatokian__hauteskundeemaitzaktokian__alderdia=alderdia,
                hauteskundeatokian__tokia=tokia,
                then=F("hauteskundeatokian__hauteskundeemaitzaktokian__ehunekoa"),
            ),
            default=0,
            output_field=FloatField(),
        )
    )

    """
    if len(children)==1:
        annotations['botoak'] = Sum(Case(When(hauteskundeatokian__hauteskundeemaitzaktokian__alderdia=alderdia, hauteskundeatokian__tokia__pk=children[0], then=F('hauteskundeatokian__hauteskundeemaitzaktokian__botoak')),default=0,output_field=IntegerField()))
        annotations['botoak_guztira'] = Sum(Case(When( hauteskundeatokian__tokia__pk=children[0], then=F('hauteskundeatokian__hauteskundeemaitzaktokian__botoak')),default=0,output_field=IntegerField()))
        annotations['eserlekuak'] = Sum(Case(When(hauteskundeatokian__hauteskundeemaitzaktokian__alderdia=alderdia, hauteskundeatokian__tokia__pk=children[0], then=F('hauteskundeatokian__hauteskundeemaitzaktokian__jarlekuak')),default=0,output_field=IntegerField()))
    else:
        annotations['botoak'] = Sum(Case(When(hauteskundeatokian__hauteskundeemaitzaktokian__alderdia=alderdia, hauteskundeatokian__tokia__in=children, then=F('hauteskundeatokian__hauteskundeemaitzaktokian__botoak')),default=0,output_field=IntegerField()))
        annotations['botoak_guztira'] = Sum(Case(When( hauteskundeatokian__tokia__in=children, then=F('hauteskundeatokian__hauteskundeemaitzaktokian__botoak')),default=0,output_field=IntegerField()))
        annotations['eserlekuak'] = Sum(Case(When(hauteskundeatokian__hauteskundeemaitzaktokian__alderdia=alderdia, hauteskundeatokian__tokia__in=children, then=F('hauteskundeatokian__hauteskundeemaitzaktokian__jarlekuak')),default=0,output_field=IntegerField()))
    """
    het = (
        Hauteskundea.objects.filter(is_public=True)
        .annotate(**annotations)
        .order_by("eguna")
    )

    tor = {}
    tor["taula"] = het
    return tor


def alderdia_motak(queryset):
    """ """
    h = {}
    for hm in HauteskundeMota.objects.filter(is_public=True).order_by("order"):
        h[hm] = []

    for item in queryset:
        if item.botoak_guztira:
            h[item.mota].append(item)

    tor = []
    for k, v in h.items():
        h2 = {}
        h2["mota"] = k
        h2["datuak"] = v
        if len(v):
            tor.append(h2)

    tor = sorted(tor, key=lambda x: x["mota"].order)
    return tor


class HauteskundeAlderdiaView(TemplateView):

    template_name = "tk_hauteskundeak/hauteskunde_alderdia.html"

    def get_context_data(self, **kwargs):
        context = super(HauteskundeAlderdiaView, self).get_context_data(**kwargs)

        tokia = get_tokia(self.kwargs)
        obj = get_object_or_404(Alderdia, slug=self.kwargs["slug"])
        hauteskundeak = []

        emaitzak = osatu_alderdiaren_taula(obj, tokia)

        context["taula"] = emaitzak["taula"]
        context["taula_motak"] = alderdia_motak(emaitzak["taula"])

        context["emaitza"] = emaitzak
        context["tokiak"] = get_tokiak()
        context["tokia"] = tokia
        context["hauteskundeak"] = []  # hauteskundeak
        context["oharrak"] = get_oharrak(
            alderdiak=[
                obj,
            ]
        )
        context["object"] = obj

        meta_url = reverse(
            "hauteskundeak_alderdia_tokia",
            kwargs={"slug": obj.slug, "slug_tokia": tokia.slug},
        )
        meta_title = "Hauteskundeak: {} - {}".format(obj.izena, tokia.izena)

        context["meta"] = Meta(meta_url, title=meta_title)

        return context


def osatu_alderdiaren_lista(tokia):
    """
    ALDERDIEN ZERRENDA
    """

    children = list(tokia.get_children().values_list("pk", flat=True))
    children.append(tokia.pk)

    hauteskundeak = Hauteskundea.objects.filter(is_public=True).order_by("-eguna")
    if not hauteskundeak.exists():
        return None

    azken_hauteskundea = hauteskundeak.first()

    annotations = {}

    annotations["botoak_azkena"] = Sum(
        Case(
            When(
                hauteskundeemaitzaktokian__hauteskundeatokian__hauteskundea=azken_hauteskundea,
                then=F("hauteskundeemaitzaktokian__botoak"),
            ),
            default=0,
            output_field=IntegerField(),
        )
    )
    annotations["kopurua"] = Count(
        "hauteskundeemaitzaktokian__hauteskundeatokian__hauteskundea",
        distinct=True,
    )
    annotations["guztira"] = Sum("hauteskundeemaitzaktokian__botoak")

    if len(children) == 1:
        het = (
            Alderdia.objects.filter(
                hauteskundeemaitzaktokian__hauteskundeatokian__tokia__pk=children[0]
            )
            .annotate(**annotations)
            .filter(kopurua__gt=0)
            .order_by("-show_in_page", "-botoak_azkena", "-guztira", "-kopurua")
        )

    else:
        het = (
            Alderdia.objects.filter(
                hauteskundeemaitzaktokian__hauteskundeatokian__tokia__in=children
            )
            .annotate(**annotations)
            .filter(kopurua__gt=0)
            .order_by("-show_in_page", "-botoak_azkena", "-guztira", "-kopurua")
        )

    return het


class HauteskundeAlderdiakListView(TemplateView):

    template_name = "tk_hauteskundeak/hauteskunde_alderdiak_list.html"

    def get_context_data(self, **kwargs):
        context = super(HauteskundeAlderdiakListView, self).get_context_data(**kwargs)

        tokia = get_tokia(self.kwargs)
        tokiak = get_tokiak()

        context["alderdiak"] = osatu_alderdiaren_lista(tokia)
        context["tokiak"] = tokiak
        context["tokia"] = tokia

        meta_url = reverse(
            "hauteskundeak_alderdiak_list_tokia",
            kwargs={"slug_tokia": tokia.slug},
        )
        meta_title = "Hauteskundeak: alderdien zerrenda - {}".format(tokia.izena)
        context["meta"] = Meta(meta_url, title=meta_title)

        return context


class HauteskundeListView(TemplateView):

    template_name = "tk_hauteskundeak/hauteskunde_list.html"

    def get_context_data(self, **kwargs):
        context = super(HauteskundeListView, self).get_context_data(**kwargs)

        tokia = get_tokia(self.kwargs)
        tokiak = get_tokiak()

        context["hauteskundeak"] = get_hauteskundeak_info(
            tokia=tokia, order_by="-eguna"
        )
        context["tokiak"] = tokiak
        context["tokia"] = tokia

        meta_url = reverse(
            "hauteskundeak_hauteskundeak_list_tokia",
            kwargs={"slug_tokia": tokia.slug},
        )
        meta_title = "Hauteskunde guztien zerrenda - {}".format(tokia.izena)
        context["meta"] = Meta(meta_url, title=meta_title)

        return context


def markatu_alderdien_booleanoak():
    """
    Alderdi bakoitzaren booleanoak markatu
    show_in_table > %2 TABLE_MIN
    show_in_graphs > %5 GRAPH_MIN
    show_in_page > %5 PAGE_MIN
    """
    TABLE_MIN = 2
    GRAPH_MIN = 5
    PAGE_MIN = 10
    tokia = get_tokia({})
    Alderdia.objects.all().update(
        show_in_table=False, show_in_graphs=False, show_in_page=False
    )
    hauteskundeak_info = get_hauteskundeak_info(tokia=tokia, order_by="-eguna")
    for hauteskundea in Hauteskundea.objects.all():
        ema = osatu_hauteskundeen_taula(
            [
                hauteskundea,
            ],
            tokia,
        )
        for alderdia in ema["taula"]:
            for h_info in hauteskundeak_info:
                if h_info == hauteskundea:
                    botoak_guztira = h_info.botoak
            ehunekoa = alderdia.botoak_0 * 100.0 / botoak_guztira
            aldatu = False
            if ehunekoa > TABLE_MIN:
                alderdia.show_in_table = True
                aldatu = True
            if ehunekoa > PAGE_MIN:
                alderdia.show_in_page = True
                aldatu = True
            if ehunekoa > GRAPH_MIN:
                alderdia.show_in_graphs = True
                aldatu = True
            if aldatu:
                alderdia.save()
        print("{}".format(hauteskundea.izena))


def konprobatu_emaitzak():
    """
    Toki hauetan emaitzak eta boto kopuruak kointziditzen duten begiratu; herrietan soilik
    """
    tokiak = get_tokiak().filter(mota=1)
    hauteskundeak = Hauteskundea.objects.filter(is_public=True)

    tor = []
    for hauteskundea in hauteskundeak:
        for tokia in tokiak:
            try:
                obj = HauteskundeaTokian.objects.get(
                    hauteskundea=hauteskundea, tokia=tokia
                )
                boto_kopurua = obj.get_hautagai_zerrenden_botoak()
                annotations = {}
                annotations["botoak"] = Sum("botoak")
                boto_kopurua_2 = (
                    HauteskundeEmaitzakTokian.objects.filter(hauteskundeatokian=obj)
                    .aggregate(Sum("botoak"))
                    .get("botoak__sum", 0)
                )
                if boto_kopurua_2 == boto_kopurua:
                    # print('OK: ONDO dago {} {}'.format(tokia.izena,hauteskundea.izena))
                    pass
                else:
                    h2 = {}
                    h2["msg"] = "Kopuru OKERRAK"
                    h2["hauteskundea"] = hauteskundea
                    h2["tokia"] = tokia
                    h2["kop1"] = boto_kopurua
                    h2["kop2"] = boto_kopurua_2
                    h2["kop_dif"] = boto_kopurua_2 - boto_kopurua
                    h2["obj"] = obj
                    tor.append(h2)
                    # print('KO: ZERBAIT gaizki zenbakietan {} {} ({} / {})'.format(hauteskundea.izena, tokia.izena, boto_kopurua, boto_kopurua_2))

            except:
                h2 = {}
                h2["msg"] = "Daturik EZ"
                h2["hauteskundea"] = hauteskundea
                h2["tokia"] = tokia
                h2["kop1"] = 0
                h2["kop2"] = 0
                h2["kop_dif"] = 0
                h2["obj"] = None
                tor.append(h2)
    return tor
    # print('KO: ez dago emaitzik {} {}'.format(hauteskundea.izena,tokia.izena,))


def errepikatutako_emaitzak_borratu():
    """ """
    tokiak = Tokia.objects.all().filter(mota=1)
    hauteskundeak = Hauteskundea.objects.all()

    for tokia in tokiak:
        for hauteskundea in hauteskundeak:
            het = HauteskundeaTokian.objects.filter(
                hauteskundea=hauteskundea, tokia=tokia
            ).order_by("pk")
            if het.exists() and het.count() > 1:
                # borratu bat ez beste guztiak
                last_pk = het.last().pk
                HauteskundeaTokian.objects.filter(
                    hauteskundea=hauteskundea, tokia=tokia, pk__lt=last_pk
                ).delete()
                print(tokia.izena)


def zuriak_txukundu():
    """ """
    zurien_alderdia = Alderdia.objects.get(pk=5523)
    for het in HauteskundeEmaitzakTokian.objects.filter(alderdia=zurien_alderdia):
        ht = het.hauteskundeatokian
        ht.zuriak = het.botoak
        ht.save()


class HauteskundeaViewIframeGraph(HauteskundeaSimpleView):
    template_name = "tk_hauteskundeak/iframe_hauteskundea_graph.html"


class HauteskundeaViewIframePie(HauteskundeaSimpleView):
    template_name = "tk_hauteskundeak/iframe_hauteskundea_pie.html"


class HauteskundeaViewIframeMap(HauteskundeaSimpleView):
    template_name = "tk_hauteskundeak/iframe_hauteskundea_map.html"


class HauteskundeaViewIframeZinegotziak(HauteskundeaSimpleView):
    template_name = "tk_hauteskundeak/iframe_hauteskundea_zinegotziak.html"


class HauteskundeaViewIframeTable(HauteskundeaSimpleView):
    template_name = "tk_hauteskundeak/iframe_hauteskundea_table.html"


class HauteskundeaCompareViewIframeGraph(HauteskundeaSimpleCompareView):
    template_name = "tk_hauteskundeak/iframe_hauteskundea_compare_graph.html"


class HauteskundeaCompareViewIframeTable(HauteskundeaSimpleCompareView):
    template_name = "tk_hauteskundeak/iframe_hauteskundea_compare_table.html"


from django.utils import timezone
from datetime import timedelta
from django.conf import settings


def update_iframe(request, iframea):
    if iframea.hauteskundea2:
        if iframea.mota == 0:
            bista = HauteskundeaCompareViewIframeGraph.as_view()(
                request,
                slug=iframea.hauteskundea1.slug,
                slug2=iframea.hauteskundea2.slug,
                slug_tokia=iframea.tokia.slug,
            )
        else:
            bista = HauteskundeaCompareViewIframeTable.as_view()(
                request,
                slug=iframea.hauteskundea1.slug,
                slug2=iframea.hauteskundea2.slug,
                slug_tokia=iframea.tokia.slug,
            )
    else:
        if iframea.mota == 0:
            bista = HauteskundeaViewIframeGraph.as_view()(
                request,
                slug=iframea.hauteskundea1.slug,
                slug_tokia=iframea.tokia.slug,
            )
        elif iframea.mota == 1:
            bista = HauteskundeaViewIframeTable.as_view()(
                request,
                slug=iframea.hauteskundea1.slug,
                slug_tokia=iframea.tokia.slug,
            )
        elif iframea.mota == 2:
            bista = HauteskundeaViewIframePie.as_view()(
                request,
                slug=iframea.hauteskundea1.slug,
                slug_tokia=iframea.tokia.slug,
            )
        elif iframea.mota == 3:
            bista = HauteskundeaViewIframeMap.as_view()(
                request,
                slug=iframea.hauteskundea1.slug,
                slug_tokia=iframea.tokia.slug,
            )
        elif iframea.mota == 4:
            bista = HauteskundeaViewIframeZinegotziak.as_view()(
                request,
                slug=iframea.hauteskundea1.slug,
                slug_tokia=iframea.tokia.slug,
            )
        else:
            bista = HauteskundeaViewIframeTable.as_view()(
                request,
                slug=iframea.hauteskundea1.slug,
                slug_tokia=iframea.tokia.slug,
            )

    bista.render()
    html = """<p>Oraindik ezin izan dira datuak erauzi.</strong> Itxaron mesedez hurrengo saiakerara. Datuak 10 minututik behin eguneratzen dira.</p>"""
    if bista.content:
        html = bista.content.decode("utf-8")
    iframea.html = html
    return iframea


HAUTESKUNDE_IFRAME_MINUTES = getattr(settings, "HAUTESKUNDE_IFRAME_MINUTES", 5)


class HauteskundeaIframeView(DetailView):
    template_name = "tk_hauteskundeak/iframe.html"
    model = HauteskundeaIframe

    def get_context_data(self, **kwargs):
        context = super(HauteskundeaIframeView, self).get_context_data(**kwargs)
        iframea = self.get_object()

        if iframea.modified < timezone.now() - timedelta(
            minutes=HAUTESKUNDE_IFRAME_MINUTES
        ):
            # edukia zaharra denez, berritu
            iframea = update_iframe(self.request, iframea)
            iframea.save()

        context["iframea"] = iframea
        return context


from .models import (
    HauteskundeaCache,
    HauteskundeaCacheMota,
    HauteskundeaCacheCompare,
)


def get_kp_cache_minutes():
    try:
        return HauteskundeKP.objects.get(is_public=True).minutes
    except:
        return 0


class CacheHauteskundeaMota(TemplateView):
    template_name = "tk_hauteskundeak/cache_hauteskundea.html"

    def get_context_data(self, **kwargs):
        context = super(CacheHauteskundeaMota, self).get_context_data(**kwargs)

        HAUTESKUNDE_CACHE_MINUTES = get_kp_cache_minutes()

        tokia = get_tokia(self.kwargs)
        mota = get_object_or_404(HauteskundeMota, slug=self.kwargs["slug"])

        qs = HauteskundeaCacheMota.objects.filter(tokia=tokia, mota=mota)

        if qs.exists():
            obj = qs.first()
            if obj.modified > timezone.now() - timedelta(
                minutes=HAUTESKUNDE_CACHE_MINUTES
            ):
                context["object"] = obj
                return context
        else:
            obj = HauteskundeaCacheMota()
            obj.tokia = tokia
            obj.mota = mota
            obj.save()

        bista = HauteskundeMotaView.as_view()(
            self.request, slug=mota.slug, slug_tokia=tokia.slug
        )
        bista.render()
        obj.html = bista.content.decode("utf-8")
        obj.save()
        context["object"] = obj
        return context


class CacheHauteskundea(TemplateView):
    template_name = "tk_hauteskundeak/cache_hauteskundea.html"

    def get_context_data(self, **kwargs):
        context = super(CacheHauteskundea, self).get_context_data(**kwargs)

        HAUTESKUNDE_CACHE_MINUTES = get_kp_cache_minutes()

        tokia = get_tokia(self.kwargs)
        hauteskundea = get_object_or_404(Hauteskundea, slug=self.kwargs["slug"])

        qs = HauteskundeaCache.objects.filter(tokia=tokia, hauteskundea=hauteskundea)

        if qs.exists():
            obj = qs.first()
            if obj.modified > timezone.now() - timedelta(
                minutes=HAUTESKUNDE_CACHE_MINUTES
            ):
                context["object"] = obj
                return context
        else:
            obj = HauteskundeaCache()
            obj.tokia = tokia
            obj.hauteskundea = hauteskundea
            obj.save()

        bista = HauteskundeaView.as_view()(
            self.request, slug=hauteskundea.slug, slug_tokia=tokia.slug
        )
        # bista = HauteskundeaSimpleView.as_view()(self.request,slug=hauteskundea.slug, slug_tokia=tokia.slug)
        bista.render()
        obj.html = bista.content.decode("utf-8")
        obj.save()
        context["object"] = obj
        return context


class CacheHauteskundeaCompare(TemplateView):
    template_name = "tk_hauteskundeak/cache_hauteskundea.html"

    def get_context_data(self, **kwargs):
        context = super(CacheHauteskundeaCompare, self).get_context_data(**kwargs)

        HAUTESKUNDE_CACHE_MINUTES = get_kp_cache_minutes()

        tokia = get_tokia(self.kwargs)
        hauteskundea1 = get_object_or_404(Hauteskundea, slug=self.kwargs["slug"])
        hauteskundea2 = get_object_or_404(Hauteskundea, slug=self.kwargs["slug2"])

        qs = HauteskundeaCacheCompare.objects.filter(
            tokia=tokia,
            hauteskundea1=hauteskundea1,
            hauteskundea2=hauteskundea2,
        )

        if qs.exists():
            obj = qs.first()
            if obj.modified > timezone.now() - timedelta(
                minutes=HAUTESKUNDE_CACHE_MINUTES
            ):
                context["object"] = obj
                return context
        else:
            obj = HauteskundeaCacheCompare()
            obj.tokia = tokia
            obj.hauteskundea1 = hauteskundea1
            obj.hauteskundea2 = hauteskundea2
            obj.save()

        bista = HauteskundeaCompareView.as_view()(
            self.request,
            slug=hauteskundea1.slug,
            slug2=hauteskundea2.slug,
            slug_tokia=tokia.slug,
        )
        # bista = HauteskundeaSimpleCompareView.as_view()(self.request,slug=hauteskundea1.slug, slug2=hauteskundea2.slug, slug_tokia=tokia.slug)
        bista.render()
        obj.html = bista.content.decode("utf-8")
        obj.save()
        context["object"] = obj
        return context


def get_eskrutinioak(qs):

    errolda_totala = 0
    batura = 0

    for haute_tok in qs:
        esk_herria = haute_tok.eskrutinioa
        errolda_herria = haute_tok.errolda
        errolda_totala += errolda_herria
        batura += esk_herria * errolda_herria

    if not errolda_totala:
        return 0
    return batura / errolda_totala


def sortu_eskualdeko_datuak(hauteskundea):
    tokiak = Tokia.objects.filter(
        is_public=True, mota__gt=1, herriak__isnull=False
    ).distinct()

    for tokia in tokiak:
        # borratu emaitza zaharrak
        HauteskundeEmaitzakTokian.objects.filter(
            hauteskundeatokian__tokia=tokia,
            hauteskundeatokian__hauteskundea=hauteskundea,
        ).delete()

        # sortu berria
        children = list(tokia.get_children().values_list("pk", flat=True))

        qs = HauteskundeaTokian.objects.filter(
            hauteskundea=hauteskundea, tokia__in=children
        )

        if not qs:
            continue

        eskrutinioa = get_eskrutinioak(qs)
        aggegations = {}
        aggegations["errolda"] = Sum("errolda")
        aggegations["boto_emaileak"] = Sum("boto_emaileak")
        aggegations["baliogabeak"] = Sum("baliogabeak")
        aggegations["zuriak"] = Sum("zuriak")
        aggegations["botoak"] = Sum("alderdien_botoak")
        aggegations["jarlekuak"] = Sum("jarlekuen_kopurua")
        qs = qs.aggregate(**aggegations)

        if not qs["errolda"]:
            continue

        htg = HauteskundeaTokian.objects.get(tokia=tokia, hauteskundea=hauteskundea)
        # htg.tokia = tokia
        # htg.hauteskundea = hauteskundea
        htg.errolda = qs["errolda"]
        htg.jarlekuen_kopurua = qs["jarlekuak"]
        htg.boto_emaileak = qs["boto_emaileak"]
        htg.baliogabeak = qs["baliogabeak"]
        htg.zuriak = qs["zuriak"]
        htg.eskrutinioa = eskrutinioa
        htg.save()

        # Eta alderdien botoak

        annotations = {}
        annotations["botoak"] = Sum("hauteskundeemaitzaktokian__botoak")
        annotations["jarlekuak"] = Sum("hauteskundeemaitzaktokian__jarlekuak")
        qs = (
            Alderdia.objects.filter(
                hauteskundeemaitzaktokian__hauteskundeatokian__tokia__in=children,
                hauteskundeemaitzaktokian__hauteskundeatokian__hauteskundea=hauteskundea,
            )
            .annotate(**annotations)
            .order_by("-botoak")
        )

        for q in qs:
            het = HauteskundeEmaitzakTokian()
            het.hauteskundeatokian = htg
            het.alderdia = q
            het.botoak = q.botoak
            het.jarlekuak = q.jarlekuak
            het.save()

    return True
