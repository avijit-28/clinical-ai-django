from django.contrib import admin
from .models import Patient, VitalSigns, LabResult, Diagnosis, RiskAlert, TreatmentPlan, CarePathway

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'age', 'gender', 'blood_group', 'admitted_on']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(VitalSigns)
class VitalSignsAdmin(admin.ModelAdmin):
    list_display = ['patient', 'systolic_bp', 'diastolic_bp', 'heart_rate', 'spo2', 'recorded_at']

@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ['patient', 'test_name', 'value', 'unit', 'is_abnormal', 'tested_at']

@admin.register(RiskAlert)
class RiskAlertAdmin(admin.ModelAdmin):
    list_display = ['patient', 'risk_level', 'risk_score', 'is_acknowledged', 'created_at']

@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ['patient', 'primary_diagnosis', 'confidence_score', 'created_at']

@admin.register(TreatmentPlan)
class TreatmentPlanAdmin(admin.ModelAdmin):
    list_display = ['patient', 'created_at']

@admin.register(CarePathway)
class CarePathwayAdmin(admin.ModelAdmin):
    list_display = ['patient', 'estimated_duration', 'created_at']
