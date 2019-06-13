# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-06-13 19:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0009_show_allow_reservations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='show',
            name='slug',
            field=models.SlugField(blank=True, help_text=b'Used in the URL of the detail page, leave blank to auto-generate.', max_length=255),
        ),
    ]
