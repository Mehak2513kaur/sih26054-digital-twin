from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os
import time
from backend.engine_service import EngineService
from backend.database.connection import SessionLocal
from backend.database.models import MissionRecord, AlertRecord

router = APIRouter()
service = EngineService()

@router.get("/report/{mission_id}")
def get_report_json(mission_id: str):
    db = SessionLocal()
    mission = db.query(MissionRecord).filter(MissionRecord.mission_id == mission_id).first()
    alerts = db.query(AlertRecord).filter(AlertRecord.mission_id == mission_id).all()
    db.close()

    curr = service.mission_controller.get_summary()
    if not mission:
        # Generate on-the-fly report from current session
        return {
            "mission_id": mission_id,
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scenario": curr["scenario_name"],
            "duration_seconds": curr["elapsed_time"],
            "engine_id": service.engine.engine_id,
            "engine_hours": round(service.engine.engine_hours, 1),
            "peak_temperature": curr["peak_temp"],
            "max_vibration": curr["max_vibration"],
            "min_oil_pressure": curr["min_oil_pressure"],
            "final_health_score": curr["final_health"],
            "final_rul_hours": curr["final_rul"],
            "faults_detected": curr["faults_observed"],
            "ai_findings": service.latest_full_state.get("ml_prediction", {}).get("explainability", {}).get("diagnostic_narrative", []),
            "recommended_maintenance": service.latest_full_state.get("recommendation", {}).get("recommended_action", "Nominal inspection."),
            "disclaimer": "Simulated prototype mission debrief report for DRDO Problem Statement 26054."
        }

    return {
        "mission_id": mission.mission_id,
        "date": mission.created_at.strftime("%Y-%m-%d %H:%M:%S") if mission.created_at else "",
        "scenario": mission.scenario_name,
        "duration_seconds": mission.duration_seconds,
        "engine_id": service.engine.engine_id,
        "engine_hours": round(service.engine.engine_hours, 1),
        "peak_temperature": mission.peak_temp,
        "max_vibration": mission.max_vibration,
        "min_oil_pressure": mission.min_oil_pressure,
        "final_health_score": mission.final_health,
        "final_rul_hours": mission.final_rul,
        "faults_detected": mission.faults_logged.split(",") if mission.faults_logged else [],
        "ai_findings": [f"Recorded peak temperature of {mission.peak_temp}°C.", f"Peak vibration observed: {mission.max_vibration} mm/s."],
        "recommended_maintenance": "Review telemetry replay and complete scheduled oil and cylinder borescope inspection.",
        "disclaimer": "Simulated prototype mission debrief report for DRDO Problem Statement 26054."
    }

