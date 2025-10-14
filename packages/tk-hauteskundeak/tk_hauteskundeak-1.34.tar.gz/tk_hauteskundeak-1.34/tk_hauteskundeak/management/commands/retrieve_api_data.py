from django.core.management.base import BaseCommand
import io
import os
import requests
from requests.auth import HTTPBasicAuth
from ftplib import FTP
from tk_hauteskundeak.management.commands.create_static_candidates import (
    create_candidates_file,
)
from tk_hauteskundeak.models import Hauteskundea, APIResourceConfig
from tk_hauteskundeak.api.utils.bn_bizkaia import import_bizkaia
from tk_hauteskundeak.api.utils.bn_araba import import_araba
from tk_hauteskundeak.api.utils.bn_gipuzkoa import import_gipuzkoa
from tk_hauteskundeak.api.utils.bn_nafarroa import import_nafarroa
from tk_hauteskundeak.api.utils.ministerioa_udalak import (
    import_ministerio_udalak,
)
from tk_hauteskundeak.api.utils.ministerioa_kongresua import (
    import_ministerio_kongresua,
)
from tk_hauteskundeak.api.utils.eusko_jaurlaritza import (
    import_jaurlaritza,
)
from tk_hauteskundeak.api.utils.europa import (
    import_europa,
)
from django.utils import timezone


def data_from_data_source(config):
    try:
        if config.protocol == "FTP":
            ftp = FTP(config.domain, encoding=config.protocol_charset)
            ftp.login(config.username, config.passwd)
            print(
                "%s Connected to %s to retrieve %s..."
                % (
                    timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    config.domain,
                    config.filename,
                )
            )
            ftp.cwd(config.path)
            f = io.BytesIO()
            ftp.retrbinary("RETR %s" % config.filename, f.write)
            return f
        else:
            if config.token_call:
                auth = HTTPBasicAuth(config.username, config.passwd)
                response = requests.get(
                    os.path.join(config.domain, config.token_call),
                    auth=auth,
                    headers={"User-Agent": "Postman"},
                )
                token = response.content.decode("utf-8")
                print(
                    "%s Connected to %s to get token"
                    % (
                        timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                        config.domain,
                    )
                )
                if config.total:
                    response = requests.get(
                        os.path.join(config.domain, config.path, token),
                        auth=auth,
                        headers={"User-Agent": "Postman"},
                    )
                else:
                    response = requests.get(
                        os.path.join(config.domain, config.path, token),
                        auth=auth,
                        headers={"User-Agent": "Postman"},
                    )
                print(
                    "%s Connected to %s%s with token %s..."
                    % (
                        timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                        config.domain,
                        config.path,
                        token,
                    )
                )
            else:
                response = requests.get(
                    os.path.join(config.domain, config.path, config.filename)
                )
                print(
                    "%s Connected to %s to retrieve %s..."
                    % (
                        timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                        config.domain,
                        config.filename,
                    )
                )
            if response.ok:
                return io.BytesIO(response.content)
            else:
                print(response.status_code, response.text)
                return None
    except:
        print("Connection ERROR!")
        return None


class Command(BaseCommand):
    args = "Hauteskunde datuen erauzketa"
    help = "Hauteskunde datuen erauzketa zuzenean egiteko"

    def handle(self, *args, **options):
        create_candidates_file()
        hauteskundeak = Hauteskundea.objects.filter(auto_import=True)

        for hauteskundea in hauteskundeak:
            datu_iturriak = APIResourceConfig.objects.filter(
                hauteskundea=hauteskundea,
                is_active=True,
            )
            for config in datu_iturriak:
                data = data_from_data_source(config)
                if not data:
                    continue
                decoded = data.getvalue().decode(config.charset)
                if config.data_set == "biz":
                    import_bizkaia(decoded, hauteskundea)
                elif config.data_set == "gip":
                    import_gipuzkoa(decoded, hauteskundea)
                elif config.data_set == "ara":
                    import_araba(decoded, hauteskundea, config.total)
                elif config.data_set == "naf":
                    import_nafarroa(decoded, hauteskundea, config.total)
                elif config.data_set == "uda":
                    import_ministerio_udalak(decoded, hauteskundea, config.total)
                elif config.data_set == "kon":
                    import_ministerio_kongresua(decoded, hauteskundea, config.total)
                elif config.data_set == "eae":
                    import_jaurlaritza(decoded, hauteskundea)
                elif config.data_set == "eur":
                    import_europa(decoded, hauteskundea, config.total)
                config.last_parsed = timezone.now()
                config.save()
        return "Data retrieved!"
