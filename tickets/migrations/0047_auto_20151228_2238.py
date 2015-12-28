# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-28 22:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0046_auto_20151228_2217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='externalpricing',
            name='show',
        ),
        migrations.DeleteModel(
            name='FringePricing',
        ),
        migrations.DeleteModel(
            name='InHousePricing',
        ),
        migrations.DeleteModel(
            name='SeasonTicketPricing',
        ),
        migrations.DeleteModel(
            name='StuFFEventPricing',
        ),
        migrations.DeleteModel(
            name='StuFFPricing',
        ),
        migrations.AlterField(
            model_name='show',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets.Category'),
        ),
        migrations.DeleteModel(
            name='ExternalPricing',
        ),
    ]
