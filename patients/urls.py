from django.urls import path
from . import views

urlpatterns = [
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:patient_id>/analyze/', views.analyze_patient, name='analyze_patient'),
    path('alerts/', views.alerts_list, name='alerts_list'),
    path('alerts/<int:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
]
