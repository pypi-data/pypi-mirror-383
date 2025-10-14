from photologue.models import Photo
from colorfield.fields import ColorField
import collections
import csv

from django.conf import settings
from django.template.defaultfilters import slugify
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

PROFILE_PHOTO_DEFAULT_SLUG = getattr(
    settings, "PROFILE_PHOTO_DEFAULT_SLUG", "no-profile-photo"
)

HAUTESKUNDE_MOTAK = (
    ("UD", "UD"),
    ("BN", "BN"),
    ("EUS", "EUS"),
    ("NAF", "NAF"),
    ("ESP", "ESP"),
    ("EUR", "EUR"),
)

MOTA_CHOICES = (
    (0, "Mahaia"),
    (1, "Herria"),
    (2, "Eskualdea"),
    (3, "Kuadrila"),
    (4, "Herrialdea"),
    (5, "Erkidegoa"),
    (6, "Estatua"),
)


class HauteskundeKP(models.Model):
    is_public = models.BooleanField(default=False, db_index=True)
    title = models.CharField(max_length=255)
    minutes = models.IntegerField(
        default=60,
        help_text=(
            "Cacheatzeko minutu kopurua. Jarri, gutxienez, 60; eta edizio"
            " bukatzen denean nahi adinakoa, handia, 30000 edo. Datuak aldatu"
            " nahi badira, jarri 0 eta nabigatzu apur bat aldatutako datuak"
            " refreskatu artean."
        ),
    )
    desc = models.TextField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if HauteskundeKP.objects.exists() and not self.pk:
            raise ValidationError("KontrolPanel bakarra egon behar du")
        return super(HauteskundeKP, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Hauteskunde Kontrol Panela"
        verbose_name_plural = "Hauteskunde Kontrol Panela"


class Tokia(models.Model):
    """ """

    slug = models.SlugField(db_index=True)
    izena = models.CharField(max_length=255)

    boundary_svg = models.TextField(blank=True, null=True)
    mota = models.IntegerField(choices=MOTA_CHOICES, default=1, db_index=True)

    herriak = models.ManyToManyField("self", blank=True)

    order_col = models.IntegerField(default=1)
    order_list = models.IntegerField(default=1)

    is_default = models.BooleanField(
        default=False,
        help_text="Herri edo eskualde nagusia. Bakarra aukeratu.",
        db_index=True,
    )
    is_public = models.BooleanField(default=False, db_index=True)
    # espainiako ministerioko excela kargatzeko
    lurralde_kodea = models.IntegerField(default=0)
    herri_kodea = models.IntegerField(default=0)

    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.izena

    def get_children(self):
        return self.herriak.filter(mota=1)

    def get_herriak_kopurua(self):
        return self.get_children().count()

    def get_gurasoak(self):
        return self.herriak.filter(is_public=True, mota__gt=self.mota).distinct()

    def has_datuak(self):
        return self.hauteskundea_tokian_set.exists()

    def get_hauteskundeak(self):
        return self.hauteskundeatokian_set.all()

    def get_hauteskundeak_kopurua(self):
        return self.hauteskundeatokian_set.all().count()

    def get_hauteskundea(self, hauteskundea):
        return self.hauteskundeatokian_set.get(hauteskundea=hauteskundea)

    class Meta:
        ordering = (
            "izena",
            "pk",
        )
        verbose_name = "Tokia"
        verbose_name_plural = "Tokiak"


class HauteskundeMota(models.Model):
    izena = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True)
    akronimoa = models.CharField(
        max_length=5, choices=HAUTESKUNDE_MOTAK, null=True, blank=True
    )
    is_public = models.BooleanField(default=True, db_index=True)
    irudia = models.ForeignKey(Photo, blank=True, null=True, on_delete=models.SET_NULL)
    order = models.IntegerField(default=0, help_text="Ordenatzeko erabiliko dugu")
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_hauteskundeak(self):
        return self.hauteskundea_set.filter(is_public=True).order_by("-eguna")

    def __str__(self):
        return self.izena

    class Meta:
        ordering = (
            "order",
            "izena",
            "pk",
        )
        verbose_name = "Hauteskunde mota"
        verbose_name_plural = "Hauteskunde motak"


