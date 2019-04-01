# Generated by Django 2.0.4 on 2018-05-12 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hts_backend', '0049_transaction_share_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketstatus',
            name='Is_Testing_Buy_Sell',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='marketstatus',
            name='BasicFeeBuy',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='marketstatus',
            name='BasicFeeSell',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='marketstatus',
            name='BuyFee',
            field=models.FloatField(default=0.03),
        ),
        migrations.AlterField(
            model_name='marketstatus',
            name='Max_Task',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='marketstatus',
            name='SellFee',
            field=models.FloatField(default=0.03),
        ),
    ]
