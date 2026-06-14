from django.shortcuts import render
from patients.models import Patient, RiskAlert


def index(request):
    patients = Patient.objects.all()
    alerts = RiskAlert.objects.filter(is_acknowledged=False).select_related('patient')[:10]
    level_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    alerts = sorted(alerts, key=lambda a: level_order.get(a.risk_level, 4))

    counts = {
        'total': patients.count(),
        'critical': RiskAlert.objects.filter(risk_level='critical', is_acknowledged=False).count(),
        'high': RiskAlert.objects.filter(risk_level='high', is_acknowledged=False).count(),
        'unassessed': sum(1 for p in patients if not p.risk_alerts.exists()),
    }

    return render(request, 'dashboard/index.html', {
        'patients': patients,
        'alerts': alerts,
        'counts': counts,
    })


def patient_view(request, patient_id):
    from django.shortcuts import get_object_or_404
    patient = get_object_or_404(Patient, id=patient_id)
    vitals = patient.vitals.first()
    labs = patient.lab_results.all()[:15]
    return render(request, 'patients/detail.html', {
        'patient': patient,
        'vitals': vitals,
        'labs': labs,
    })
