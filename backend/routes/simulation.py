from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any

from backend.database.database import get_db
from backend.models.user import User
from backend.models.simulation import PlacementSimulation
from backend.schemas.simulation import (
    SimulationStartRequest,
    SimulationRoundCompleteRequest,
    SimulationFinalReportRequest,
    SimulationReportResponse
)
from backend.dependencies import get_current_user
from backend.utils.helpers import calculate_readiness_score

router = APIRouter(prefix="/api/simulation", tags=["Placement Simulation"])

@router.post("/start", response_model=Dict[str, Any])
def start_simulation(
    req: SimulationStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a full 4-round placement simulation (Aptitude -> GD -> Technical -> HR -> Report)."""
    sim = PlacementSimulation(
        user_id=current_user.id,
        target_role=req.target_role or current_user.target_role or "Software Developer",
        status="in_progress",
        current_round="aptitude",
        round_details={"company_focus": req.company_focus or "General Tech Drive"}
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)

    return {
        "simulation_id": sim.id,
        "current_round": sim.current_round,
        "target_role": sim.target_role,
        "rounds_sequence": ["aptitude", "gd", "technical", "hr"],
        "message": "Placement simulation initiated. Welcome to Round 1: Aptitude Screening."
    }

@router.post("/complete-round", response_model=Dict[str, Any])
def complete_round(
    req: SimulationRoundCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record score for completed round and advance to the next round."""
    sim = db.query(PlacementSimulation).filter(
        PlacementSimulation.id == req.simulation_id,
        PlacementSimulation.user_id == current_user.id
    ).first()

    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found.")

    round_type = req.round_type.lower()
    details = dict(sim.round_details or {})

    if round_type == "aptitude":
        sim.aptitude_score = req.round_score
        sim.current_round = "gd"
        details["aptitude"] = req.round_data or {"score": req.round_score}
        next_msg = "Round 1 passed. Proceeding to Round 2: Group Discussion."
    elif round_type == "gd":
        sim.gd_score = req.round_score
        sim.current_round = "technical"
        details["gd"] = req.round_data or {"score": req.round_score}
        next_msg = "Round 2 completed. Proceeding to Round 3: Technical Interview."
    elif round_type == "technical":
        sim.technical_score = req.round_score
        sim.current_round = "hr"
        details["technical"] = req.round_data or {"score": req.round_score}
        next_msg = "Round 3 completed. Proceeding to Final Round: HR & Managerial."
    elif round_type == "hr":
        sim.hr_score = req.round_score
        sim.communication_score = req.round_data.get("communication", req.round_score * 0.9) if req.round_data else req.round_score
        sim.current_round = "completed"
        sim.status = "completed"
        sim.completed_at = datetime.utcnow()
        details["hr"] = req.round_data or {"score": req.round_score}

        # Calculate final overall weighted score
        overall = calculate_readiness_score(
            sim.aptitude_score,
            sim.gd_score,
            sim.technical_score,
            sim.hr_score,
            sim.communication_score
        )
        sim.overall_score = overall

        # Diagnostic strengths & weaknesses
        strengths = []
        weaknesses = []
        recommendations = []

        if sim.aptitude_score >= 75:
            strengths.append(f"Strong quantitative and logical reasoning baseline ({sim.aptitude_score}%).")
        else:
            weaknesses.append(f"Aptitude accuracy under timed conditions ({sim.aptitude_score}%).")
            recommendations.append("Dedicate 20 minutes daily to speed-math and logical series practice.")

        if sim.gd_score >= 70:
            strengths.append(f"Confident articulation and constructive collaboration in GD ({sim.gd_score}%).")
        else:
            weaknesses.append(f"Substantiating arguments with facts during group discussions ({sim.gd_score}%).")
            recommendations.append("Practice 30-second structured speech hooks using real-world case studies.")

        if sim.technical_score >= 75:
            strengths.append(f"Clear architectural depth and problem-solving in technical interview ({sim.technical_score}%).")
        else:
            weaknesses.append(f"Addressing system trade-offs and edge cases ({sim.technical_score}%).")
            recommendations.append("Review core CS fundamentals (indexing, concurrency, cloud VPCs).")

        if sim.hr_score >= 75:
            strengths.append(f"Professional composure, adaptability, and culture alignment ({sim.hr_score}%).")
        else:
            weaknesses.append(f"Structuring situational behavioral examples ({sim.hr_score}%).")
            recommendations.append("Prepare STAR framework narratives for team conflicts and project leadership.")

        sim.strengths = strengths or ["Consistent preparation across core domains."]
        sim.weak_areas = weaknesses or ["Refining delivery under high-pressure scenarios."]
        sim.recommendations = recommendations or ["Continue practicing company-specific mock rounds."]
        sim.summary_report = (
            f"Candidate completed the complete 4-round placement simulation for {sim.target_role} "
            f"with an overall preparation performance score of {overall}%. "
            f"Aptitude: {sim.aptitude_score}%, GD: {sim.gd_score}%, Technical: {sim.technical_score}%, HR: {sim.hr_score}%."
        )
        next_msg = "All 4 rounds completed successfully! Your comprehensive placement report is ready."
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown round type: {round_type}")

    sim.round_details = details
    db.commit()
    db.refresh(sim)

    return {
        "simulation_id": sim.id,
        "current_round": sim.current_round,
        "status": sim.status,
        "message": next_msg,
        "is_finished": (sim.status == "completed")
    }

@router.post("/final-report", response_model=SimulationReportResponse)
def generate_or_get_final_report(
    req: SimulationFinalReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve or finalize placement simulation report."""
    sim = db.query(PlacementSimulation).filter(
        PlacementSimulation.id == req.simulation_id,
        PlacementSimulation.user_id == current_user.id
    ).first()

    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found.")

    return SimulationReportResponse.model_validate(sim)

@router.get("/{simulation_id}", response_model=SimulationReportResponse)
def get_simulation_report(
    simulation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full simulation scorecard and final report."""
    sim = db.query(PlacementSimulation).filter(
        PlacementSimulation.id == simulation_id,
        PlacementSimulation.user_id == current_user.id
    ).first()

    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found.")

    return SimulationReportResponse.model_validate(sim)
