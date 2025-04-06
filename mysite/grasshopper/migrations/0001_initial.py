# Generated by Django 4.1.13 on 2024-10-08 02:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Athlet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='ФИО спортсмена')),
                ('gender', models.CharField(choices=[('MN', 'Мужчина'), ('WN', 'Женщина')], max_length=2)),
                ('rank', models.CharField(choices=[('FR', '1 разряд'), ('KM', 'КМС'), ('MS', 'МС'), ('MK', 'МСМК')], default='FR', max_length=2)),
                ('date_birthday', models.DateField(verbose_name='Дата рождения спортсмена')),
                ('publish', models.DateTimeField(default=django.utils.timezone.now)),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='region_posts', to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-publish'],
            },
        ),
        migrations.AddIndex(
            model_name='athlet',
            index=models.Index(fields=['-publish'], name='grasshopper_publish_0d3ae9_idx'),
        ),
    ]
