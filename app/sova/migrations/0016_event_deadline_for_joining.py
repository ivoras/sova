# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-21 17:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sova', '0015_auto_20170221_1642'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='deadline_for_joining',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
