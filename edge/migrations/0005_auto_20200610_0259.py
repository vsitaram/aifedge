# Generated by Django 3.0.7 on 2020-06-10 06:59

import aifedge.storage_backends
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edge', '0004_auto_20200609_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='upload',
            field=models.FileField(default=None, storage=aifedge.storage_backends.PublicFileStorage(), upload_to=''),
        ),
    ]