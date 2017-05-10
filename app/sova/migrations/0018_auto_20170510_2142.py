# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-10 19:42
from __future__ import unicode_literals

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('sova', '0017_emailschedule_target'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='footer',
            field=tinymce.models.HTMLField(default=b'----'),
        ),
        migrations.AlterField(
            model_name='event',
            name='header',
            field=tinymce.models.HTMLField(default=b'Hi,'),
        ),
    ]
