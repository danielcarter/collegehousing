# Generated by Django 3.0.7 on 2020-07-09 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rent_data', '0018_auto_20200709_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eviction',
            name='date',
            field=models.DateField(null=True),
        ),
    ]