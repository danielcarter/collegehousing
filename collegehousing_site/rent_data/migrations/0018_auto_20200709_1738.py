# Generated by Django 3.0.7 on 2020-07-09 22:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rent_data', '0017_auto_20200709_1732'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='property',
            name='evictions',
        ),
        migrations.AddField(
            model_name='eviction',
            name='property',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='rent_data.Property'),
        ),
    ]
