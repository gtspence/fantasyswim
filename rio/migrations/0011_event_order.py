# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-28 13:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rio', '0010_auto_20160622_0811'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='order',
            field=models.IntegerField(blank=True, null=True, verbose_name=b'Event Number'),
        ),
    ]
