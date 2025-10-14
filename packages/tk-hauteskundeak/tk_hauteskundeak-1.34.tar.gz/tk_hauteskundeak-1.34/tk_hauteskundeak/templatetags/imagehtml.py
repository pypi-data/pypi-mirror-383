import re
from django import template
from django.conf import settings

from photologue.models import Photo

register = template.Library()


@register.filter
def getphoto(pk):
    if pk:
        try:
            return Photo.objects.get(pk=pk)
        except:
            pass
    return None
