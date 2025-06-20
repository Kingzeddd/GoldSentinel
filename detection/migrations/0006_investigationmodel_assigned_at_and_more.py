# Generated by Django 5.2.1 on 2025-06-02 02:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detection', '0005_alter_detectionmodel_detection_type_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='investigationmodel',
            name='assigned_at',
            field=models.DateTimeField(blank=True, help_text='Timestamp when the investigation was assigned', null=True),
        ),
        migrations.AddField(
            model_name='investigationmodel',
            name='assigned_by',
            field=models.ForeignKey(blank=True, help_text='User who assigned the investigation', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='investigations_coordinated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='investigationmodel',
            name='assignment_notes',
            field=models.TextField(blank=True, help_text='Notes provided during assignment'),
        ),
        migrations.AddField(
            model_name='investigationmodel',
            name='priority',
            field=models.CharField(default='MEDIUM', help_text='Priority of the investigation (LOW, MEDIUM, HIGH)', max_length=10),
        ),
        migrations.AlterField(
            model_name='investigationmodel',
            name='access_instructions',
            field=models.TextField(blank=True, help_text="Instructions to access the site (e.g., 'Take road X, village Y')"),
        ),
        migrations.AlterField(
            model_name='investigationmodel',
            name='assigned_to',
            field=models.ForeignKey(blank=True, help_text='Agent assigned to this investigation', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_investigations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='investigationmodel',
            name='field_notes',
            field=models.TextField(blank=True, help_text='Notes from the field investigation'),
        ),
        migrations.AlterField(
            model_name='investigationmodel',
            name='investigation_date',
            field=models.DateField(blank=True, help_text='Date the investigation was conducted', null=True),
        ),
        migrations.AlterField(
            model_name='investigationmodel',
            name='result',
            field=models.CharField(blank=True, choices=[('CONFIRMED', 'Confirmé'), ('FALSE_POSITIVE', 'Faux positif'), ('NEEDS_MONITORING', 'Surveillance nécessaire')], help_text='Result of the field investigation', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='investigationmodel',
            name='status',
            field=models.CharField(choices=[('PENDING', 'En attente'), ('ASSIGNED', 'Assignée'), ('IN_PROGRESS', 'En cours'), ('COMPLETED', 'Terminée')], default='PENDING', help_text='Current status of the investigation', max_length=20),
        ),
        migrations.AlterField(
            model_name='investigationmodel',
            name='target_coordinates',
            field=models.CharField(help_text="Coordinates of the target (e.g., '8.0402, -2.8000')", max_length=50),
        ),
    ]
