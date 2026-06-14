"""
Run this script to populate the database with 20 realistic mock patients.

Usage:
    python scripts/seed_data.py
"""
import os
import sys
import django
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_ai.settings')
django.setup()

from faker import Faker
from patients.models import Patient, VitalSigns, LabResult

fake = Faker('en_IN')
random.seed(42)

LAB_PANELS = [
    # (test_name, unit, normal_range, low, high, abnormal_threshold_low, abnormal_threshold_high)
    ('Haemoglobin',     'g/dL',   '12–17',    9.0,  18.0, 11.5, 17.5),
    ('WBC Count',       'K/uL',   '4–11',     2.0,  18.0, 4.0,  11.0),
    ('Platelet Count',  'K/uL',   '150–400',  50.0, 600.0, 150.0, 400.0),
    ('Sodium',          'mEq/L',  '136–145',  125.0, 155.0, 136.0, 145.0),
    ('Potassium',       'mEq/L',  '3.5–5.0',  2.5,  6.5,  3.5,  5.0),
    ('Creatinine',      'mg/dL',  '0.6–1.2',  0.4,  5.0,  0.6,  1.2),
    ('Blood Glucose',   'mg/dL',  '70–100',   50.0, 400.0, 70.0, 140.0),
    ('HbA1c',           '%',      '< 5.7',    4.0,  12.0, 4.0,  5.7),
    ('Total Cholesterol','mg/dL', '< 200',    100.0, 350.0, 0,   200.0),
    ('CRP',             'mg/L',   '< 10',     0.1,  200.0, 0,   10.0),
    ('ALT',             'U/L',    '7–56',     5.0,  300.0, 7.0,  56.0),
    ('Troponin I',      'ng/mL',  '< 0.04',   0.01, 5.0,  0,    0.04),
]

MEDICAL_HISTORIES = [
    'Type 2 Diabetes Mellitus diagnosed 5 years ago',
    'Hypertension, on antihypertensive therapy for 3 years',
    'Chronic Kidney Disease Stage 2, history of UTI',
    'Ischaemic Heart Disease, PTCA done 2 years ago',
    'Asthma since childhood, on inhaler therapy',
    'No significant past medical history',
    'Hypothyroidism on levothyroxine',
    'Chronic Obstructive Pulmonary Disease (COPD), ex-smoker',
    'Rheumatoid Arthritis on DMARDs',
    'Epilepsy, controlled on antiepileptics',
    'History of pulmonary tuberculosis, completed treatment',
    'Anaemia, on iron supplementation',
]

MEDICATIONS = [
    'Metformin 500mg BD, Atorvastatin 10mg OD',
    'Amlodipine 5mg OD, Telmisartan 40mg OD',
    'Aspirin 75mg OD, Atorvastatin 20mg OD, Metoprolol 25mg BD',
    'Levothyroxine 50mcg OD',
    'Salbutamol inhaler PRN, Budesonide inhaler BD',
    'None',
    'Folic acid 5mg OD, Ferrous sulphate 200mg BD',
    'Methotrexate 10mg weekly, Folic acid 5mg OD',
    'Sodium valproate 500mg BD',
]

ALLERGIES = [
    'Penicillin — rash',
    'Sulpha drugs — anaphylaxis',
    'NSAIDs — gastric upset',
    'None known',
    'None known',
    'None known',
    'Contrast dye — urticaria',
    'Codeine — nausea',
]


def make_vitals(patient, risk_level='normal'):
    """Generate vitals that vary by risk profile."""
    if risk_level == 'critical':
        sbp  = random.randint(80, 100)
        dbp  = random.randint(50, 70)
        hr   = random.randint(110, 140)
        rr   = random.randint(24, 32)
        temp = round(random.uniform(38.8, 40.2), 1)
        spo2 = round(random.uniform(88, 93), 1)
    elif risk_level == 'high':
        sbp  = random.randint(160, 190)
        dbp  = random.randint(100, 120)
        hr   = random.randint(95, 115)
        rr   = random.randint(20, 26)
        temp = round(random.uniform(37.8, 38.8), 1)
        spo2 = round(random.uniform(93, 96), 1)
    else:
        sbp  = random.randint(110, 135)
        dbp  = random.randint(70, 88)
        hr   = random.randint(62, 90)
        rr   = random.randint(14, 18)
        temp = round(random.uniform(36.4, 37.4), 1)
        spo2 = round(random.uniform(97, 100), 1)

    weight = round(random.uniform(52, 95), 1)
    height = round(random.uniform(155, 185), 1)

    return VitalSigns.objects.create(
        patient=patient,
        systolic_bp=sbp, diastolic_bp=dbp,
        heart_rate=hr, respiratory_rate=rr,
        temperature=temp, spo2=spo2,
        weight=weight, height=height,
    )


def make_labs(patient, abnormal_chance=0.3):
    """Generate a full lab panel for a patient."""
    for name, unit, ref, lo, hi, norm_lo, norm_hi in LAB_PANELS:
        value = round(random.uniform(lo, hi), 2)
        is_abnormal = not (norm_lo <= value <= norm_hi)

        # Force a few abnormals if chance says so
        if random.random() < abnormal_chance and not is_abnormal:
            value = round(random.choice([
                random.uniform(lo, norm_lo * 0.9),
                random.uniform(norm_hi * 1.1, hi),
            ]), 2)
            is_abnormal = True

        LabResult.objects.create(
            patient=patient,
            test_name=name,
            value=str(value),
            unit=unit,
            normal_range=ref,
            is_abnormal=is_abnormal,
        )


def seed():
    print("Seeding 20 mock patients...")
    Patient.objects.all().delete()

    risk_profiles = ['critical'] * 3 + ['high'] * 5 + ['normal'] * 12
    random.shuffle(risk_profiles)

    for i, risk in enumerate(risk_profiles):
        gender = random.choice(['M', 'F'])
        first = fake.first_name_male() if gender == 'M' else fake.first_name_female()
        last  = fake.last_name()

        p = Patient.objects.create(
            first_name=first,
            last_name=last,
            age=random.randint(28, 78),
            gender=gender,
            blood_group=random.choice(['A+','B+','O+','AB+','A-','B-','O-']),
            contact_number=fake.phone_number()[:15],
            email=fake.email(),
            address=fake.address(),
            medical_history=random.choice(MEDICAL_HISTORIES),
            current_medications=random.choice(MEDICATIONS),
            allergies=random.choice(ALLERGIES),
        )

        make_vitals(p, risk_level=risk)
        abnormal_chance = 0.6 if risk == 'critical' else 0.4 if risk == 'high' else 0.15
        make_labs(p, abnormal_chance=abnormal_chance)

        print(f"  [{i+1:02d}] {p.full_name()} — profile: {risk}")

    print(f"\nDone. {Patient.objects.count()} patients seeded.")
    print("Run 'python manage.py runserver' and open http://127.0.0.1:8000/")


if __name__ == '__main__':
    seed()
