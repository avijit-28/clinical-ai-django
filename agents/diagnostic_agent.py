import json
import re
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are an expert clinical diagnostician AI agent with deep knowledge across
internal medicine, emergency medicine, and specialist care. You analyse patient data and produce
a structured differential diagnosis.

Always respond in this exact JSON format (no markdown, no extra text):
{
  "primary_diagnosis": "Most likely diagnosis",
  "confidence_score": 0.0,
  "icd_code": "ICD-10 code",
  "reasoning": "Step-by-step clinical reasoning",
  "differentials": [
    {"name": "Diagnosis 1", "confidence": 0.0, "key_findings": "supporting evidence"},
    {"name": "Diagnosis 2", "confidence": 0.0, "key_findings": "supporting evidence"},
    {"name": "Diagnosis 3", "confidence": 0.0, "key_findings": "supporting evidence"}
  ],
  "red_flags": ["list of concerning findings"],
  "recommended_tests": ["additional tests if needed"]
}"""


class DiagnosticAgent(BaseAgent):
    def run(self, patient) -> dict:
        context = self._format_patient_context(patient)
        prompt = f"""Analyse this patient and provide a full differential diagnosis.\n\n{context}"""
        response = self._call(SYSTEM_PROMPT, prompt, max_tokens=2000)

        try:
            clean = re.sub(r'```json|```', '', response).strip()
            return json.loads(clean)
        except json.JSONDecodeError:
            return {
                "primary_diagnosis": "Unable to parse — see raw output",
                "confidence_score": 0.0,
                "icd_code": "",
                "reasoning": response,
                "differentials": [],
                "red_flags": [],
                "recommended_tests": [],
            }
