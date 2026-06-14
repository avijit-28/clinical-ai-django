import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Patient, VitalSigns, LabResult, RiskAlert, Diagnosis, TreatmentPlan, CarePathway
from agents.orchestrator import Orchestrator


def patient_list(request):
    patients = Patient.objects.all()
    data = []
    for p in patients:
        latest_alert = p.risk_alerts.first()
        data.append({
            'id': p.id,
            'name': p.full_name(),
            'age': p.age,
            'gender': p.get_gender_display(),
            'blood_group': p.blood_group,
            'admitted_on': p.admitted_on.strftime('%Y-%m-%d'),
            'risk_level': latest_alert.risk_level if latest_alert else 'unassessed',
            'risk_score': latest_alert.risk_score if latest_alert else None,
        })
    return JsonResponse({'patients': data})


def patient_detail(request, patient_id):
    try:
        p = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)

    vitals = p.vitals.first()
    labs = list(p.lab_results.values(
        'test_name', 'value', 'unit', 'normal_range', 'is_abnormal', 'tested_at'
    )[:20])
    for lab in labs:
        lab['tested_at'] = str(lab['tested_at'])

    latest_diagnosis = p.diagnoses.first()
    latest_risk = p.risk_alerts.first()
    latest_treatment = p.treatment_plans.first()
    latest_pathway = p.care_pathways.first()

    return JsonResponse({
        'id': p.id,
        'name': p.full_name(),
        'first_name': p.first_name,
        'last_name': p.last_name,
        'age': p.age,
        'gender': p.get_gender_display(),
        'blood_group': p.blood_group,
        'contact_number': p.contact_number,
        'email': p.email,
        'address': p.address,
        'medical_history': p.medical_history,
        'current_medications': p.current_medications,
        'allergies': p.allergies,
        'admitted_on': p.admitted_on.strftime('%Y-%m-%d'),
        'vitals': {
            'systolic_bp': vitals.systolic_bp,
            'diastolic_bp': vitals.diastolic_bp,
            'heart_rate': vitals.heart_rate,
            'respiratory_rate': vitals.respiratory_rate,
            'temperature': vitals.temperature,
            'spo2': vitals.spo2,
            'weight': vitals.weight,
            'height': vitals.height,
            'bmi': vitals.bmi(),
            'recorded_at': vitals.recorded_at.strftime('%Y-%m-%d %H:%M'),
        } if vitals else None,
        'lab_results': labs,
        'latest_diagnosis': {
            'primary': latest_diagnosis.primary_diagnosis,
            'differentials': latest_diagnosis.differentials,
            'confidence': latest_diagnosis.confidence_score,
            'reasoning': latest_diagnosis.reasoning,
            'created_at': latest_diagnosis.created_at.strftime('%Y-%m-%d %H:%M'),
        } if latest_diagnosis else None,
        'latest_risk': {
            'level': latest_risk.risk_level,
            'score': latest_risk.risk_score,
            'reasons': latest_risk.alert_reasons,
            'actions': latest_risk.immediate_actions,
        } if latest_risk else None,
        'latest_treatment': {
            'medications': latest_treatment.medications,
            'interventions': latest_treatment.interventions,
            'monitoring': latest_treatment.monitoring,
            'contraindications': latest_treatment.contraindications,
        } if latest_treatment else None,
        'latest_pathway': {
            'daily_schedule': latest_pathway.daily_schedule,
            'care_team_tasks': latest_pathway.care_team_tasks,
            'estimated_duration': latest_pathway.estimated_duration,
            'discharge_criteria': latest_pathway.discharge_criteria,
        } if latest_pathway else None,
    })


