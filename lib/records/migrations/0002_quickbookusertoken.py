# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-01 05:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuickbookUserToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refreshExpiry', models.IntegerField()),
                ('accessToken', models.CharField(max_length=728)),
                ('tokenType', models.CharField(max_length=512)),
                ('refreshToken', models.CharField(max_length=512)),
                ('accessTokenExpiry', models.IntegerField()),
                ('idToken', models.TextField(max_length=512)),
                ('user_integration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='records.YellowUserToken')),
            ],
        ),
    ]
