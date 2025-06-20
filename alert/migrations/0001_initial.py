# Generated by Django 5.2.1 on 2025-05-29 13:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0002_remove_usermodel_access_level_and_more'),
        ('detection', '0001_initial'),
        ('region', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=150)),
                ('level', models.CharField(choices=[('LOW', 'Faible'), ('MEDIUM', 'Moyen'), ('HIGH', 'Élevé'), ('CRITICAL', 'Critique')], max_length=20)),
                ('alert_type', models.CharField(choices=[('CLANDESTINE_SITE', 'Site clandestin détecté'), ('SITE_EXPANSION', "Expansion possible d'un site existant"), ('SUSPICIOUS_ACTIVITY', 'Activité suspecte détectée par IA'), ('NEW_SITE', "Nouveau site détecté près d'une rivière"), ('PROTECTED_ZONE_BREACH', 'Activité en zone protégée'), ('WATER_POLLUTION', "Pollution d'eau détectée"), ('DEFORESTATION_ALERT', 'Déforestation majeure détectée')], max_length=50)),
                ('message', models.TextField()),
                ('alert_status', models.CharField(choices=[('ACTIVE', 'Active'), ('ACKNOWLEDGED', 'Accusée'), ('RESOLVED', 'Résolue'), ('FALSE_ALARM', 'Fausse alerte')], default='ACTIVE', max_length=20)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_alerts', to='account.usermodel')),
                ('detection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='detection.detectionmodel')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='region.regionmodel')),
            ],
            options={
                'db_table': 'mining_alerts',
                'ordering': ['-sent_at'],
                'indexes': [models.Index(fields=['level', 'alert_status'], name='mining_aler_level_160610_idx'), models.Index(fields=['alert_type', 'region'], name='mining_aler_alert_t_713fe5_idx'), models.Index(fields=['region', 'sent_at'], name='mining_aler_region__c4b071_idx')],
            },
        ),
        migrations.CreateModel(
            name='FinancialRiskModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('area_hectares', models.FloatField(help_text='Surface affectée en hectares')),
                ('cost_per_hectare', models.FloatField(default=50000, help_text='Coût par hectare en FCFA')),
                ('estimated_loss', models.FloatField(help_text='Perte estimée en FCFA')),
                ('sensitive_zone_distance_km', models.FloatField(default=0, help_text='Distance zones sensibles (km)')),
                ('occurrence_count', models.IntegerField(default=1, help_text="Nombre d'occurrences détectées")),
                ('risk_level', models.CharField(choices=[('LOW', 'Faible'), ('MEDIUM', 'Moyen'), ('HIGH', 'Élevé'), ('CRITICAL', 'Critique')], max_length=20)),
                ('detection', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='financial_risk', to='detection.detectionmodel')),
            ],
            options={
                'db_table': 'financial_risks',
                'ordering': ['-estimated_loss'],
                'indexes': [models.Index(fields=['risk_level', 'estimated_loss'], name='financial_r_risk_le_32099a_idx')],
            },
        ),
    ]
