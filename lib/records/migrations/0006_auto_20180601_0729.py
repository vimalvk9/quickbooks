# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-01 07:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0005_quickbookusertoken_realmid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quickbookusertoken',
            name='realmID',
            field=models.CharField(default=' ', max_length=200),
        ),
    ]
