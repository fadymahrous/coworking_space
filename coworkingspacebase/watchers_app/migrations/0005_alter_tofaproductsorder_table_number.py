# Generated by Django 5.2.4 on 2025-07-16 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watchers_app', '0004_tofaproductsorder_table_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tofaproductsorder',
            name='table_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
