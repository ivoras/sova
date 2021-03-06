# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-14 18:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sova', '0022_event_max_people'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participation',
            old_name='grade',
            new_name='poll_grade',
        ),
        migrations.RenameField(
            model_name='participation',
            old_name='note',
            new_name='poll_note',
        ),
        migrations.AddField(
            model_name='participation',
            name='poll_best',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='participation',
            name='poll_change',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='participation',
            name='poll_futureorg',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='participation',
            name='poll_worst',
            field=models.TextField(blank=True, null=True),
        ),
    ]
