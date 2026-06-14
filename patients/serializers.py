from rest_framework import serializers
from .models import Patient, VitalSigns, LabResult, Diagnosis, RiskAlert, TreatmentPlan, CarePathway


class VitalSignsSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VitalSigns
        fields = '__all__'


class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LabResult
        fields = '__all__'


class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Diagnosis
        fields = '__all__'


class RiskAlertSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model  = RiskAlert
        fields = '__all__'

    def get_patient_name(self, obj):
        return str(obj.patient)


class TreatmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TreatmentPlan
        fields = '__all__'


class CarePathwaySerializer(serializers.ModelSerializer):
    class Meta:
        model  = CarePathway
        fields = '__all__'


class PatientListSerializer(serializers.ModelSerializer):
    age          = serializers.ReadOnlyField()
    latest_risk  = serializers.SerializerMethodField()

    class Meta:
        model  = Patient
        fields = ['id','first_name','last_name','age','gender','blood_group',
                  'phone','created_at','latest_risk']

    def get_latest_risk(self, obj):
        alert = obj.risk_alerts.filter(status='active').first()
        return alert.severity if alert else None


class PatientDetailSerializer(serializers.ModelSerializer):
    age          = serializers.ReadOnlyField()
    vital_signs  = VitalSignsSerializer(many=True, read_only=True)
    lab_results  = LabResultSerializer(many=True, read_only=True)
    diagnoses    = DiagnosisSerializer(many=True, read_only=True)
    risk_alerts  = RiskAlertSerializer(many=True, read_only=True)
    treatment_plans = TreatmentPlanSerializer(many=True, read_only=True)
    care_pathways   = CarePathwaySerializer(many=True, read_only=True)

    class Meta:
        model  = Patient
        fields = '__all__'
