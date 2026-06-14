import json
import re
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are a patient risk assessment AI agent. You continuously monitor patient
data to identify deterioration, sepsis, cardiac events, and other life-threatening conditions.

Always respond in this exact JSON format (no markdown, no extra text):
{
  "risk_level": "low|medium|high|critical",
  "risk_score": 0,
  "alert_reasons": ["reason 1", "reason 2"],
  "immediate_actions": ["action 1", "action 2"],
  "monitoring_frequency": "e.g. every 15 minutes",
  "escalation_required": true,
  "clinical_notes": "Brief clinical summary"
}

Risk score is 0-100. Risk levels: low=0-25, medium=26-50, high=51-75, critical=76-100."""


class RiskAgent(BaseAgent):
    def run(self, patient, diagnosis_result: dict = None) -> dict:
        context = self._format_patient_context(patient)

        diagnosis_section = ""
        if diagnosis_result:
            diagnosis_section = f"""
CURRENT DIAGNOSIS
Primary : {diagnosis_result.get('primary_diagnosis', 'Unknown')}
Red Flags: {', '.join(diagnosis_result.get('red_flags', []))}
"""

        prompt = f"""Assess the risk level for this patient and generate alerts if needed.\n\n{context}{diagnosis_section}"""
        response = self._call(SYSTEM_PROMPT, prompt, max_tokens=1000)

        try:
            clean = re.sub(r'```json|```', '', response).strip()
            return json.loads(clean)
        except json.JSONDecodeError:
            return {
                "risk_level": "medium",
                "risk_score": 50,
                "alert_reasons": ["Unable to parse agent response"],
                "immediate_actions": ["Manual review required"],
                "monitoring_frequency": "Every 30 minutes",
                "escalation_required": False,
                "clinical_notes": response,
            }
