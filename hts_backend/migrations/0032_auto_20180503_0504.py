# Generated by Django 2.0.4 on 2018-05-03 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hts_backend', '0031_auto_20180503_0413'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accessed_user',
            options={'verbose_name': '접속중인 회원'},
        ),
        migrations.AlterModelOptions(
            name='domainlist',
            options={'verbose_name': '도메인 리스트'},
        ),
        migrations.AlterModelOptions(
            name='m_p_managementlist',
            options={'verbose_name': '파트너 정산'},
        ),
        migrations.AlterModelOptions(
            name='profit_stat',
            options={'verbose_name': '수익 통계'},
        ),
        migrations.AddField(
            model_name='signinreq',
            name='signin_domain',
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='user_in',
            name='signin_domain',
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='domainlist',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]