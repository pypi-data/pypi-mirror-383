from django.core.management.base import BaseCommand
from tk_hauteskundeak.models import Alderdia


class Command(BaseCommand):
    args = "Hauteskunderik gabeko alderdiak ezabatu"
    help = "Hauteskunderik gabeko alderdiak ezabatu"

    def handle(self, *args, **options):
        alderdiak = Alderdia.objects.all()

        for alderdia in alderdiak:
            if alderdia.get_hauteskunde_kopurua() == 0:
                alderdia.delete()
