from .diagnostic_agent import DiagnosticAgent
from .risk_agent import RiskAgent
from .treatment_agent import TreatmentAgent
from .care_pathway_agent import CarePathwayAgent
from patients.models import Diagnosis, RiskAlert, TreatmentPlan, CarePathway


class Orchestrator:
    """
    Runs all 4 agents in sequence for one patient.
    Each agent receives the outputs of the previous agents as context.
    Saves all results to the database and returns a combined report.
    """

    def __init__(self):
        self.diagnostic  = DiagnosticAgent()
        self.risk        = RiskAgent()
        self.treatment   = TreatmentAgent()
        self.care_pathway = CarePathwayAgent()

    def run(self, patient) -> dict:
        print(f"[Orchestrator] Starting analysis for {patient.full_name()}")

        # Step 1 — Diagnostic Agent
        print("[Orchestrator] Running DiagnosticAgent...")
        dx_result = self.diagnostic.run(patient)
        diagnosis_obj = Diagnosis.objects.create(
            patient=patient,
            primary_diagnosis=dx_result.get('primary_diagnosis', ''),
            differentials=dx_result.get('differentials', []),
            icd_code=dx_result.get('icd_code', ''),
            reasoning=dx_result.get('reasoning', ''),
            confidence_score=dx_result.get('confidence_score', 0.0),
        )

        # Step 2 — Risk Agent (uses diagnosis output)
        print("[Orchestrator] Running RiskAgent...")
        risk_result = self.risk.run(patient, diagnosis_result=dx_result)
        RiskAlert.objects.create(
            patient=patient,
            risk_level=risk_result.get('risk_level', 'medium'),
            risk_score=risk_result.get('risk_score', 50),
            alert_reasons=risk_result.get('alert_reasons', []),
            immediate_actions=risk_result.get('immediate_actions', []),
        )

        # Step 3 — Treatment Agent (uses diagnosis + risk)
        print("[Orchestrator] Running TreatmentAgent...")
        tx_result = self.treatment.run(patient, diagnosis_result=dx_result, risk_result=risk_result)
        treatment_obj = TreatmentPlan.objects.create(
            patient=patient,
            diagnosis=diagnosis_obj,
            medications=tx_result.get('medications', []),
            interventions=tx_result.get('interventions', []),
            monitoring=tx_result.get('monitoring_parameters', []),
            contraindications=tx_result.get('contraindications_noted', []),
            notes=tx_result.get('evidence_basis', ''),
        )

        # Step 4 — Care Pathway Agent (uses all previous outputs)
        print("[Orchestrator] Running CarePathwayAgent...")
        cp_result = self.care_pathway.run(
            patient,
            diagnosis_result=dx_result,
            risk_result=risk_result,
            treatment_result=tx_result,
        )
        CarePathway.objects.create(
            patient=patient,
            treatment_plan=treatment_obj,
            daily_schedule=cp_result.get('daily_schedule', []),
            care_team_tasks=cp_result.get('care_team_tasks', {}),
            follow_up_dates=cp_result.get('follow_up_appointments', []),
            discharge_criteria=cp_result.get('discharge_criteria', []),
            estimated_duration=cp_result.get('estimated_duration', ''),
            sustainability_notes=cp_result.get('sustainability_notes', ''),
        )

        print(f"[Orchestrator] Done. Risk: {risk_result.get('risk_level', '?').upper()}")

        return {
            'diagnosis': dx_result,
            'risk': risk_result,
            'treatment': tx_result,
            'care_pathway': cp_result,
        }
