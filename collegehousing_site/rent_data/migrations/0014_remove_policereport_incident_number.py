# Generated by Django 2.1.7 on 2020-03-17 00:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rent_data', '0013_auto_20200312_1824'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policereport',
            name='incident_number',
        ),
    ]