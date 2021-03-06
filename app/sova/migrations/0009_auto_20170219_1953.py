# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-19 18:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sova', '0008_auto_20170218_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='participation',
            name='requirements_done',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='person',
            name='phone',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='phone_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
