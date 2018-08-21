# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-21 13:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conditions', '0014_meta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='condition',
            name='source',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='The Attribute of the value this condition.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='domain.AttributeEntity', verbose_name='Source'),
        ),
    ]
