# Generated by Django 5.1.6 on 2025-04-01 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_travelagentprofile_fcm_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='fcm_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
