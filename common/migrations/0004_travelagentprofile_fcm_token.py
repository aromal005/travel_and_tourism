# Generated by Django 5.1.6 on 2025-03-25 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_travelagentprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='travelagentprofile',
            name='fcm_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
