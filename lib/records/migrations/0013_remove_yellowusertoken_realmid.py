# Generated by Django 2.0.6 on 2018-06-11 09:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0012_yellowusertoken_realmid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='yellowusertoken',
            name='realmId',
        ),
    ]