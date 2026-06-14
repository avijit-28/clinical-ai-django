from django.urls import path
from . import views
from patients.views import add_patient

urlpatterns = [
    path('', views.index, name='index'),
    path('patients/<int:patient_id>/', views.patient_view, name='patient_view'),
     path('patients/add/', add_patient, name='add_patient'),
]
