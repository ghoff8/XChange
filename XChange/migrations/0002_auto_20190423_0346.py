# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-04-23 03:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('XChange', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='shares',
            field=models.FloatField(max_length=250),
        ),
    ]
