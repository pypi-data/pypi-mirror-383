from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework import generics

from .serializers import (
    HauteskundeaSerializer,
    HauteskundeaTokianSerializer,
    HauteskundeaTokianSerializer2,
    HauteskundeEserlekuakTokianSerializer,
    TokiaSerializer,
    AlderdiaSerializer,
    HauteskundeEmaitzaSerializer,
)

from tk_hauteskundeak.models import (
    Hauteskundea,
    HauteskundeaTokian,
    HauteskundeEserlekuakTokian,
    Tokia,
)
from tk_hauteskundeak.views import *
from photologue.models import Photo

from .views import osatu_hauteskunde_baten_info_dena


def get_emaitza(prev_tokian, slug):
    if prev_tokian.hauteskundeemaitzaktokian_set.filter(alderdia__slug=slug).exists():
        alderdia = prev_tokian.hauteskundeemaitzaktokian_set.filter(
            alderdia__slug=slug
        ).first()
        return alderdia.botoak, alderdia.jarlekuak, alderdia.ehunekoa
    return "-", "-", "-"


class HauteskundeaSimpleApiView(APIView, HauteskundeaSimpleView):
    def get(self, request, *args, **kwargs):

        hauteskundea_serializer = HauteskundeaSerializer(
            self.get_context_data()["object"], context={"request": request}
        )

        # Hauteskunde hau
        hauteskundea = self.get_context_data()["object"]
        hauteskundea_tokian = HauteskundeaTokian.objects.get(
            hauteskundea=hauteskundea, tokia__slug=kwargs["slug_tokia"]
        )
        hauteskundea_tokian_serializer = HauteskundeaTokianSerializer(
            hauteskundea_tokian, context={"request": request}
        )

        # Mota bereako aurreko hauteskundea
        prev_hauteskundea = (
            Hauteskundea.objects.filter(
                mota=hauteskundea.mota, eguna__lt=hauteskundea.eguna
            )
            .exclude(id=hauteskundea.id)
            .order_by("eguna")
            .last()
        )
        try:
            prev_tokian = HauteskundeaTokian.objects.get(
                hauteskundea=prev_hauteskundea, tokia__slug=kwargs["slug_tokia"]
            )
        except:
            prev_tokian = None
        aurreko_hauteskundea_serializer = HauteskundeaTokianSerializer(
            prev_tokian, context={"request": request}
        )

        taula = self.get_context_data()["info"]["taula"]
        aurrekoan_eserlekuak_qs = HauteskundeEserlekuakTokian.objects.filter(
            hauteskundeatokian=prev_tokian
        ).order_by("ordena")
        aurrekoan_eserlekuak_serializer = HauteskundeEserlekuakTokianSerializer(
            aurrekoan_eserlekuak_qs, many=True, context={"request": request}
        )
        eserlekuak_qs = HauteskundeEserlekuakTokian.objects.filter(
            hauteskundeatokian=hauteskundea_tokian
        ).order_by("ordena")
        eserlekuak_serializer = HauteskundeEserlekuakTokianSerializer(
            eserlekuak_qs, many=True, context={"request": request}
        )

        taula_berria = []

        for item in taula:
            item_berria = item
            aurrekoan_botoak, aurrekoan_eserlekuak_alderdia, aurrekoan_ehunekoa = (
                get_emaitza(prev_tokian, item["alderdia__slug"])
            )
            item_berria["aurreko_hauteskundea"] = prev_hauteskundea.izena
            item_berria["aurrekoan_botoak"] = aurrekoan_botoak
            item_berria["aurrekoan_eserlekuak"] = aurrekoan_eserlekuak_alderdia
            item_berria["aurrekoan_ehunekoa"] = aurrekoan_ehunekoa

            try:
                item_berria["logoa"] = Photo.objects.get(
                    pk=item["alderdia__logoa"]
                ).get_tokikom_700x700_url()
            except:
                item_berria["logoa"] = ""

            taula_berria.append(item_berria)

        dena = {
            "aurreko_hauteskundea": aurreko_hauteskundea_serializer.data,
            "oraingo_hauteskundea": hauteskundea_tokian_serializer.data,
            "taula": taula_berria,
            "eserlekuak": eserlekuak_serializer.data,
            "aurrekoan_eserlekuak": aurrekoan_eserlekuak_serializer.data,
        }
        return Response(dena)


class HauteskundeaSimpleApiViewTokiak(APIView, HauteskundeaSimpleView):
    def get(self, request, *args, **kwargs):
        itzuli = {}
        for tokia in Tokia.objects.filter(is_public=True):
            try:
                hauteskundea_serializer = HauteskundeaSerializer(
                    self.get_context_data()["object"], context={"request": request}
                )

                # Hauteskunde hau
                hauteskundea = self.get_context_data()["object"]
                hauteskundea_tokian = HauteskundeaTokian.objects.get(
                    hauteskundea=hauteskundea, tokia__slug=tokia.slug
                )
                hauteskundea_tokian_serializer = HauteskundeaTokianSerializer(
                    hauteskundea_tokian, context={"request": request}
                )

                info = osatu_hauteskunde_baten_info_dena(hauteskundea, tokia)

                taula = info["taula"]
                taula_berria = []

                for item in taula:
                    item_berria = item

                    try:
                        item_berria["logoa"] = Photo.objects.get(
                            pk=item["alderdia__logoa"]
                        ).get_tokikom_700x700_url()
                    except:
                        item_berria["logoa"] = ""

                    taula_berria.append(item_berria)

                dena = {
                    "oraingo_hauteskundea": hauteskundea_tokian_serializer.data,
                    "taula": taula_berria,
                }
                itzuli[tokia.slug] = dena
            except:
                print(tokia.slug)

        return Response(itzuli)


