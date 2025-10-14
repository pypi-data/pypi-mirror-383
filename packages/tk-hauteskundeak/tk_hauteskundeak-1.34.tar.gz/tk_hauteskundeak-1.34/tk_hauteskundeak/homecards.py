from django.test.client import RequestFactory
from .views import HauteskundeaView, HauteskundeaCompareView, HauteskundeaPortadaView


class HauteskundeaViewHomeMap(HauteskundeaPortadaView):
    template_name = "tk_hauteskundeak/homecard/hauteskundea_map.html"


class HauteskundeaViewCompareGraph(HauteskundeaCompareView):
    template_name = "tk_hauteskundeak/homecard/hauteskundea_compare_graph.html"


class HauteskundeaViewCompareTable(HauteskundeaCompareView):
    template_name = "tk_hauteskundeak/homecard/hauteskundea_compare_table.html"


def home_html_blokea_eskualdea(hauteskundea, tokia):
    """ """
    if hauteskundea and tokia:
        factory = RequestFactory()
        request = factory.get(
            "/hauteskundea/{}/{}".format(hauteskundea.slug, tokia.slug)
        )
        bista = HauteskundeaViewHomeMap.as_view()(
            request, slug=hauteskundea.slug, slug_tokia=tokia.slug
        )
        bista.render()
        return bista.content.decode("utf-8")
    else:
        return ""


def home_html_blokea_alderaketa(hauteskundea, hauteskundea2, tokia):
    """ """
    if hauteskundea and hauteskundea2 and tokia:
        factory = RequestFactory()
        request = factory.get(
            "/hauteskundea/{}vs{}/{}".format(
                hauteskundea.slug, hauteskundea2.slug, tokia.slug
            )
        )
        bista = HauteskundeaViewCompareGraph.as_view()(
            request,
            slug=hauteskundea.slug,
            slug2=hauteskundea2.slug,
            slug_tokia=tokia.slug,
        )
        bista.render()
        return bista.content.decode("utf-8")
    else:
        return ""


def home_html_blokea_alderaketa_taula(hauteskundea, hauteskundea2, tokia):
    """ """
    if hauteskundea and hauteskundea2 and tokia:
        factory = RequestFactory()
        request = factory.get(
            "/hauteskundea/{}vs{}/{}".format(
                hauteskundea.slug, hauteskundea2.slug, tokia.slug
            )
        )
        bista = HauteskundeaViewCompareTable.as_view()(
            request,
            slug=hauteskundea.slug,
            slug2=hauteskundea2.slug,
            slug_tokia=tokia.slug,
        )
        bista.render()
        return bista.content.decode("utf-8")
    else:
        return ""
