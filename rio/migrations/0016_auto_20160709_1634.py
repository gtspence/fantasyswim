# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-09 16:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rio', '0015_auto_20160709_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name=b'League Name'),
        ),
    ]