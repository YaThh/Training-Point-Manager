# Generated by Django 5.0.4 on 2024-05-11 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TrainingPoint', '0002_remove_studentactivity_achievement_alter_news_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievement',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='department',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='grade',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='missingpointreport',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='news',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='studentactivity',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='trainingpoint',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
