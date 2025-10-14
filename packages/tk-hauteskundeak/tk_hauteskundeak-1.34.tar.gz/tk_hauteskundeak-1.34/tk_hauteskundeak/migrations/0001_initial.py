# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Alderdia",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("izena", models.CharField(max_length=255)),
                ("slug", models.SlugField()),
                ("izen_orokorra", models.CharField(max_length=255)),
                ("akronimoa", models.CharField(max_length=30)),
                ("kolorea", models.CharField(max_length=8)),
                ("added", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "logoa",
                    models.ForeignKey(to="photologue.Photo", on_delete=models.CASCADE),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Hauteskundea",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("izena", models.CharField(max_length=255, null=True, blank=True)),
                ("slug", models.SlugField()),
                ("eguna", models.DateField()),
                ("added", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="HauteskundeaTokian",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("jarlekuen_kopurua", models.IntegerField(default=0)),
                ("errolda", models.IntegerField(default=0)),
                ("boto_emaileak", models.IntegerField(default=0)),
                ("baliogabeak", models.IntegerField(default=0)),
                ("zuriak", models.IntegerField(default=0)),
                ("added", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "hauteskundea",
                    models.ForeignKey(
                        to="tk_hauteskundeak.Hauteskundea", on_delete=models.CASCADE
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HauteskundeEmaitzakTokian",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("botoak", models.IntegerField(default=0)),
                ("jarlekuak", models.IntegerField(default=0)),
                ("added", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "alderdia",
                    models.ForeignKey(
                        to="tk_hauteskundeak.Alderdia", on_delete=models.CASCADE
                    ),
                ),
                (
                    "hauteskundea",
                    models.ForeignKey(
                        to="tk_hauteskundeak.HauteskundeaTokian",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HauteskundeMota",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("izena", models.CharField(max_length=255)),
                ("slug", models.SlugField()),
                ("added", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Tokia",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("izena", models.CharField(max_length=255)),
                ("slug", models.SlugField()),
                ("added", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "aita",
                    models.ForeignKey(
                        blank=True,
                        to="tk_hauteskundeak.Tokia",
                        null=True,
                        on_delete=models.SET_NULL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="hauteskundeatokian",
            name="tokia",
            field=models.ForeignKey(
                to="tk_hauteskundeak.Tokia", on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="hauteskundea",
            name="mota",
            field=models.ForeignKey(
                to="tk_hauteskundeak.HauteskundeMota", on_delete=models.CASCADE
            ),
        ),
    ]
