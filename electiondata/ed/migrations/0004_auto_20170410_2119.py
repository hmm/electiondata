# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-10 21:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ed', '0003_auto_20170410_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votingdatacomparison',
            name='eligible_finland_men',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='votingdatacomparison',
            name='eligible_finland_women',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='votingdatacomparison',
            name='eligible_men',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='votingdatacomparison',
            name='eligible_total',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='votingdatacomparison',
            name='eligible_women',
            field=models.IntegerField(null=True),
        ),
    ]
