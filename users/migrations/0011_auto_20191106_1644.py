# Generated by Django 2.2.5 on 2019-11-06 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20191028_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailview',
            name='sent',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Sent Date (in UTC)'),
        ),
        migrations.AlterField(
            model_name='emailview',
            name='viewed',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Viewed Date (in UTC)'),
        ),
    ]
