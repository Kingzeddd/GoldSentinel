# Generated by Django 5.2.1 on 2025-05-31 17:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detection', '0003_investigationmodel_detectionfeedbackmodel_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='investigationmodel',
            name='assigned_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_investigations', to=settings.AUTH_USER_MODEL),
        ),
    ]
