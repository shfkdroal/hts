# Generated by Django 2.0.4 on 2018-05-03 03:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hts_backend', '0028_auto_20180503_0349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profit_stat',
            name='daybefore',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 3, 3, 51, 34, 119246)),
        ),
        migrations.AlterField(
            model_name='profit_stat',
            name='yesterday',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 3, 3, 51, 34, 119246)),
        ),
    ]