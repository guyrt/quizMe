# Generated by Django 5.0.3 on 2024-03-27 20:06

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_alter_looseusersettings_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="date_joined",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
