# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-18 17:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sova', '0007_auto_20170212_2132'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='participation',
            name='participated',
            field=models.BooleanField(default=False),
        ),
    ]
