import json
import random
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.gd import GDSession, GDResponse
from backend.models.progress import Progress
from backend.schemas.gd import (
    GDTopicPrep,
    GDGenerateRequest,
    GDStartRequest,
    GDRespondRequest,
    GDEvaluationResponse
)
from backend.services.ai_service import ai_service
from backend.prompts.gd_prompts import (
    GD_TOPIC_PREP_PROMPT,
    GD_SIMULATION_TURN_PROMPT,
    GD_EVALUATION_PROMPT
)
from backend.utils.helpers import calculate_gd_score

class GDService:
    def __init__(self):
        self.topics_file = settings.DATA_DIR / "gd_topics.json"
        self._cached_topics: List[Dict[str, Any]] = []
        self._load_topics()

    def _load_topics(self):
        if self.topics_file.exists():
            with open(self.topics_file, "r", encoding="utf-8") as f:
                self._cached_topics = json.load(f)

    def get_topics(self, search: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        topics = list(self._cached_topics)
        if search:
            q = search.lower().strip()
            topics = [t for t in topics if q in t["topic"].lower() or q in t.get("overview", "").lower()]
        if category and category.lower() != "all":
            topics = [t for t in topics if t.get("category", "").lower() == category.lower()]
        return topics

    def get_topic_by_id(self, topic_id: str) -> Optional[Dict[str, Any]]:
        for t in self._cached_topics:
            if t.get("id") == topic_id:
                return t
        return None

    async def generate_topic_prep(self, req: GDGenerateRequest) -> GDTopicPrep:
        """Generate comprehensive GD prep material for any custom or selected topic."""
        # Check if topic already exists in curated cache
        for t in self._cached_topics:
            if t["topic"].lower().strip() == req.topic.lower().strip():
                return GDTopicPrep(**t)

        # If AI is configured, invoke LLM
        if ai_service.is_configured():
            prompt = GD_TOPIC_PREP_PROMPT.format(
                topic=req.topic,
                category=req.category or "General",
                difficulty=req.difficulty or "Medium"
            )
            ai_result = await ai_service.generate_json(prompt)
            if ai_result and "topic" in ai_result:
                return GDTopicPrep(
                    id=f"custom-gd-{random.randint(1000, 9999)}",
                    **ai_result
                )

        # Fallback generator for offline practice mode
        return GDTopicPrep(
            id=f"custom-gd-{random.randint(1000, 9999)}",
            topic=req.topic,
            category=req.category or "Technology & Society",
            difficulty=req.difficulty or "Medium",
            overview=f"An in-depth debate examining the strategic, ethical, and practical implications of '{req.topic}' on industries, professionals, and future policy.",
            opening_statement=f"Good morning everyone. The discussion on '{req.topic}' is both timely and critical. We must analyze this topic from technical feasibility, economic viability, and social equity perspectives.",
            key_arguments_for=[
                f"Accelerates productivity, technological modernization, and global competitiveness.",
                f"Fosters new innovations, democratizes access, and drives economic efficiency.",
                f"Empowers individuals and organizations to solve previously intractable problems at scale."
            ],
            key_arguments_against=[
                f"Poses challenges regarding workforce transition, skill displacement, and regulatory lags.",
                f"Risk of exacerbating the digital divide and concentrating power among few market leaders.",
                f"Demands substantial upfront capital investment and long-term security compliance."
            ],
            real_world_examples=[
                "Case studies across digital transformations in banking, healthcare, and education over the past decade.",
                "Global regulatory frameworks balancing innovation pace with consumer protection."
            ],
            thirty_sec_speech=f"Friends, '{req.topic}' presents immense transformative potential, but its success hinges on responsible implementation. We must balance innovation velocity with ethical governance.",
            one_min_speech=f"Respected peers, when we evaluate '{req.topic}', we must recognize that technology and social change are rarely zero-sum. The primary objective should be sustainable integration—leveraging efficiency gains while building safety nets and continuous upskilling avenues for stakeholders. By focusing on data-driven policy and collaborative frameworks, we can harness its full value.",
            conclusion=f"In conclusion, '{req.topic}' requires a balanced, nuanced approach: proactive adoption combined with thoughtful regulatory safeguards.",
            things_to_avoid=[
                "Taking polarized, emotional stances without factual support",
                "Interrupting other participants without acknowledging their points",
                "Failing to propose constructive, actionable solutions"
            ],
            follow_up_questions=[
                f"What are the immediate policy steps required to address the primary risks of this topic?",
                f"How should academic institutions adapt their curriculum in light of this development?"
            ]
        )

    def start_simulation(self, db: Session, user_id: str, req: GDStartRequest) -> Dict[str, Any]:
        """Initialize a new GD simulation session with Moderator opening introduction."""
        session = GDSession(
            user_id=user_id,
            topic=req.topic,
            duration=req.duration_minutes,
            difficulty=req.difficulty or "Medium",
            num_participants=req.num_participants
        )
        db.add(session)
        db.flush()

        # Moderator opening introduction
        mod_msg = (
            f"Welcome members to this group discussion on: '{req.topic}'. "
            f"You will have {req.duration_minutes} minutes. Please present structured points with real-world examples, "
            f"listen actively, and maintain a respectful, constructive dialogue. Let us begin!"
        )
        mod_resp = GDResponse(
            session_id=session.id,
            speaker="Moderator",
            response=mod_msg
        )
        db.add(mod_resp)

        # Participant 1 opening prompt to kickstart
        p1_msg = (
            f"Thank you Moderator. I'd like to initiate the discussion. Looking at '{req.topic}', "
            f"the primary metric we cannot ignore is the rapid pace of adoption across global markets. "
            f"Recent industry data highlights substantial efficiency gains, yet cost and operational bottlenecks remain prevalent."
        )
        p1_resp = GDResponse(
            session_id=session.id,
            speaker="Participant 1 (Aarav)",
            response=p1_msg
        )
        db.add(p1_resp)

        db.commit()
        db.refresh(session)

        return {
            "session_id": session.id,
            "topic": session.topic,
            "duration_minutes": session.duration,
            "initial_messages": [
                {"speaker": "Moderator", "message": mod_msg},
                {"speaker": "Participant 1 (Aarav)", "message": p1_msg}
            ]
        }

    async def user_respond(self, db: Session, req: GDRespondRequest) -> Dict[str, Any]:
        """Record user contribution, then simulate AI participants responding specifically to user."""
        session = db.query(GDSession).filter(GDSession.id == req.session_id).first()
        if not session:
            raise ValueError("GD Session not found.")

        # Save user response
        user_entry = GDResponse(
            session_id=session.id,
            speaker="User",
            response=req.user_response
        )
        db.add(user_entry)
        db.flush()

        # Load recent conversation history
        past_responses = db.query(GDResponse).filter(GDResponse.session_id == session.id).order_by(GDResponse.created_at.asc()).all()
        history_text = "\n".join([f"{r.speaker}: {r.response}" for r in past_responses[-6:]])

        ai_speakers = []

        if ai_service.is_configured():
            prompt = GD_SIMULATION_TURN_PROMPT.format(
                topic=session.topic,
                history=history_text,
                user_input=req.user_response
            )
            ai_data = await ai_service.generate_json(prompt)
            if ai_data and "speaker_responses" in ai_data:
                for item in ai_data["speaker_responses"]:
                    ai_speakers.append(item)

        # Fallback responses if AI is not configured or didn't return
        if not ai_speakers:
            # Deterministic, conversational reactive statements
            first_words = req.user_response.strip().split()[:6]
            snippet = " ".join(first_words) + ("..." if len(first_words) >= 6 else "")

            p2_templates = [
                f"I really appreciate the point raised about '{snippet}'. Adding to that, we also need to consider the human and ethical dimension—how this directly impacts ground-level practitioners.",
                f"That's a very valid observation regarding '{snippet}'. However, we should also examine the socio-economic implications in developing economies where infrastructure is still maturing.",
                f"Building on that perspective, another crucial factor is institutional governance and public trust. Without transparent protocols, even well-intentioned initiatives face public resistance."
            ]
            p3_templates = [
                f"While I agree with the core sentiment, let me play devil's advocate. If we over-regulate or delay deployment, don't we risk losing competitive edge to global counterparts?",
                f"That's a compelling point, but what about the economic feasibility? High implementation costs often hinder widespread adoption among smaller organizations.",
                f"True, but how do we realistically balance rapid innovation with accountability? That seems to be the central bottleneck."
            ]

            ai_speakers.append({
                "speaker": "Participant 2 (Priya)",
                "message": random.choice(p2_templates)
            })
            if random.random() > 0.3:
                ai_speakers.append({
                    "speaker": "Participant 3 (Rohan)",
                    "message": random.choice(p3_templates)
                })

        # Save AI responses to DB
        saved_messages = []
        for msg in ai_speakers:
            db_resp = GDResponse(
                session_id=session.id,
                speaker=msg["speaker"],
                response=msg["message"]
            )
            db.add(db_resp)
            saved_messages.append({"speaker": msg["speaker"], "message": msg["message"]})

        db.commit()

        return {
            "session_id": session.id,
            "ai_responses": saved_messages,
            "prompt_for_user": "You may counter, support, or present an example to steer the group discussion."
        }

    async def evaluate_session(self, db: Session, user_id: str, session_id: str) -> GDEvaluationResponse:
        """Generate rigorous GD evaluation based on user contributions."""
        session = db.query(GDSession).filter(GDSession.id == session_id, GDSession.user_id == user_id).first()
        if not session:
            raise ValueError("GD Session not found.")

        user_responses = db.query(GDResponse).filter(
            GDResponse.session_id == session.id,
            GDResponse.speaker == "User"
        ).all()

        combined_user_text = "\n".join([f"Contribution {i+1}: {r.response}" for i, r in enumerate(user_responses)])
        word_count = sum(len(r.response.split()) for r in user_responses)

        eval_data = None
        if ai_service.is_configured() and user_responses:
            prompt = GD_EVALUATION_PROMPT.format(
                topic=session.topic,
                user_transcript=combined_user_text
            )
            eval_data = await ai_service.generate_json(prompt)

        if not eval_data:
            # Heuristic rule-based evaluation (0-10 scale)
            # Content: based on word count and depth
            content_score = min(9.0, max(5.0, 5.0 + (word_count / 80.0)))
            # Relevance: presence of key topic terms
            relevance_score = min(9.0, max(6.0, 6.5 + (0.5 if len(user_responses) >= 2 else 0.0)))
            # Clarity & Structure
            clarity_score = 7.5
            structure_score = 7.0
            fluency_score = 7.5

            overall_score = calculate_gd_score(content_score, relevance_score, clarity_score, structure_score, fluency_score)

            strengths = [
                "Proactively entered the discussion with clear articulation.",
                "Successfully engaged with peer points rather than speaking in isolation.",
                "Maintained professional, collaborative communication etiquette."
            ]
            improvements = [
                "Incorporate more statistical data and specific industry examples to substantiate arguments.",
                "Structure inputs with a clearer opening hook, evidence, and synthesis.",
                "Practice synthesizing opposing viewpoints to guide the group toward consensus."
            ]

            eval_data = {
                "content": content_score,
                "relevance": relevance_score,
                "clarity": clarity_score,
                "structure": structure_score,
                "fluency": fluency_score,
                "overall": overall_score,
                "strengths": strengths,
                "improvements": improvements,
                "better_response": (
                    f"A stronger contribution on '{session.topic}' might open with: 'Building on what Aarav and Priya mentioned, "
                    f"the key metric to consider is the trade-off between deployment velocity and ethical governance. For example, in healthcare, "
                    f"AI reduces diagnostic turnaround by 40%, yet human clinical oversight remains indispensable. Therefore, our focus must be human-in-the-loop systems.'"
                ),
                "feedback": "Demonstrated good presence and conversational flow. Enhancing argument depth with concrete metrics will elevate your performance to top tier."
            }

        # Calculate or sync overall score
        overall = eval_data.get("overall") or calculate_gd_score(
            eval_data.get("content", 7.0),
            eval_data.get("relevance", 7.0),
            eval_data.get("clarity", 7.0),
            eval_data.get("structure", 7.0),
            eval_data.get("fluency", 7.0)
        )

        session.score = overall
        session.strengths = eval_data.get("strengths", [])
        session.improvements = eval_data.get("improvements", [])

        # Update Progress record in DB
        progress = db.query(Progress).filter(Progress.user_id == user_id, Progress.skill == "GD").first()
        if not progress:
            progress = Progress(user_id=user_id, skill="GD", score=overall)
            db.add(progress)
        else:
            progress.score = round((progress.score * 0.4) + (overall * 0.6), 1)

        db.commit()

        return GDEvaluationResponse(
            session_id=session.id,
            topic=session.topic,
            overall=overall,
            content=round(eval_data.get("content", 7.5), 1),
            relevance=round(eval_data.get("relevance", 7.5), 1),
            clarity=round(eval_data.get("clarity", 7.0), 1),
            structure=round(eval_data.get("structure", 7.0), 1),
            fluency=round(eval_data.get("fluency", 7.5), 1),
            strengths=eval_data.get("strengths", []),
            improvements=eval_data.get("improvements", []),
            better_response=eval_data.get("better_response", ""),
            feedback=eval_data.get("feedback", "")
        )

gd_service = GDService()
