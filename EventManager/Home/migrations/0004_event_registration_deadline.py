# Generated by Django 3.1.4 on 2021-01-19 10:06

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0003_auto_20210111_1741'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='registration_deadline',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 19, 10, 6, 13, 702733, tzinfo=utc)),
        ),
    ]