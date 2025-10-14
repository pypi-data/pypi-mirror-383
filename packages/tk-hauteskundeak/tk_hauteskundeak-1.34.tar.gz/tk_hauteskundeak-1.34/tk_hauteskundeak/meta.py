from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.html import strip_tags

SITE_TITLE = getattr(settings, "SITE_TITLE", "Tokikom.eus")
SITE_TAGLINE = getattr(settings, "SITE_TAGLINE", "Tokikom.eus tagline")
SITE_DESC = getattr(settings, "SITE_DESC", "Tokikom.eus, tokiko hedabideak")
SITE_KEYWORDS = getattr(
    settings, "SITE_KEYWORDS", "Tokikom.eus, tokiko hedabideak"
)
SITE_IMG = getattr(settings, "SITE_IMG", "/img/tk-logoa.png")
SITE_TW = getattr(settings, "SITE_TW", "@tokikom")


class Meta(object):
    def __init__(
        self,
        url,
        is_home=None,
        title=None,
        description=None,
        image_url=None,
        keywords=None,
        social=False,
        nofollow=False,
    ):
        if is_home:
            self.title = "%s - %s" % (SITE_TAGLINE, SITE_TITLE)
            self.description = SITE_DESC
            self.keywords = SITE_KEYWORDS
        else:
            self.title = (
                title
                and "%s - %s" % (title, SITE_TITLE)
                or "%s - %s" % (SITE_TAGLINE, SITE_TITLE)
            )
            self.description = description or None
            self.keywords = keywords

        self.image = (
            image_url and self.get_url(image_url) or self.get_url(SITE_IMG)
        )
        self.default_image = self.get_url(SITE_IMG)
        self.url = self.get_url(url)
        self._twitter = social
        self._facebook = social
        self.canonical = self.get_url(url)
        if nofollow:
            self.robots = "noindex, nofollow"
        else:
            self.robots = "index, follow"

    def get_keywords(self):
        tor = []
        tor.append(self.title)
        if self.description:
            tor.append(strip_tags(self.description))
        tor.append(getattr(self, "fulltext", u""))
        txt = u" ".join(tor)
        txt = txt.lower().replace("-", "")
        return u", ".join(set(txt.split()))

    def get_url(self, url):
        if not url.startswith("https"):
            return u"https://{}{}".format(
                Site.objects.get_current().domain, url
            )
        return url

    def set_more_props(self):
        if self._twitter:
            self.twitter_title = getattr(self, "twitter_title", self.title)
            self.twitter_description = getattr(
                self, "twitter_description", self.description
            )
            self.twitter_image = (
                getattr(self, "twitter_image", self.image)
                or self.default_image
            )
            self.twitter_creator = SITE_TW
            self.twitter_site = SITE_TW
            self.twitter_url = getattr(self, "twitter_url", self.url)
            self.twitter_card = getattr(self, "twitter_card", "summary")

        if self._facebook:
            self.fb_app__id = getattr(settings, "FACEBOOK_APP_ID", "")
            self.og_site__name = SITE_TITLE
            self.og_title = getattr(self, "og_title", self.title)
            self.og_description = getattr(
                self, "og_description", self.description
            )
            self.og_image = (
                getattr(self, "og_image", self.image) or self.default_image
            )
            self.og_url = getattr(self, "og_url", self.url)

        if not getattr(self, "keywords", ""):
            self.keywords = self.get_keywords()

        self.image = self.image or self.default_image

        return None

    def get_meta(self):
        self.set_more_props()
        h = self.__dict__
        tor = []
        keys = sorted(h.keys())
        for key in keys:
            if (
                not key.startswith("_")
                and not key.startswith("url")
                and h[key]
            ):
                nkey = key.replace("__", "+")
                nkey = nkey.replace("_", ":")
                nkey = nkey.replace("+", "_")
                tor.append({"key": nkey, "value": h[key]})
        return tor


def get_object_meta(obj):
    meta = Meta(obj.get_absolute_url(), title=obj.title, social=True)

    if obj.get_photo():
        meta.image = obj.get_photo().get_tokikom_700x700_url()

    try:
        meta.description = obj.get_summary()
    except AttributeError:
        pass
    return meta