class Hauteskundea(models.Model):
    """ """

    slug = models.SlugField(db_index=True)
    izen_motza = models.CharField(max_length=10, null=True, blank=True)
    izena = models.CharField(max_length=255, null=True, blank=True)

    eguna = models.DateField()
    mota = models.ForeignKey(HauteskundeMota, on_delete=models.CASCADE)

    irudia = models.ForeignKey(Photo, blank=True, null=True, on_delete=models.SET_NULL)

    is_public = models.BooleanField(default=False, db_index=True)
    is_closed = models.BooleanField(
        default=False,
        verbose_name="Itxita",
        help_text=(
            "Herrietako portadetako estatistikak ezkutatzen ditu. Hauteskundea"
            " amaitu ostean markatu."
        ),
    )

    auto_import = models.BooleanField(
        default=False,
        help_text="Aukeratu hauteskundea automatikoki inportatu nahi bada",
    )

    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.izena

    def has_eserlekuak(self):
        return True

    def get_urtea(self):
        if self.eguna:
            return self.eguna.year
        return 1900

    """
    def get_toki_nagusiak(self):
        return self.hauteskundea_tokian_set.filter(tokia__aita__isnull=True)
    """

    class Meta:
        ordering = (
            "-eguna",
            "pk",
        )
        verbose_name = "Hauteskundea"
        verbose_name_plural = "Hauteskundeak"


class HauteskundeaTokian(models.Model):
    hauteskundea = models.ForeignKey(
        Hauteskundea, db_index=True, on_delete=models.CASCADE
    )
    tokia = models.ForeignKey(Tokia, db_index=True, on_delete=models.CASCADE)

    jarlekuen_kopurua = models.IntegerField(default=0)
    errolda = models.IntegerField(default=0)

    boto_emaileak = models.IntegerField(default=0)
    baliogabeak = models.IntegerField(default=0)
    zuriak = models.IntegerField(default=0)
    alderdien_botoak = models.IntegerField(default=0, editable=False)

    eskrutinioa = models.DecimalField(default=0, max_digits=5, decimal_places=2)

    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_aurrekoan_jarlekuak(self):
        prev_hauteskundea = (
            Hauteskundea.objects.filter(
                mota=self.hauteskundea.mota, eguna__lt=self.hauteskundea.eguna
            )
            .exclude(id=self.hauteskundea.id)
            .order_by("eguna")
            .last()
        )
        prev_tokian = HauteskundeaTokian.objects.get(
            hauteskundea=prev_hauteskundea, tokia__slug=self.tokia.slug
        )
        aurrekoan_eserlekuak_qs = HauteskundeEserlekuakTokian.objects.filter(
            hauteskundeatokian=prev_tokian
        ).order_by("ordena")
        return aurrekoan_eserlekuak_qs.count() or 0

    """
    def gehitu_emaitzen_taulara(self, emaitzak = collections.OrderedDict(), n=1):
        emaitzak_graph1 = []
        emaitzak_graph1_ehunekoak = "["
        for emaitza in self.get_emaitzak():
            if not emaitza.alderdia in emaitzak.keys():
                emaitzak[emaitza.alderdia] = {}
            emaitzak[emaitza.alderdia]['botoak%d'%n]=emaitza.botoak
            emaitzak[emaitza.alderdia]['botoak%d_ehunekoa'%n]=(emaitza.botoak*100)/self.boto_emaileak
            emaitzak[emaitza.alderdia]['jarlekuak%d'%n]=emaitza.jarlekuak
            emaitzak_graph1.append(int(emaitza.botoak))
            emaitzak_graph1_ehunekoak += "['%s', %d], "%(emaitza.alderdia.izena, emaitzak[emaitza.alderdia]['botoak%d_ehunekoa'%n])
        emaitzak_graph1_ehunekoak+="]"
        return emaitzak, emaitzak_graph1, emaitzak_graph1_ehunekoak


    def get_boto_emaileak_ehunekotan(self):
        return (float(self.boto_emaileak)/float(self.errolda))*100

    def get_emaitzak(self):
        # 0 bozka daukatenak kenduta
        return self.hauteskundeemaitzaktokian_set.filter(botoak__gt=0).order_by('-botoak')

    def get_emaitzak_denak(self):
        return self.hauteskundeemaitzaktokian_set.all().order_by('-botoak')

    def get_baliozko_botoak(self):
        return self.boto_emaileak - self.baliogabeak

    def get_abstentzioa_ehunekotan(self):
        return (float(self.get_abstentzioa()) / float(self.errolda))*100

    def get_abstentzioa(self):
        return self.errolda - self.boto_emaileak

    def get_hautagai_zerrenden_botoak(self):
        return self.boto_emaileak - self.baliogabeak -self.zuriak

    def get_jarlekuak_sum(self):
        return self.hauteskundeemaitzaktokian_set.all().aggregate(Sum('jarlekuak'))['jarlekuak__sum']

    """

    def get_zuriak_ehunekotan(self):
        if self.boto_emaileak:
            return (float(self.zuriak) / float(self.boto_emaileak)) * 100

    def get_baliogabeak_ehunekotan(self):
        if self.boto_emaileak:
            return (float(self.baliogabeak) / float(self.boto_emaileak)) * 100

    def get_jarlekuak_sum(self):
        return self.hauteskundeemaitzaktokian_set.all().aggregate(Sum("jarlekuak"))[
            "jarlekuak__sum"
        ]

    def get_baliozko_botoak_sum(self):
        return self.hauteskundeemaitzaktokian_set.all().aggregate(Sum("botoak"))[
            "botoak__sum"
        ]

    def itxuraz_ondo(self):
        return self.get_baliozko_botoak_sum() == self.alderdien_botoak

    itxuraz_ondo.boolean = True

    def save(self, *args, **kwargs):
        if (
            type(self.boto_emaileak) is int
            and type(self.boto_emaileak) is int
            and type(self.zuriak) is int
        ):
            self.alderdien_botoak = self.boto_emaileak - self.baliogabeak - self.zuriak
        for emai in HauteskundeEmaitzakTokian.objects.filter(hauteskundeatokian=self):
            emai.save()
        return super(HauteskundeaTokian, self).save(*args, **kwargs)

    def __str__(self):
        return "{} ({})".format(self.hauteskundea.izena, self.tokia.izena)

    class Meta:
        ordering = (
            "hauteskundea",
            "tokia",
        )
        verbose_name = "Hauteskundea Tokian"
        verbose_name_plural = "Hauteskundeak Tokian"


