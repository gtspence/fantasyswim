# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-15 10:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rio', '0006_auto_20160615_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='WR_event2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='WR_event2', to='rio.Event', verbose_name='WR event 2'),
        ),
        migrations.AlterField(
            model_name='team',
            name='WR_event3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='WR_event3', to='rio.Event', verbose_name='WR event 3'),
        ),
    ]
