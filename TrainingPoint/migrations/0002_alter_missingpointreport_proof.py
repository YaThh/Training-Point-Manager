# Generated by Django 5.0.4 on 2024-05-15 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TrainingPoint', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='missingpointreport',
            name='proof',
            field=models.TextField(),
        ),
    ]
