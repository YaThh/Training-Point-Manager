# Generated by Django 5.0.4 on 2024-05-15 11:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TrainingPoint', '0002_alter_missingpointreport_proof'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classification',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
