import os
from django.core.management.base import BaseCommand
from xml.dom import minidom
from tk_hauteskundeak.models import Tokia

abs_path = "/var/csmant/django/tokikom/erran2/buildout"

class Command(BaseCommand):
    help = 'Herrien SVG irudiak erauzi'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str)

    def handle(self, *args, **options):
        doc = minidom.parse(os.path.join(abs_path, "map/" + options['file_name']))
        paths = doc.getElementsByTagName('path')
        for path in paths:
            name = path.getAttribute('name')
            qs = Tokia.objects.filter(is_public=True, mota=1, izena=name).filter()
            if qs.exists(): 
                t = qs[0]
                t.boundary_svg = path.getAttribute('d')
                t.save()
            else:
                print(name)