# Generated by Django 4.1.3 on 2022-12-21 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0002_settings_judging_deadline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='application_confirmation_deadline',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='settings',
            name='application_submission_deadline',
            field=models.DateTimeField(),
        ),
    ]