@router.get("/report/{mission_id}/pdf")
def generate_report_pdf(mission_id: str):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors

    root = Path(__file__).resolve().parent.parent.parent
    reports_dir = root / "reports"
    os.makedirs(reports_dir, exist_ok=True)
    pdf_path = reports_dir / f"Mission_Debrief_{mission_id}.pdf"

    curr = service.mission_controller.get_summary()
    pred = service.latest_full_state.get("ml_prediction", {})
    rec = service.latest_full_state.get("recommendation", {})
    residuals = service.latest_full_state.get("residuals", {})
    xai = pred.get("explainability", {})

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # Top Security Classification Banner
    c.setFillColor(colors.HexColor("#dc2626"))
    c.rect(0, height - 24, width, 24, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(width / 2.0, height - 16, "CLASSIFICATION: SIMULATION / DEMONSTRATION DATA - NOT OPERATIONAL FLIGHT")

    # Header Banner (Aerospace Navy)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.rect(0, height - 110, width, 86, stroke=0, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 55, "DRDO PS 26054: MALE UAV ENGINE DIGITAL TWIN")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 75, f"MISSION DEBRIEF & PROGNOSTIC HEALTH DOSSIER | MISSION ID: {mission_id}")
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(40, height - 92, "Powertrain: 4-Cylinder Turbocharged Aircraft Piston (Rotax 914/915 iS class)")

    # 1. Mission Metadata section
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, height - 135, "1. MISSION OPERATIONAL PROFILE")
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setLineWidth(0.5)
    c.line(40, height - 139, width - 40, height - 139)

    c.setFont("Helvetica", 9)
    c.drawString(50, height - 155, f"Engine Identifier: {service.engine.engine_id}")
    c.drawString(250, height - 155, f"Cumulative Engine Hours: {service.engine.engine_hours:.1f} h")
    c.drawString(50, height - 170, f"Flight Scenario: {curr['scenario_name']}")
    c.drawString(250, height - 170, f"Mission Duration: {curr['elapsed_time']:.1f} seconds")

    # 2. Digital Twin Observed vs Expected Residuals
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, height - 200, "2. DIGITAL TWIN RESIDUAL ANALYSIS (OBSERVED vs VIRTUAL)")
    c.line(40, height - 204, width - 40, height - 204)

    # Table Header
    c.setFillColor(colors.HexColor("#f1f5f9"))
    c.rect(40, height - 225, width - 80, 16, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#1e293b"))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(45, height - 220, "PARAMETER")
    c.drawString(170, height - 220, "OBSERVED")
    c.drawString(250, height - 220, "EXPECTED")
    c.drawString(340, height - 220, "RESIDUAL")
    c.drawString(430, height - 220, "Z-SCORE")
    c.drawString(495, height - 220, "STATUS")

    params = residuals.get("parameters", {})
    cht_p = params.get("cht", {})
    oil_p = params.get("oil_pressure", {})
    vib_p = params.get("vibration", {})
    egt_p = params.get("egt", {})

    rows = [
        ("Cylinder Head Temp (CHT)", f"{curr['peak_temp']:.1f} deg C", f"{cht_p.get('expected', 96.5):.1f} deg C", f"{cht_p.get('residual', 0.0):+.1f} deg C", f"{cht_p.get('z_score', 0.0):+.1f}\u03c3", cht_p.get('status', 'ALIGNED')),
        ("Hydraulic Oil Pressure", f"{curr['min_oil_pressure']:.2f} bar", f"{oil_p.get('expected', 4.10):.2f} bar", f"{oil_p.get('residual', 0.0):+.2f} bar", f"{oil_p.get('z_score', 0.0):+.1f}\u03c3", oil_p.get('status', 'ALIGNED')),
        ("Mechanical RMS Vibration", f"{curr['max_vibration']:.2f} mm/s", f"{vib_p.get('expected', 1.65):.2f} mm/s", f"{vib_p.get('residual', 0.0):+.2f} mm/s", f"{vib_p.get('z_score', 0.0):+.1f}\u03c3", vib_p.get('status', 'ALIGNED')),
        ("Exhaust Gas Temp (EGT)", f"{service.latest_full_state.get('telemetry', {}).get('exhaust_gas_temp', 760.0):.1f} deg C", f"{egt_p.get('expected', 760.0):.1f} deg C", f"{egt_p.get('residual', 0.0):+.1f} deg C", f"{egt_p.get('z_score', 0.0):+.1f}\u03c3", egt_p.get('status', 'ALIGNED'))
    ]

    y = height - 240
    c.setFont("Helvetica", 8)
    for p_name, obs, exp, res_val, z_val, stat in rows:
        c.setFillColor(colors.black)
        c.drawString(45, y, p_name)
        c.drawString(170, y, obs)
        c.drawString(250, y, exp)
        c.drawString(340, y, res_val)
        c.drawString(430, y, z_val)
        if stat == "DIVERGENT":
            c.setFillColor(colors.HexColor("#dc2626"))
        elif stat == "WARNING":
            c.setFillColor(colors.HexColor("#d97706"))
        else:
            c.setFillColor(colors.HexColor("#16a34a"))
        c.drawString(495, y, stat)
        y -= 14

    # 3. AI Prognostics & Explainability
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 15, "3. AI DIAGNOSTICS & EXPLAINABLE AI (XAI) ATTRIBUTION")
    c.line(40, y - 19, width - 40, y - 19)

    c.setFont("Helvetica", 9)
    pred_fault = pred.get("predicted_fault", "NORMAL")
    conf = pred.get("confidence", 95.0)
    rul = pred.get("rul", {}).get("rul_hours", curr['final_rul'])
    deg_idx = pred.get("rul", {}).get("degradation_index", 12.0)
    deg_vel = pred.get("rul", {}).get("degradation_velocity", 0.35)

    c.drawString(50, y - 35, f"Diagnosed Fault Mode: {pred_fault} (Confidence: {conf:.1f}%)")
    c.drawString(310, y - 35, f"Composite Health Score: {curr['final_health']:.1f}%")
    c.drawString(50, y - 50, f"Remaining Useful Life (Simulated): {rul:.1f} hours")
    c.drawString(310, y - 50, f"Degradation Index: {deg_idx:.1f}/100 | Velocity: {deg_vel:.2f}%/hr")

    narrative = xai.get("diagnostic_narrative", ["Physics residuals match theoretical equilibrium envelope."])
    ny = y - 70
    c.setFont("Helvetica", 8.5)
    for line_text in narrative[:3]:
        c.drawString(60, ny, f"- {line_text}")
        ny -= 13

    # 4. Actionable Defense Maintenance Directive
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, ny - 15, "4. ACTIONABLE DEFENSE MAINTENANCE DIRECTIVE")
    c.line(40, ny - 19, width - 40, ny - 19)

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#0f172a"))
    action_title = rec.get("title", "Nominal Flight Readiness")
    action_directive = rec.get("recommended_action", "Maintain standard pre-flight and 50-hour scheduled inspection envelope.")
    c.drawString(50, ny - 35, f"Directive: {action_title}")
    
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.HexColor("#334155"))
    c.drawString(50, ny - 50, action_directive[:105])
    if len(action_directive) > 105:
        c.drawString(50, ny - 64, action_directive[105:210])

    # Bottom Classification & Legal Footer
    c.setFillColor(colors.HexColor("#dc2626"))
    c.rect(0, 0, width, 24, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(width / 2.0, 8, "CLASSIFICATION: SIMULATION / DEMONSTRATION DATA - NOT FOR PHYSICAL AIRCRAFT USE")

    c.save()
    return FileResponse(path=str(pdf_path), filename=f"Mission_Debrief_{mission_id}.pdf", media_type="application/pdf")
