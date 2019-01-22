# Generated by Django 2.1.5 on 2019-01-22 10:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='block',
            name='place',
        ),
        migrations.AddField(
            model_name='block',
            name='time_end',
            field=models.DateTimeField(default=datetime.date(2000, 1, 1)),
        ),
        migrations.AddField(
            model_name='block',
            name='time_start',
            field=models.DateTimeField(default=datetime.date(2000, 1, 1)),
        ),
        migrations.AlterField(
            model_name='block',
            name='activity',
            field=models.CharField(default='', max_length=256),
        ),
        migrations.DeleteModel(
            name='Activity',
        ),
        migrations.DeleteModel(
            name='Place',
        ),
    ]
