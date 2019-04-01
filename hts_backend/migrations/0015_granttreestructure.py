# Generated by Django 2.0.4 on 2018-05-01 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hts_backend', '0014_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrantTreeStructure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_idx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hts_backend.admins')),
                ('admin_refer_idx', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_refer_idx', to='hts_backend.admins')),
            ],
        ),
    ]