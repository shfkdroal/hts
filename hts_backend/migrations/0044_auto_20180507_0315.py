# Generated by Django 2.0.4 on 2018-05-06 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hts_backend', '0043_auto_20180504_2326'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deposit_withdraw_order_done_list',
            old_name='WhoDidThisTransaction',
            new_name='TransactionDependency',
        ),
    ]
