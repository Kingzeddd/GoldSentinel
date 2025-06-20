# Generated by Django 5.2.1 on 2025-05-29 22:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0002_remove_usermodel_access_level_and_more'),
        ('alert', '0002_alter_financialriskmodel_estimated_loss'),
        ('detection', '0003_investigationmodel_detectionfeedbackmodel_and_more'),
        ('region', '0003_remove_regionmodel_geographic_zone'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventLogModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event_type', models.CharField(choices=[('DETECTION_CREATED', 'New Detection Created'), ('ALERT_GENERATED', 'New Alert Generated'), ('ALERT_ACKNOWLEDGED', 'Alert Acknowledged'), ('ALERT_RESOLVED', 'Alert Resolved'), ('DETECTION_VALIDATED', 'Detection Validated'), ('INVESTIGATION_CREATED', 'Investigation Created'), ('INVESTIGATION_ASSIGNED', 'Investigation Assigned'), ('INVESTIGATION_COMPLETED', 'Investigation Completed'), ('ANALYSIS_STARTED', 'Analysis Started'), ('ANALYSIS_COMPLETED', 'Analysis Completed'), ('USER_LOGIN', 'User Logged In'), ('REPORT_GENERATED', 'Report Generated'), ('IMAGE_PROCESSED', 'Image Processed'), ('SYSTEM_ERROR', 'System Error'), ('FINANCIAL_RISK_CALCULATED', 'Financial Risk Calculated'), ('FEEDBACK_CREATED', 'Detection Feedback Created')], help_text='Type of system event', max_length=50)),
                ('message', models.TextField(help_text='Detailed description of the event')),
                ('metadata', models.JSONField(blank=True, help_text='Additional event data', null=True)),
                ('alert', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alert_events', to='alert.alertmodel')),
                ('detection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='detection_events', to='detection.detectionmodel')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='region_events', to='region.regionmodel')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_events', to='account.usermodel')),
            ],
            options={
                'verbose_name': 'Event Log',
                'verbose_name_plural': 'Event Logs',
                'db_table': 'event_logs',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['event_type', 'created_at'], name='event_logs_event_t_f0df7d_idx'), models.Index(fields=['user', 'event_type'], name='event_logs_user_id_80bd4f_idx'), models.Index(fields=['created_at'], name='event_logs_created_87c40d_idx')],
            },
        ),
    ]
