# Generated by Django 5.1.6 on 2025-03-25 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel_agent', '0005_travelpackage_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='travelpackage',
            name='no_of_persons',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
