# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import colorfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tk_hauteskundeak', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokia',
            name='datuak_ditu',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='alderdia',
            name='kolorea',
            field=colorfield.fields.ColorField(default=b'#FF0000', max_length=18),
        ),
    ]
