# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-06 06:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0010_auto_20180604_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='quickbookusertoken',
            name='login_update_flag',
            field=models.BooleanField(default=False, max_length=100),
        ),
    ]
