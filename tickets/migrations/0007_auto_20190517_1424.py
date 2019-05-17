# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-05-17 14:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0006_auto_20190516_2104'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='interval_number',
            field=models.IntegerField(default=0, help_text=b'Number of intervals the show has, typically 0 or 1.'),
        ),
        migrations.AddField(
            model_name='show',
            name='runtime',
            field=models.IntegerField(blank=True, help_text=b'Show running time in minutes, without interval time.', null=True),
        ),
    ]
