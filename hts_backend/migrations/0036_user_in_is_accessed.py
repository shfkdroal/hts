# Generated by Django 2.0.4 on 2018-05-04 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hts_backend', '0035_auto_20180503_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_in',
            name='is_accessed',
            field=models.BooleanField(default=False),
        ),
    ]