# Generated by Django 2.0.4 on 2018-05-15 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hts_backend', '0051_auto_20180516_0045'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='granttreestructure',
            options={'verbose_name': '대출 요청과 처리 내역'},
        ),
        migrations.AddField(
            model_name='granttreestructure',
            name='admin_id1',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='granttreestructure',
            name='admin_id2',
            field=models.CharField(default='', max_length=50),
        ),
    ]
