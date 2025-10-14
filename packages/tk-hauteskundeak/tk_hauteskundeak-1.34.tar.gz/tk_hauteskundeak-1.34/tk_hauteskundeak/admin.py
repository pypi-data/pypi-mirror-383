from django.contrib import admin

# from django.conf import settings
# from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.db.models import Q
from django import forms
from .models import (
    Tokia,
    HauteskundeMota,
    Hauteskundea,
    HauteskundeaTokian,
    HauteskundeEmaitzakTokian,
    Alderdia,
    HauteskundeEserlekuakTokian,
    HauteskundeOharrak,
    HauteskundeKP,
    HauteskundeaKargatu,
    HauteskundeaIframe,
    HauteskundeaCache,
    HauteskundeaCacheCompare,
    HauteskundeaCacheMota,
    APIResourceConfig,
)
from django.urls import reverse
from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

from django.db import transaction
from django_object_actions import DjangoObjectActions
import csv
from django.http import HttpResponse
from django_object_actions import DjangoObjectActions
from .views import osatu_hauteskundeen_taula, get_tokia
from django.utils import timezone
from django.template.defaultfilters import slugify
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class TokiaAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "izena",
        "mota",
        "herri_kodea",
        "lurralde_kodea",
        "get_herriak_kopurua",
        "order_col",
        "order_list",
        "is_public",
        "is_default",
        "get_hauteskundeak_kopurua",
    )
    list_editable = (
        "order_col",
        "order_list",
    )
    list_display_links = (
        "slug",
        "izena",
    )
    search_fields = [
        "izena",
    ]
    prepopulated_fields = {"slug": ("izena",)}
    list_filter = ("mota", "is_public")
    raw_id_fields = ("herriak",)
    readonly_fields = ("added", "modified")

    actions = ["batu_tokia"]

    def batu_tokia(self, request, queryset):
        if "apply" in request.POST:
            # The user clicked submit on the intermediate form.
            # Perform our update action:
            # queryset.update(status='NEW_STATUS')
            # HEMEN EGIN GURE LANA
            toki_berria = Tokia.objects.get(pk=request.POST.get("toki_berria"))
            for tokia in queryset:
                HauteskundeaTokian.objects.filter(tokia=tokia).update(
                    tokia=toki_berria
                )

            # Redirect to our admin view after our update has
            # completed with a nice little info message saying
            # our models have been updated:
            self.message_user(
                request, "Tokia batuta: {} toki".format(queryset.count())
            )
            return HttpResponseRedirect(request.get_full_path())
        context = {}
        context["tokiak"] = Tokia.objects.filter(is_public=True)
        context["tokia"] = queryset
        return render(
            request, "tk_hauteskundeak/admin/batu_tokia.html", context=context
        )

    batu_tokia.short_description = "Batu toki hau beste batera"


class HauteskundeMotaAdmin(admin.ModelAdmin):
    list_display = ("slug", "order", "akronimoa", "izena")
    list_display_links = (
        "slug",
        "izena",
    )
    prepopulated_fields = {"slug": ("izena",)}
    raw_id_fields = ("irudia",)
    search_fields = [
        "izena",
    ]
    readonly_fields = ("added", "modified")


class HauteskundeEmaitzakTokianInlineOrokorra(admin.TabularInline):
    model = HauteskundeaTokian
    extra = 2
    fields = (
        "tokia",
        "jarlekuen_kopurua",
        "errolda",
        "boto_emaileak",
        "baliogabeak",
        "zuriak",
        "eskrutinioa",
    )

    def get_queryset(self, request):
        qs = super(HauteskundeEmaitzakTokianInlineOrokorra, self).get_queryset(
            request
        )
        return qs.filter(tokia__is_public=True)


def sortu_kopia_bat(hauteskundea):
    """ """
    orain = timezone.now()
    izena = "{} {}".format(hauteskundea.mota.izena, orain.year)
    izen_motza = "{}{}".format(hauteskundea.mota.akronimoa, orain.year)
    slug = slugify(izena)

    if Hauteskundea.objects.filter(slug=slug).exists():
        slug = "{}-{}".format(slug, orain.month)

    if Hauteskundea.objects.filter(izen_motza=izen_motza).exists():
        izen_motza = "{}{}".format(izen_motza, orain.month)

    berria = Hauteskundea()
    berria.izen_motza = izen_motza
    berria.izena = izena
    berria.slug = slug
    berria.eguna = orain
    berria.mota = hauteskundea.mota
    berria.irudia = hauteskundea.irudia
    berria.is_public = False
    berria.is_closed = False
    berria.save()

    for ht in HauteskundeaTokian.objects.filter(hauteskundea=hauteskundea):
        ht_berria = HauteskundeaTokian()
        ht_berria.hauteskundea = berria
        ht_berria.tokia = ht.tokia
        ht_berria.jarlekuen_kopurua = ht.jarlekuen_kopurua
        ht_berria.save()

        for hte in HauteskundeEmaitzakTokian.objects.filter(
            hauteskundeatokian=ht
        ):
            hte_berria = HauteskundeEmaitzakTokian()
            hte_berria.hauteskundeatokian = ht_berria
            hte_berria.alderdia = hte.alderdia
            hte_berria.save()

    return True


