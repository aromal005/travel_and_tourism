# Generated by Django 5.1.6 on 2025-02-27 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel_agent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('cat_description', models.TextField()),
            ],
        ),
    ]
