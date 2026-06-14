from groq import Groq
from django.conf import settings


class BaseAgent:
    MODEL = "llama-3.3-70b-versatile"

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def _call(self, system_prompt: str, user_message: str, max_tokens: int = 2000) -> str:
        response = self.client.chat.completions.create(
            model=self.MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content

    def _format_patient_context(self, patient) -> str:
        vitals = patient.vitals.first()
        labs = patient.lab_results.all()[:15]

        lines = [
            f"PATIENT PROFILE",
            f"Name        : {patient.full_name()}",
            f"Age         : {patient.age} years",
            f"Gender      : {patient.get_gender_display()}",
            f"Blood Group : {patient.blood_group}",
            f"Allergies   : {patient.allergies or 'None reported'}",
            f"Medications : {patient.current_medications or 'None'}",
            f"History     : {patient.medical_history or 'None'}",
            "",
        ]

        if vitals:
            lines += [
                "VITAL SIGNS (most recent)",
                f"  Blood Pressure    : {vitals.systolic_bp}/{vitals.diastolic_bp} mmHg",
                f"  Heart Rate        : {vitals.heart_rate} bpm",
                f"  Respiratory Rate  : {vitals.respiratory_rate} breaths/min",
                f"  Temperature       : {vitals.temperature} °C",
                f"  SpO2              : {vitals.spo2}%",
                f"  BMI               : {vitals.bmi()}",
                "",
            ]

        if labs:
            lines.append("LAB RESULTS")
            for lab in labs:
                flag = " [ABNORMAL]" if lab.is_abnormal else ""
                lines.append(f"  {lab.test_name}: {lab.value} {lab.unit} (ref: {lab.normal_range}){flag}")
            lines.append("")

        return "\n".join(lines)