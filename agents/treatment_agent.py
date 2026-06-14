import json
import re
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are an evidence-based treatment planning AI agent. You generate
comprehensive, personalised treatment plans based on clinical guidelines (WHO, NICE, AHA).

Always respond in this exact JSON format (no markdown, no extra text):
{
  "medications": [
    {"name": "Drug name", "dose": "dose", "route": "oral/IV/etc", "frequency": "freq", "duration": "duration", "notes": ""}
  ],
  "interventions": ["procedure or intervention 1", "procedure 2"],
  "monitoring_parameters": ["what to monitor", "frequency"],
  "contraindications_noted": ["any contraindications flagged"],
  "lifestyle_advice": ["diet", "activity", "other"],
  "follow_up": "when to follow up",
  "evidence_basis": "guidelines referenced",
  "specialist_referral": "if any specialist needed"
}"""


class TreatmentAgent(BaseAgent):
    def run(self, patient, diagnosis_result: dict = None, risk_result: dict = None) -> dict:
        context = self._format_patient_context(patient)

        dx_section = ""
        if diagnosis_result:
            dx_section = f"""
CONFIRMED DIAGNOSIS
Primary : {diagnosis_result.get('primary_diagnosis', 'Unknown')}
ICD     : {diagnosis_result.get('icd_code', '')}
Reasoning: {diagnosis_result.get('reasoning', '')[:300]}
"""

        risk_section = ""
        if risk_result:
            risk_section = f"""
RISK ASSESSMENT
Level   : {risk_result.get('risk_level', 'unknown').upper()}
Score   : {risk_result.get('risk_score', 0)}/100
Actions : {', '.join(risk_result.get('immediate_actions', []))}
"""

        prompt = f"""Create a comprehensive evidence-based treatment plan.\n\n{context}{dx_section}{risk_section}"""
        response = self._call(SYSTEM_PROMPT, prompt, max_tokens=2000)

        try:
            clean = re.sub(r'```json|```', '', response).strip()
            return json.loads(clean)
        except json.JSONDecodeError:
            return {
                "medications": [],
                "interventions": [],
                "monitoring_parameters": [],
                "contraindications_noted": [],
                "lifestyle_advice": [],
                "follow_up": "To be determined",
                "evidence_basis": response,
                "specialist_referral": "None",
            }
