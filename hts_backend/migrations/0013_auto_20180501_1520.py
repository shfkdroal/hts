# Generated by Django 2.0.4 on 2018-05-01 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hts_backend', '0012_marketstatus_ovnfee'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessed_user',
            name='accessing_time_now',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='accessed_user',
            name='behave_type',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='share_chart',
            name='C_load_balance_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='accessed_user',
            name='access_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