@csrf_exempt
def analyze_patient(request, patient_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        p = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)

    try:
        orchestrator = Orchestrator()
        report = orchestrator.run(p)
        return JsonResponse({'success': True, 'report': report})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def alerts_list(request):
    level_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    alerts = RiskAlert.objects.filter(is_acknowledged=False).select_related('patient')
    data = [
        {
            'id': a.id,
            'patient_id': a.patient.id,
            'patient_name': a.patient.full_name(),
            'risk_level': a.risk_level,
            'risk_score': a.risk_score,
            'reasons': a.alert_reasons,
            'actions': a.immediate_actions,
            'created_at': a.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        for a in alerts
    ]
    data.sort(key=lambda x: level_order.get(x['risk_level'], 4))
    return JsonResponse({'alerts': data})


@csrf_exempt
def acknowledge_alert(request, alert_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        alert = RiskAlert.objects.get(id=alert_id)
        alert.is_acknowledged = True
        alert.acknowledged_at = timezone.now()
        alert.save()
        return JsonResponse({'success': True})
    except RiskAlert.DoesNotExist:
        return JsonResponse({'error': 'Alert not found'}, status=404)


LAB_FIELDS = [
    ('Haemoglobin',      'haemoglobin',      'g/dL',   '12–17'),
    ('WBC Count',        'wbc',              'K/uL',   '4–11'),
    ('Platelet Count',   'platelets',        'K/uL',   '150–400'),
    ('Blood Glucose',    'glucose',          'mg/dL',  '70–100'),
    ('HbA1c',            'hba1c',            '%',      '< 5.7'),
    ('Creatinine',       'creatinine',       'mg/dL',  '0.6–1.2'),
    ('Sodium',           'sodium',           'mEq/L',  '136–145'),
    ('Potassium',        'potassium',        'mEq/L',  '3.5–5.0'),
    ('Total Cholesterol','cholesterol',      'mg/dL',  '< 200'),
    ('CRP',              'crp',              'mg/L',   '< 10'),
    ('ALT',              'alt',              'U/L',    '7–56'),
    ('Troponin I',       'troponin',         'ng/mL',  '< 0.04'),
]

LAB_NORMAL = {
    'haemoglobin': (11.5, 17.5), 'wbc': (4.0, 11.0),
    'platelets': (150, 400),     'glucose': (70, 140),
    'hba1c': (0, 5.7),           'creatinine': (0.6, 1.2),
    'sodium': (136, 145),        'potassium': (3.5, 5.0),
    'cholesterol': (0, 200),     'crp': (0, 10),
    'alt': (7, 56),              'troponin': (0, 0.04),
}

def add_patient(request):
    from patients.models import VitalSigns, LabResult
    ctx = {}

    if request.method == 'POST':
        try:
            # Patient
            p = Patient.objects.create(
                first_name  = request.POST.get('first_name','').strip(),
                last_name   = request.POST.get('last_name','').strip(),
                age         = int(request.POST.get('age', 0)),
                gender      = request.POST.get('gender','M'),
                blood_group = request.POST.get('blood_group','O+'),
                contact_number = request.POST.get('contact_number','').strip(),
                email       = request.POST.get('email','').strip(),
                address     = request.POST.get('address','').strip(),
                medical_history     = request.POST.get('medical_history','').strip(),
                current_medications = request.POST.get('current_medications','').strip(),
                allergies   = request.POST.get('allergies','').strip(),
            )
            # Vitals
            VitalSigns.objects.create(
                patient          = p,
                systolic_bp      = int(request.POST.get('systolic_bp', 120)),
                diastolic_bp     = int(request.POST.get('diastolic_bp', 80)),
                heart_rate       = int(request.POST.get('heart_rate', 72)),
                respiratory_rate = int(request.POST.get('respiratory_rate', 16)),
                temperature      = float(request.POST.get('temperature', 37.0)),
                spo2             = float(request.POST.get('spo2', 98)),
                weight           = float(request.POST.get('weight', 70)),
                height           = float(request.POST.get('height', 170)),
            )
            # Labs
            LAB_MAP = [
                ('Haemoglobin','haemoglobin','g/dL','12–17',(11.5,17.5)),
                ('WBC Count','wbc','K/uL','4–11',(4.0,11.0)),
                ('Platelet Count','platelets','K/uL','150–400',(150,400)),
                ('Blood Glucose','glucose','mg/dL','70–100',(70,140)),
                ('HbA1c','hba1c','%','< 5.7',(0,5.7)),
                ('Creatinine','creatinine','mg/dL','0.6–1.2',(0.6,1.2)),
                ('Sodium','sodium','mEq/L','136–145',(136,145)),
                ('Potassium','potassium','mEq/L','3.5–5.0',(3.5,5.0)),
                ('Total Cholesterol','cholesterol','mg/dL','< 200',(0,200)),
                ('CRP','crp','mg/L','< 10',(0,10)),
                ('ALT','alt','U/L','7–56',(7,56)),
                ('Troponin I','troponin','ng/mL','< 0.04',(0,0.04)),
            ]
            for label, name, unit, ref, (lo, hi) in LAB_MAP:
                val = request.POST.get('lab_' + name, '').strip()
                if val:
                    try:
                        v = float(val)
                        abnormal = not (lo <= v <= hi)
                    except ValueError:
                        abnormal = False
                    LabResult.objects.create(
                        patient=p, test_name=label,
                        value=val, unit=unit,
                        normal_range=ref, is_abnormal=abnormal,
                    )
            ctx['success'] = p.full_name()
            ctx['new_id']  = p.id
        except Exception as e:
            ctx['error'] = str(e)

    from django.shortcuts import render
    return render(request, 'patients/add.html', ctx)