class HauteskundeaSVGApiView(APIView, HauteskundeaSimpleView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = "tk_hauteskundeak/include/svg.html"
    pagination_class = None
    paginator = None

    def get(self, request, *args, **kwargs):
        hauteskundea = self.get_context_data()["object"]
        queryset = HauteskundeaTokian.objects.get(
            hauteskundea=hauteskundea, tokia__slug=kwargs["slug_tokia"]
        )
        tokia = get_tokia(self.kwargs)
        herriak = tokia.get_children()

        if herriak:
            herriak2 = get_hauteskundea_tokiak_irabazleak(hauteskundea, herriak)

        return Response({"herriak": herriak2})


class HauteskundeaTokiaView(generics.ListAPIView):
    queryset = Tokia.objects.all()
    serializer_class = TokiaSerializer
    pagination_class = None
    paginator = None


class AlderdiakView(APIView, HauteskundeaSimpleView):
    queryset = Alderdia.objects.all()
    serializer_class = AlderdiaSerializer
    pagination_class = None
    paginator = None

    def get(self, request, *args, **kwargs):
        hauteskundea = self.get_context_data()["object"]
        hauteskundeak_tokian = HauteskundeaTokian.objects.filter(
            hauteskundea=hauteskundea
        )

        alderdiak = []

        for haut_tok in hauteskundeak_tokian:
            for emaitza in haut_tok.hauteskundeemaitzaktokian_set.all():
                if not emaitza.alderdia in alderdiak:
                    alderdiak.append(emaitza.alderdia)

        alderdiak_serializer = AlderdiaSerializer(
            alderdiak, many=True, context={"request": request}
        )

        return Response(alderdiak_serializer.data)


class HauteskundeaAlderdiaView(APIView, HauteskundeaSimpleView):
    pagination_class = None

    def get(self, request, *args, **kwargs):
        hauteskundea = self.get_context_data()["object"]
        hauteskundeak_tokian = HauteskundeaTokian.objects.filter(
            hauteskundea=hauteskundea
        )
        zerrenda = []

        for haut_tok in hauteskundeak_tokian:
            tokian_alderdia = haut_tok.hauteskundeemaitzaktokian_set.filter(
                alderdia__slug=kwargs["slug_alderdia"]
            ).first()

            if tokian_alderdia:
                zerrenda.append(tokian_alderdia)

        emaitzak_serializer = HauteskundeEmaitzaSerializer(
            zerrenda, many=True, context={"request": request}
        )

        return Response({"zerrenda": emaitzak_serializer.data})


class HauteskundeaIrabazleakTokia(APIView, HauteskundeaSimpleView):
    pagination_class = None

    def get(self, request, *args, **kwargs):
        hauteskundea = self.get_context_data()["object"]
        queryset = HauteskundeaTokian.objects.get(
            hauteskundea=hauteskundea, tokia__slug=kwargs["slug_tokia"]
        )
        tokia = get_tokia(self.kwargs)
        herriak = tokia.get_children()

        if herriak:
            herriak2 = get_hauteskundea_tokiak_irabazleak(hauteskundea, herriak)
        itzuli = {}
        for herria in herriak2:
            if not isinstance(herria["irabazlea"], str):
                if not herria["irabazlea"].slug in itzuli.keys():
                    logoa = (
                        herria["irabazlea"].logoa
                        and herria["irabazlea"].logoa.image.url
                        or ""
                    )
                    itzuli[herria["irabazlea"].slug] = {
                        "herriak": [],
                        "irabazlea_akronimoa": herria["irabazlea"].akronimoa,
                        "irabazlea_kolorea": herria["irabazlea"].kolorea,
                        "irabazlea_logoa": logoa,
                    }

                itzuli[herria["irabazlea"].slug]["herriak"].append(herria["tokia"].slug)

            """


            itzuli.append({'herria':herria['tokia'].slug,
                           'irabazlea':herria['irabazlea'].slug,
                           'irabazlea_akronimoa':herria['irabazlea'].akronimoa,
                           'irabazlea_kolorea':herria['irabazlea'].kolorea,
                           'irabazlea_logoa':logoa})
            """
        return Response({"irabazleak": itzuli})


"""
class EserlekuakViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HauteskundeEserlekuakTokianSerializer

    def get_queryset(self):
        eserlekuak = HauteskundeEserlekuakTokian.objects.filter(hauteskundeatokian=prev_tokian)

        tokia = 'a'
        return HauteskundeEserlekuakTokian.objects.filter(
            hauteskundeatokian__tokia=tokia,
            hauteskundeatokian__hauteskundea=hauteskundea,
            is_selected=True,
        ).order_by("ordena")


"""
