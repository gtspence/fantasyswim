# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-19 11:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rio', '0019_auto_20160719_1054'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ['-date_time']},
        ),
    ]
