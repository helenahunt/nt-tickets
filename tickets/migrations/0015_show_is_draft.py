# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-10-20 20:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0014_auto_20190627_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='is_draft',
            field=models.BooleanField(default=False, help_text=b'Tick to hide from all listings, etc. Useful for being able to add the new season as draft until launch date.'),
        ),
    ]
