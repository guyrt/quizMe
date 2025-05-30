# Generated by Django 5.0.2 on 2024-02-26 22:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stripehandler", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StripeErrorLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.TextField()),
                ("event_id", models.CharField(max_length=128, unique=True)),
                ("triaged", models.BooleanField(default=False)),
            ],
        ),
    ]
