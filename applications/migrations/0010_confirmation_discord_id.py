# Generated by Django 2.2.13 on 2021-02-20 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0009_application_referrer_locked'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmation',
            name='discord_id',
            field=models.CharField(default='', max_length=100),
        ),
    ]