class Alderdia(models.Model):
    slug = models.SlugField(max_length=300, db_index=True, unique=True)
    akronimoa = models.CharField(max_length=30, default="-")
    izena = models.CharField(max_length=255)
    import_kodea = models.CharField(max_length=255, null=True, blank=True)
    kolorea = ColorField(default="#000000")
    logoa = models.ForeignKey(Photo, blank=True, null=True, on_delete=models.SET_NULL)

    show_in_table = models.BooleanField(
        default=True, help_text="Konparaketa tabletan erakutsiko da"
    )
    show_in_graphs = models.BooleanField(
        default=True, help_text="Grafikoetan erakutsiko da. Kolorea gehitu!"
    )
    show_in_page = models.BooleanField(
        default=True, help_text="Orri propioa du alderdi honek"
    )

    slug_list = models.TextField(null=True, blank=True)

    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.akronimoa

    def get_hauteskunde_kopurua(self):
        return self.hauteskundeemaitzaktokian_set.filter(
            hauteskundeatokian__tokia__is_public=True
        ).count()

    def show_izena(self):
        return self.izena and self.akronimoa != self.izena

    class Meta:
        ordering = (
            "izena",
            "pk",
        )
        verbose_name = "Alderdia"
        verbose_name_plural = "Alderdiak"


