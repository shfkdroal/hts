# Generated by Django 2.0.4 on 2018-05-02 12:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hts_backend', '0020_auto_20180502_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposit_withdraw_order_done_list',
            name='TransDateTime',
            field=models.DateTimeField(auto_created=True, auto_now=True),
        ),
        migrations.AlterField(
            model_name='profit_stat',
            name='daybefore',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 2, 21, 30, 5, 824911)),
        ),
        migrations.AlterField(
            model_name='profit_stat',
            name='yesterday',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 2, 21, 30, 5, 824911)),
        ),
    ]
