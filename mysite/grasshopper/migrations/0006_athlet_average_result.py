# Generated by Django 4.1.13 on 2024-11-05 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grasshopper', '0005_alter_athlet_results'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlet',
            name='average_result',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