class HauteskundeEmaitzakTokian(models.Model):
    hauteskundeatokian = models.ForeignKey(
        HauteskundeaTokian, db_index=True, on_delete=models.CASCADE
    )
    alderdia = models.ForeignKey(Alderdia, db_index=True, on_delete=models.CASCADE)

    botoak = models.IntegerField(default=0)
    jarlekuak = models.IntegerField(default=0)
    ehunekoa = models.FloatField(default=0)

    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_jarlekuak_aurrekoan(self):
        hauteskundea = self.hauteskundeatokian.hauteskundea
        tokia = self.hauteskundeatokian.tokia
        prev_hauteskundea = (
            Hauteskundea.objects.filter(
                mota=hauteskundea.mota, eguna__lt=hauteskundea.eguna
            )
            .exclude(id=hauteskundea.id)
            .order_by("eguna")
            .last()
        )
        prev_tokian = HauteskundeaTokian.objects.get(
            hauteskundea=prev_hauteskundea, tokia__slug=tokia.slug
        )
        aurrekoan_emaitzak = HauteskundeEmaitzakTokian.objects.filter(
            hauteskundeatokian=prev_tokian, alderdia=self.alderdia
        )
        return aurrekoan_emaitzak and aurrekoan_emaitzak[0].jarlekuak or 0

    def save(self, *args, **kwargs):
        if self.hauteskundeatokian.alderdien_botoak > 0:
            self.ehunekoa = (
                int(self.botoak)
                * 100.0
                / (
                    self.hauteskundeatokian.alderdien_botoak
                    + self.hauteskundeatokian.zuriak
                )
            )
        return super(HauteskundeEmaitzakTokian, self).save(*args, **kwargs)

    class Meta:
        ordering = (
            "hauteskundeatokian",
            "-botoak",
            "alderdia",
        )
        verbose_name = "Emaitza"
        verbose_name_plural = "Emaitzak"