from .views import sortu_eskualdeko_datuak


class HauteskundeaAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = (
        "id",
        "slug",
        "izena",
        "mota",
        "is_public",
        "is_closed",
        "auto_import",
    )
    list_display_links = (
        "slug",
        "izena",
    )
    date_hierarchy = "eguna"
    list_filter = ("mota",)
    prepopulated_fields = {"slug": ("izena",)}
    raw_id_fields = ("irudia",)
    search_fields = ["izen_motza", "izena"]
    inlines = [HauteskundeEmaitzakTokianInlineOrokorra]

    def kalkulatu(self, request, obj):
        sortu_eskualdeko_datuak(obj)
        self.message_user(request, "Eskualdeko datuak kalkulatuta")

    kalkulatu.label = "Kalkulatu eskualdeko datuak"

    def delete_cache(self, request, obj):
        HauteskundeaCache.objects.filter(hauteskundea=obj).delete()
        HauteskundeaCacheCompare.objects.filter(hauteskundea1=obj).delete()
        HauteskundeaCacheCompare.objects.filter(hauteskundea2=obj).delete()
        HauteskundeaCacheMota.objects.filter(mota=obj.mota).delete()
        self.message_user(
            request, "Borratu dugu hauteskunde honen cache guztia"
        )

    delete_cache.label = "Ezabatu cacheak"

    def kopiatu(self, request, obj):
        sortu_kopia_bat(obj)
        self.message_user(request, "Sortuta kopia bat. Joan hara ;-)")

    kopiatu.label = "Kopiatu hauteskunde hau"

    change_actions = ("kalkulatu", "delete_cache", "kopiatu")

    def kalkulatu_qs(self, request, queryset):
        for q in queryset:
            sortu_eskualdeko_datuak(q)
        self.message_user(
            request, "Kalkulatuta: {} hauteskunde".format(queryset.count())
        )
        return HttpResponseRedirect(request.get_full_path())

    kalkulatu_qs.short_description = "Kalkulatu eskualdekoak"

    def kopiatu_qs(self, request, queryset):
        for q in queryset:
            sortu_kopia_bat(q)
        self.message_user(
            request, "Kopiatuta: {} hauteskunde".format(queryset.count())
        )
        return HttpResponseRedirect(request.get_full_path())

    kopiatu_qs.short_description = "Kopiatu hauteskundeak"

    actions = ["kalkulatu_qs", "kopiatu_qs"]


class HauteskundeEmaitzakTokianInline(admin.TabularInline):
    raw_id_fields = ("alderdia",)
    model = HauteskundeEmaitzakTokian
    readonly_fields = ("ehunekoa",)
    extra = 2


class ZinegotziakInline(admin.TabularInline):
    raw_id_fields = (
        "alderdia",
        "argazkia",
    )
    model = HauteskundeEserlekuakTokian
    extra = 2


class TokiaListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "Tokia"

    parameter_name = "tokia"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return Tokia.objects.filter(is_public=True).values_list("pk", "izena")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tokia__id=self.value())
        return queryset


class HauteskundeaTokianAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = (
        "hauteskundea",
        "tokia",
        "jarlekuen_kopurua",
        "errolda",
        "boto_emaileak",
        "baliogabeak",
        "zuriak",
        "alderdien_botoak",
        "itxuraz_ondo",
        "eskrutinioa",
    )
    list_display_links = ("hauteskundea", "tokia")
    list_filter = ("hauteskundea__mota", "hauteskundea", TokiaListFilter)
    ("is_staff", admin.BooleanFieldListFilter)
    search_fields = ["hauteskundea__izena", "tokia__izena"]
    raw_id_fields = (
        "hauteskundea",
        "tokia",
    )
    inlines = [HauteskundeEmaitzakTokianInline, ZinegotziakInline]
    readonly_fields = (
        "added",
        "modified",
        "alderdien_botoak",
        "get_baliozko_botoak_sum",
        "get_jarlekuak_sum",
    )

    fieldsets = (
        ("Datu orokorrak", {"fields": ("hauteskundea", "tokia")}),
        (
            "Kopuruak",
            {
                "fields": (
                    ("jarlekuen_kopurua", "get_jarlekuak_sum"),
                    ("errolda", "eskrutinioa"),
                    (
                        "boto_emaileak",
                        "baliogabeak",
                        "zuriak",
                    ),
                    ("get_baliozko_botoak_sum", "alderdien_botoak"),
                )
            },
        ),
    )

    def get_baliozko_botoak(self, obj):
        return obj.get_hautagai_zerrenden_botoak()

    def get_baliozko_botoak_batuketa(self, obj):
        return obj.get_baliozko_botoak_sum()

    get_baliozko_botoak.short_description = "Baliozko botuak"
    get_baliozko_botoak_batuketa.short_description = "Baliozko botuen batuketa"

    def get_jarlekuak(self, obj):
        return obj.get_jarlekuak_sum()

    get_jarlekuak.short_description = "Jarlekuen batuketa"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "tokia":
            kwargs["queryset"] = Tokia.objects.filter(is_public=True)
        return super(HauteskundeaTokianAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def borratu_zinegotziak(self, request, obj):
        obj.hauteskundeeserlekuaktokian_set.all().delete()
        self.message_user(request, "Borratuta zinegotzi guztiak")

    borratu_zinegotziak.label = "Borratu zinegotziak"

    def sortu_zinegotziak(self, request, obj):
        kop = obj.jarlekuen_kopurua
        if not kop:
            self.message_user(
                request, "Ez dago jarlekurik... ezin zinegotzirik sortu"
            )
            return False
        for emaitza in obj.hauteskundeemaitzaktokian_set.all():
            for i in range(1, kop + 1):
                het = HauteskundeEserlekuakTokian()
                het.hauteskundeatokian = obj
                het.alderdia = emaitza.alderdia
                het.ordena_alderdian = i
                het.izena = "Izen Abizena"
                het.is_selected = False
                het.save()
        self.message_user(request, "Sortuta zinegotzi guztiak")

    sortu_zinegotziak.label = "Sortu zinegotziak hutsik"

    def publikatu_zinegotziak(self, request, obj):
        e = 0
        for emaitza in obj.hauteskundeemaitzaktokian_set.all().order_by(
            "-botoak",
            "-jarlekuak",
        ):
            for z in obj.hauteskundeeserlekuaktokian_set.filter(
                alderdia=emaitza.alderdia,
                ordena_alderdian__lte=emaitza.jarlekuak,
            ):
                z.is_selected = True
                z.ordena = e * 100 + z.ordena_alderdian
                z.save()
            e += 1
        self.message_user(request, "Publikatuta tokatzen diren zinegotziak")

    publikatu_zinegotziak.label = "Publikatu zinegotziak"

    change_actions = (
        "borratu_zinegotziak",
        "sortu_zinegotziak",
        "publikatu_zinegotziak",
    )


class HTMLWidget(forms.widgets.Input):
    input_type = None  # Subclasses must define this.

    def render(self, name, value, attrs=None, renderer=None):
        try:
            return mark_safe(u'<img src="%s" />' % self.attrs["img"])
        except:
            return u""


class PhotoAdminForm(forms.ModelForm):
    get_embed_img = forms.CharField(widget=HTMLWidget(), required=False)

    def __init__(self, *args, **kwargs):
        super(PhotoAdminForm, self).__init__(*args, **kwargs)
        try:
            self.fields["get_embed_img"].widget.attrs[
                "img"
            ] = self.instance.logoa.get_admin_thumbnail_url()
        except:
            pass

        self.fields["get_embed_img"].widget.attrs["readonly"] = True
        self.fields["get_embed_img"].label = "Embed code"


class AlderdiaResource(resources.ModelResource):
    class Meta:
        model = Alderdia
        fields = ("akronimoa", "izena", "slug")
        export_order = ("akronimoa", "izena", "slug")


class AlderdiaForm(forms.ModelForm):
    def clean(self):
        self.cleaned_data = super(AlderdiaForm, self).clean()
        import_kodea = self.cleaned_data.get("import_kodea", None)
        slug = self.cleaned_data.get("slug", None)

        if Alderdia.objects.filter(slug=slug).exists():
            cur_alderdia = Alderdia.objects.get(slug=slug)
        else:
            cur_alderdia = None

        if (
            cur_alderdia
            and import_kodea
            and Alderdia.objects.filter(
                Q(import_kodea=import_kodea) | Q(slug=import_kodea)
            )
            .exclude(id=cur_alderdia.id)
            .exists()
        ):
            self.add_error(
                "import_kodea",
                "Slug horrekin dagoeneko alderdi bat existitzen da! Errepasatu"
                " eta errepikatuak ezabatu edo batu!",
            )
        elif (
            not cur_alderdia and
            import_kodea
            and Alderdia.objects.filter(
                Q(import_kodea=import_kodea) | Q(slug=import_kodea)
            ).exists()
        ):
            self.add_error(
                "import_kodea",
                "Slug horrekin dagoeneko alderdi bat existitzen da! Errepasatu"
                " eta errepikatuak ezabatu edo batu!",
            )

        return self.cleaned_data


class AlderdiaAdmin(ImportExportModelAdmin):
    list_display = (
        "akronimoa",
        "izena",
        "kolorea",
        "get_hauteskunde_kopurua",
    )  # 'datuak')
    search_fields = [
        "akronimoa",
        "izena",
    ]
    raw_id_fields = ("logoa",)
    readonly_fields = ("added", "modified")
    search_fields = [
        "akronimoa",
        "izena",
    ]
    form = AlderdiaForm

    def get_queryset(self, request):
        qs = super(AlderdiaAdmin, self).get_queryset(request)
        return qs

    def datuak(self, obj):
        return obj.datuak

    datuak.short_description = "Datuak"
    datuak.admin_order_field = "datuak"

    actions = ["batu_alderdia"]
    resource_classes = [AlderdiaResource]

    def batu_alderdia(self, request, queryset):
        if "apply" in request.POST:
            # The user clicked submit on the intermediate form.
            # Perform our update action:
            # queryset.update(status='NEW_STATUS')
            # HEMEN EGIN GURE LANA
            alderdi_berria = Alderdia.objects.get(
                pk=request.POST.get("alderdi_berria")
            )
            for alderdia in queryset:
                HauteskundeEmaitzakTokian.objects.filter(
                    alderdia=alderdia
                ).update(alderdia=alderdi_berria)

            # Redirect to our admin view after our update has
            # completed with a nice little info message saying
            # our models have been updated:
            self.message_user(
                request, "Alderdia batuta: {} alderdi".format(queryset.count())
            )
            return HttpResponseRedirect(request.get_full_path())
        context = {}
        context["alderdiak"] = Alderdia.objects.all()
        context["alderdia"] = queryset
        return render(
            request,
            "tk_hauteskundeak/admin/batu_alderdia.html",
            context=context,
        )

    batu_alderdia.short_description = "Batu alderdi hau beste batera"


class HauteskundeaKargatuAdmin(DjangoObjectActions, admin.ModelAdmin):
    raw_id_fields = ("hauteskundea",)
    changelist_actions = ("deskargatu_eredua",)

    @transaction.atomic
    def deskargatu_eredua(self, request, obj):
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="hauteskundea_eredua.csv"'
        azken_hauteskundea = (
            Hauteskundea.objects.filter(is_public=True)
            .order_by("-eguna")
            .first()
        )
        emaitza = osatu_hauteskundeen_taula(
            [
                azken_hauteskundea,
            ],
            get_tokia({}),
        )
        alderdiak = [ald.slug for ald in emaitza["taula"]]
        herriak = Tokia.objects.filter(is_public=True, mota=1)
        writer = csv.writer(response)
        lehen_lerroa = [
            "lurralde_kodea",
            "herri_kodea",
            "errolda",
            "boto_emaileak",
            "baliogabeak",
            "zuriak",
        ]  #
        lehen_lerroa.extend(alderdiak)
        writer.writerow(lehen_lerroa)

        return response

    deskargatu_eredua.short_description = "Deskarkatu eredua"
    deskargatu_eredua.label = "Deskarkatu eredua"


class HauteskundeOharrakAdmin(admin.ModelAdmin):
    list_display = (
        "added",
        "alderdia",
        "oharrak",
    )
    raw_id_fields = ("alderdia", "hauteskundeak")


class HauteskundeKPAdmin(DjangoObjectActions, admin.ModelAdmin):
    """ """

    def delete_cache(self, request, queryset):
        HauteskundeaCache.objects.all().delete()
        HauteskundeaCacheCompare.objects.all().delete()
        HauteskundeaCacheMota.objects.all().delete()
        messages.add_message(
            request,
            messages.SUCCESS,
            "Borratu ditugu cache guztiak; taulak berriz sortuko dira eskatu"
            " ahala",
        )

    delete_cache.label = "Cacheak ezabatu, denak"
    delete_cache.short_description = (
        "Emaitza taula eta grafiko cache guztiak ezabatu"
    )

    list_display = (
        "added",
        "title",
        "is_public",
    )
    changelist_actions = [
        "delete_cache",
    ]


class HTMLWidget(forms.widgets.Input):
    """ """

    input_type = None  # Subclasses must define this.

    def render(self, name, value, attrs=None, renderer=None):
        if "html" in self.attrs:
            return mark_safe(self.attrs["html"])
        return u""


class HauteskundeaIframeAdminForm(forms.ModelForm):

    get_embed_code = forms.CharField(required=False, widget=forms.Textarea)
    get_html = forms.CharField(required=False, widget=HTMLWidget)

    def __init__(self, *args, **kwargs):
        super(HauteskundeaIframeAdminForm, self).__init__(*args, **kwargs)
        try:
            self.fields[
                "get_embed_code"
            ].initial = (
                '<iframe class="" width="{}" height="{}" frameBorder="0"'
                ' src="{}" allowfullscreen></iframe>'.format(
                    self.instance.width,
                    self.instance.height,
                    reverse(
                        "hauteskundeak_hauteskundea_iframe",
                        kwargs={"pk": self.instance.pk},
                    ),
                )
            )
            self.fields["get_html"].widget.attrs["html"] = self.fields[
                "get_embed_code"
            ].initial
        except:
            self.fields["get_embed_code"].initial = ""
            self.fields["get_html"].widget.attrs["html"] = ""

        self.fields["get_embed_code"].widget.attrs["readonly"] = True

    class Meta:
        model = HauteskundeaIframe
        fields = "__all__"


class HauteskundeaIframeAdmin(admin.ModelAdmin):
    form = HauteskundeaIframeAdminForm
    list_display = (
        "izena",
        "tokia",
        "mota",
        "hauteskundea1",
        "hauteskundea2",
        "added",
        "modified",
    )
    raw_id_fields = ("hauteskundea1", "hauteskundea2", "tokia")
    fieldsets = (
        (
            "Iframe datuak",
            {
                "fields": (
                    "izena",
                    ("hauteskundea1", "hauteskundea2"),
                    "tokia",
                    "mota",
                    ("width", "height"),
                )
            },
        ),
        (
            "Emaitza",
            {"fields": ("get_embed_code",)},
        ),
        (
            "Gehiago",
            {"fields": ("get_html",)},
        ),
    )


class HauteskundeEserlekuakTokianAdmin(admin.ModelAdmin):
    list_display = (
        "hauteskundeatokian",
        "alderdia",
        "ordena",
        "izena",
        "argazkia",
        "is_selected",
    )
    list_display_links = ("hauteskundeatokian", "alderdia", "ordena", "izena")
    list_filter = (
        "hauteskundeatokian__tokia",
        "hauteskundeatokian__hauteskundea",
        "alderdia",
    )
    raw_id_fields = (
        "hauteskundeatokian",
        "argazkia",
    )
    readonly_fields = (
        "added",
        "modified",
    )


class APIResourceConfigAdmin(admin.ModelAdmin):
    @admin.action(description="Aktibatu / Desaktibatu APIak")
    def toggle_active(modeladmin, request, queryset):
        for q in queryset:
            q.is_active = not q.is_active
            q.save()

    list_display = (
        "is_active",
        "hauteskundea",
        "data_set",
        "total",
        "protocol",
        "domain",
        "format",
        "charset",
        "path",
        "filename",
        "last_parsed",
    )
    list_display_links = (
        "hauteskundea",
        "data_set",
        "protocol",
        "domain",
    )
    list_filter = ("is_active", "data_set")
    actions = [toggle_active]


admin.site.register(Alderdia, AlderdiaAdmin)
admin.site.register(HauteskundeMota, HauteskundeMotaAdmin)
admin.site.register(Tokia, TokiaAdmin)
admin.site.register(Hauteskundea, HauteskundeaAdmin)
admin.site.register(HauteskundeaTokian, HauteskundeaTokianAdmin)
admin.site.register(HauteskundeOharrak, HauteskundeOharrakAdmin)
admin.site.register(HauteskundeKP, HauteskundeKPAdmin)
admin.site.register(HauteskundeaKargatu, HauteskundeaKargatuAdmin)
admin.site.register(HauteskundeaIframe, HauteskundeaIframeAdmin)
admin.site.register(
    HauteskundeEserlekuakTokian, HauteskundeEserlekuakTokianAdmin
)
admin.site.register(APIResourceConfig, APIResourceConfigAdmin)
