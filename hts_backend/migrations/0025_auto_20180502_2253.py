# Generated by Django 2.0.4 on 2018-05-02 13:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hts_backend', '0024_auto_20180502_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profit_stat',
            name='daybefore',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 2, 22, 53, 20, 940597)),
        ),
        migrations.AlterField(
            model_name='profit_stat',
            name='yesterday',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 2, 22, 53, 20, 940597)),
        ),
    ]