class HauteskundeEserlekuakTokian(models.Model):
    hauteskundeatokian = models.ForeignKey(
        HauteskundeaTokian, db_index=True, on_delete=models.CASCADE
    )
    alderdia = models.ForeignKey(Alderdia, db_index=True, on_delete=models.CASCADE)
    ordena_alderdian = models.IntegerField(
        default=0, help_text="Zerrendan zer ordenatan doan"
    )
    ordena = models.IntegerField(
        default=0, help_text="Emaitza orrian honen arabera erakutsiko dira"
    )
    izena = models.CharField(max_length=255)
    desc = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nahi bada ofizioa, urtea... info pixkat",
    )
    argazkia = models.ForeignKey(
        Photo, blank=True, null=True, on_delete=models.SET_NULL
    )
    is_selected = models.BooleanField(default=False, db_index=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_photo(self):
        if self.argazkia:
            return self.argazkia
        else:
            try:
                return Photo.objects.get(slug=PROFILE_PHOTO_DEFAULT_SLUG)
            except:
                return None

    def __str__(self):
        return self.izena

    class Meta:
        ordering = ("hauteskundeatokian", "alderdia", "ordena_alderdian")
        verbose_name = "Zinegotzia"
        verbose_name_plural = "Zinegotziak"


class HauteskundeOharrak(models.Model):
    alderdia = models.ForeignKey(
        Alderdia, blank=True, null=True, on_delete=models.SET_NULL
    )
    hauteskundeak = models.ManyToManyField(Hauteskundea, blank=True)
    oharrak = models.TextField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hauteskunde Oharra"
        verbose_name_plural = "Hauteskunde Oharrak"


from django.db.models.signals import post_save


class HauteskundeaKargatu(models.Model):
    hauteskundea = models.ForeignKey(Hauteskundea, on_delete=models.CASCADE)
    fitxategia = models.FileField()
    oharrak = models.TextField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hauteskundea.izena

    class Meta:
        verbose_name = "Hauteskundea karkatu"
        verbose_name_plural = "Hauteskundea kargatu"


def Hauteskundea_postsave(sender, instance, created, **kwargs):
    fitxategia = instance.fitxategia
    hautes = instance.hauteskundea
    decoded_file = fitxategia.read().decode("utf-8").splitlines()
    delimiter = ","
    rd = csv.DictReader(decoded_file, delimiter=delimiter)

    for row1 in rd:
        # tokia = Tokia.objects.get(slug=row1.pop('herria'))
        lurralde_kodea = row1.pop("lurralde_kodea")
        herri_kodea = row1.pop("herri_kodea")

        if Tokia.objects.filter(
            lurralde_kodea=lurralde_kodea, herri_kodea=herri_kodea
        ).exists():
            tokia = Tokia.objects.get(
                lurralde_kodea=lurralde_kodea, herri_kodea=herri_kodea
            )
            HauteskundeaTokian.objects.filter(hauteskundea=hautes, tokia=tokia).delete()

            hautesk_tok = HauteskundeaTokian()
            hautesk_tok.hauteskundea = hautes
            hautesk_tok.tokia = tokia
            hautesk_tok.errolda = row1.pop("errolda").replace(".", "") or 0
            hautesk_tok.boto_emaileak = row1.pop("boto_emaileak").replace(".", "") or 0
            hautesk_tok.baliogabeak = row1.pop("baliogabeak").replace(".", "") or 0
            hautesk_tok.zuriak = row1.pop("zuriak").replace(".", "") or 0
            hautesk_tok.save()
            for alderdi, boto in row1.items():

                if boto and int(boto.replace(".", "")) > 0:
                    emaitza = HauteskundeEmaitzakTokian()
                    if Alderdia.objects.filter(slug=alderdi):
                        alderdia = Alderdia.objects.filter(slug=alderdi)[0]
                    else:
                        alderdia, created = Alderdia.objects.get_or_create(
                            izena=alderdi,
                            slug=slugify(alderdi),
                            akronimoa=alderdi,
                        )
                    emaitza.hauteskundeatokian = hautesk_tok
                    emaitza.alderdia = alderdia

                    emaitza.botoak = int(boto.replace(".", "")) or 0
                    emaitza.save()

            hautesk_tok.save()


post_save.connect(Hauteskundea_postsave, sender=HauteskundeaKargatu)

from django.template.loader import render_to_string
from django.urls import reverse

IFRAME_CHOICES = (
    (0, "Grafiko barra"),
    (1, "Emaitzen tabla"),
    (2, "Tarta"),
    (3, "Mapa"),
    (4, "Zinegotziak"),
)


class HauteskundeaIframe(models.Model):
    """ """

    izena = models.CharField(max_length=255, help_text="Sartu gogoratzeko moduko izena")

    hauteskundea1 = models.ForeignKey(
        Hauteskundea,
        related_name="hauteskundea_iframe_1",
        on_delete=models.CASCADE,
    )
    hauteskundea2 = models.ForeignKey(
        Hauteskundea,
        related_name="hauteskundea_iframe_2",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    tokia = models.ForeignKey(Tokia, on_delete=models.CASCADE)
    mota = models.IntegerField(choices=IFRAME_CHOICES, default=0)

    width = models.CharField(
        max_length=6,
        default="100%",
        help_text=(
            'Iframearen zabalera. Defektuz, sartu "100%"; zabalera finkoa nahi'
            ' bada, sartu pixelak: "400px", "600px" '
        ),
    )
    height = models.CharField(
        max_length=6,
        default="500px",
        help_text=('Iframearen altuera. Sartu pixel kopurua: "400px", "600px"... '),
    )

    html = models.TextField(
        blank=True,
        null=True,
        help_text="HTMLa",
    )

    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.izena

    class Meta:
        ordering = ("-pk",)
        verbose_name = "Hauteskunde iframea"
        verbose_name_plural = "Hauteskunde iframeak"


@receiver(post_save, sender=HauteskundeaIframe, dispatch_uid="update_iframe")
def update_iframe(sender, instance, created, **kwargs):
    if created:
        from .views import update_iframe
        from django.http.request import HttpRequest

        request = HttpRequest
        request.method = "GET"
        request.GET = {}
        request.META = {}
        iframe = update_iframe(request, instance)
        iframe.save()


class HauteskundeaCache(models.Model):
    """ """

    tokia = models.ForeignKey(Tokia, on_delete=models.CASCADE)
    hauteskundea = models.ForeignKey(Hauteskundea, on_delete=models.CASCADE)

    html = models.TextField(blank=True, null=True)

    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("pk",)
        verbose_name = "Cache: hauteskundea"
        verbose_name_plural = "Cache: hauteskundeak"


class HauteskundeaCacheCompare(models.Model):
    """ """

    tokia = models.ForeignKey(Tokia, on_delete=models.CASCADE)
    hauteskundea1 = models.ForeignKey(
        Hauteskundea,
        related_name="hauteskundea_cache_1",
        on_delete=models.CASCADE,
    )
    hauteskundea2 = models.ForeignKey(
        Hauteskundea,
        related_name="hauteskundea_cache_2",
        on_delete=models.CASCADE,
    )

    html = models.TextField(blank=True, null=True)

    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("pk",)
        verbose_name = "Cache: hauteskunde alderaketa"
        verbose_name_plural = "Cache: hauteskunde alderaketak"


class HauteskundeaCacheMota(models.Model):
    """ """

    tokia = models.ForeignKey(Tokia, on_delete=models.CASCADE)
    mota = models.ForeignKey(HauteskundeMota, on_delete=models.CASCADE)

    html = models.TextField(blank=True, null=True)

    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("pk",)
        verbose_name = "Cache: hauteskunde mota"
        verbose_name_plural = "Cache: hauteskunde motak"


PROTOCOL_CHOICES = (
    ("HTTPS", "HTTPS"),
    ("FTP", "FTP"),
)

FORMAT_CHOICES = (
    ("TXT", "TXT"),
    ("XML", "XML"),
    ("CSV", "CSV"),
)

CHARSET_CHOICES = (
    ("latin-1", "ISO-8859-1"),
    ("utf-8", "UTF-8"),
)

ALDUNDIA_CHOICES = (
    ("ara", "Araba"),
    ("biz", "Bizkaia"),
    ("gip", "Gipuzkoa"),
    ("naf", "Nafarroa"),
    ("uda", "Ministerioa (Udalak)"),
    ("kon", "Ministerioa (Kongresua)"),
    ("eae", "Eusko Jaurlaritza"),
    ("eur", "Ministerioa (Europa)"),
)


class APIResourceConfig(models.Model):
    protocol = models.CharField(
        max_length=6, choices=PROTOCOL_CHOICES, verbose_name="Protokoloa"
    )
    protocol_charset = models.CharField(
        max_length=8,
        choices=CHARSET_CHOICES,
        default="utf-8",
        verbose_name="Protokolo kodetzea",
        help_text=(
            "FTP protokoloak karpeta sisteman nabigatzeko darabilen kodetzea."
            " Defektuz, UTF-8. HTTPS konfigurazioan defektuzkoa utzi."
        ),
    )
    domain = models.CharField(max_length=100, verbose_name="Domainua")
    username = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Erabiltzailea"
    )
    passwd = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Pasahitza"
    )
    format = models.CharField(
        max_length=5, choices=FORMAT_CHOICES, verbose_name="Formatua"
    )
    charset = models.CharField(
        max_length=8, choices=CHARSET_CHOICES, verbose_name="Kodetzea"
    )
    token_call = models.CharField(
        max_length=255,
        verbose_name="Token deia",
        null=True,
        blank=True,
        help_text=(
            "API deiak Token bat behar badu, adierazi tokena lortzeko"
            " helbide erlatiboa."
        ),
    )
    path = models.CharField(max_length=255, verbose_name="Direktorioa/Helbidea")
    filename = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Fitxategia/Erreferentzia",
        help_text=(
            "FTP edo HTTPS eskaeran fitxategi bat arkitu behar bada, adierazi" " hemen."
        ),
    )
    total = models.BooleanField(
        default=False,
        verbose_name="Datu totalak ditu",
        help_text=(
            "Fitxategi honek herrietatik aparteko hainbat eremuren datu"
            " totalak ditu. Araba, Nafarroa adibidez."
        ),
    )

    data_set = models.CharField(
        max_length=3,
        null=True,
        choices=ALDUNDIA_CHOICES,
        verbose_name="Datuen iturria",
        help_text="Adierazi datuen iturria",
    )

    hauteskundea = models.ForeignKey(
        Hauteskundea,
        null=True,
        related_name="hauteskundea",
        on_delete=models.SET_NULL,
        verbose_name="Hauteskundea",
    )

    is_active = models.BooleanField(default=False, verbose_name="Aktibatuta")
    last_parsed = models.DateTimeField(null=True)

    def __str__(self):
        return "%s" % self.domain

    class Meta:
        verbose_name = "API konexioa"
        verbose_name_plural = "API konexioak"
