# Generated by Django 5.1.4 on 2025-03-05 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_watchlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
