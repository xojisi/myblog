# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-24 16:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='tag',
            field=models.ManyToManyField(related_name='tag', to='blog.Tag', verbose_name='\u6807\u7b7e'),
        ),
    ]
