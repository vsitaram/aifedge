# Generated by Django 3.0.1 on 2019-12-31 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edge', '0005_auto_20191231_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pitch',
            name='pitch_date',
            field=models.DateField(verbose_name='date pitched'),
        ),
    ]
