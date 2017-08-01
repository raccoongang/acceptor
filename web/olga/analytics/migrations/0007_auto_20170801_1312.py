# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-01 13:12
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0006_auto_20170801_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installationstatistics',
            name='students_per_country',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
