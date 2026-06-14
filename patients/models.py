from django.db import models
from django.utils import timezone


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    BLOOD_GROUP_CHOICES = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
    ]

    first_name       = models.CharField(max_length=100)
    last_name        = models.CharField(max_length=100)
    age              = models.IntegerField()
    gender           = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group      = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    contact_number   = models.CharField(max_length=15)
    email            = models.EmailField(blank=True)
    address          = models.TextField(blank=True)
    medical_history  = models.TextField(blank=True, help_text="Past conditions, surgeries")
    current_medications = models.TextField(blank=True)
    allergies        = models.TextField(blank=True)
    admitted_on      = models.DateTimeField(default=timezone.now)
    created_at       = models.DateTimeField(auto_now_add=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name()} (Age: {self.age})"

    class Meta:
        ordering = ['-created_at']


class VitalSigns(models.Model):
    patient          = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vitals')
    systolic_bp      = models.IntegerField(help_text="mmHg")
    diastolic_bp     = models.IntegerField(help_text="mmHg")
    heart_rate       = models.IntegerField(help_text="bpm")
    respiratory_rate = models.IntegerField(help_text="breaths/min")
    temperature      = models.FloatField(help_text="Celsius")
    spo2             = models.FloatField(help_text="Oxygen saturation %")
    weight           = models.FloatField(help_text="kg")
    height           = models.FloatField(help_text="cm")
    recorded_at      = models.DateTimeField(default=timezone.now)

    def bmi(self):
        h = self.height / 100
        return round(self.weight / (h * h), 1)

    def __str__(self):
        return f"Vitals for {self.patient.full_name()} at {self.recorded_at:%Y-%m-%d %H:%M}"

    class Meta:
        ordering = ['-recorded_at']


class LabResult(models.Model):
    patient       = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    test_name     = models.CharField(max_length=200)
    value         = models.CharField(max_length=100)
    unit          = models.CharField(max_length=50, blank=True)
    normal_range  = models.CharField(max_length=100, blank=True)
    is_abnormal   = models.BooleanField(default=False)
    notes         = models.TextField(blank=True)
    tested_at     = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.test_name}: {self.value} {self.unit} ({self.patient.full_name()})"

    class Meta:
        ordering = ['-tested_at']


class Diagnosis(models.Model):
    patient           = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diagnoses')
    primary_diagnosis = models.CharField(max_length=300)
    differentials     = models.JSONField(default=list, help_text="List of {name, confidence, reasoning}")
    icd_code          = models.CharField(max_length=20, blank=True)
    reasoning         = models.TextField()
    confidence_score  = models.FloatField(default=0.0)
    agent_version     = models.CharField(max_length=50, default='claude-3-5-sonnet')
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.primary_diagnosis} — {self.patient.full_name()}"

    class Meta:
        ordering = ['-created_at']


class RiskAlert(models.Model):
    RISK_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    patient         = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='risk_alerts')
    risk_level      = models.CharField(max_length=10, choices=RISK_LEVELS)
    risk_score      = models.IntegerField(help_text="0-100")
    alert_reasons   = models.JSONField(default=list)
    immediate_actions = models.JSONField(default=list)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    LEVEL_ORDER = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}

    def __str__(self):
        return f"[{self.risk_level.upper()}] {self.patient.full_name()}"

    class Meta:
        ordering = ['-created_at']


class TreatmentPlan(models.Model):
    patient        = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatment_plans')
    diagnosis      = models.ForeignKey(Diagnosis, on_delete=models.SET_NULL, null=True, blank=True)
    medications    = models.JSONField(default=list, help_text="List of {name, dose, frequency, duration}")
    interventions  = models.JSONField(default=list)
    monitoring     = models.JSONField(default=list, help_text="Parameters to monitor")
    contraindications = models.JSONField(default=list)
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Treatment plan for {self.patient.full_name()} on {self.created_at:%Y-%m-%d}"

    class Meta:
        ordering = ['-created_at']


class CarePathway(models.Model):
    patient           = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='care_pathways')
    treatment_plan    = models.ForeignKey(TreatmentPlan, on_delete=models.SET_NULL, null=True, blank=True)
    daily_schedule    = models.JSONField(default=list, help_text="List of {day, tasks}")
    care_team_tasks   = models.JSONField(default=dict, help_text="{doctor:[], nurse:[], lab:[]}")
    follow_up_dates   = models.JSONField(default=list)
    discharge_criteria = models.JSONField(default=list)
    estimated_duration = models.CharField(max_length=100, blank=True)
    sustainability_notes = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Care pathway for {self.patient.full_name()} ({self.estimated_duration})"

    class Meta:
        ordering = ['-created_at']
