# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-12 10:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rio', '0007_auto_20160608_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]