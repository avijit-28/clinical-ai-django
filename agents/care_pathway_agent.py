import json
import re
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are a care pathway planning AI agent. You create structured,
day-by-day care plans that coordinate the full care team efficiently and sustainably.

Always respond in this exact JSON format (no markdown, no extra text):
{
  "estimated_duration": "e.g. 5-7 days",
  "daily_schedule": [
    {"day": 1, "focus": "stabilisation", "tasks": ["task 1", "task 2"]},
    {"day": 2, "focus": "monitoring", "tasks": ["task 1"]}
  ],
  "care_team_tasks": {
    "doctor": ["task 1", "task 2"],
    "nurse": ["task 1", "task 2"],
    "lab": ["test 1", "test 2"],
    "physiotherapy": [],
    "dietitian": []
  },
  "follow_up_appointments": [
    {"when": "1 week post-discharge", "with": "cardiologist", "purpose": "review"}
  ],
  "discharge_criteria": ["criterion 1", "criterion 2"],
  "sustainability_notes": "resource efficiency and long-term care notes",
  "patient_education": ["what to teach the patient before discharge"]
}"""


class CarePathwayAgent(BaseAgent):
    def run(self, patient, diagnosis_result: dict = None,
            risk_result: dict = None, treatment_result: dict = None) -> dict:
        context = self._format_patient_context(patient)

        summary = ""
        if diagnosis_result:
            summary += f"\nDIAGNOSIS: {diagnosis_result.get('primary_diagnosis', '')}"
        if risk_result:
            summary += f"\nRISK: {risk_result.get('risk_level', '').upper()} (score {risk_result.get('risk_score', 0)})"
        if treatment_result:
            meds = [m.get('name', '') for m in treatment_result.get('medications', [])]
            summary += f"\nMEDICATIONS: {', '.join(meds)}"

        prompt = f"""Create a complete care pathway and discharge plan.\n\n{context}\nCLINICAL SUMMARY{summary}"""
        response = self._call(SYSTEM_PROMPT, prompt, max_tokens=2000)

        try:
            clean = re.sub(r'```json|```', '', response).strip()
            return json.loads(clean)
        except json.JSONDecodeError:
            return {
                "estimated_duration": "To be determined",
                "daily_schedule": [],
                "care_team_tasks": {"doctor": [], "nurse": [], "lab": []},
                "follow_up_appointments": [],
                "discharge_criteria": [],
                "sustainability_notes": response,
                "patient_education": [],
            }
