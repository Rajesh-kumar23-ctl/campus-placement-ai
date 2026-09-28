import json
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.interview import InterviewSession, InterviewQuestion, InterviewAnswer
from backend.models.resume import Resume
from backend.models.progress import Progress
from backend.schemas.interview import (
    InterviewStartRequest,
    InterviewAnswerSubmit,
    InterviewAnswerResponse,
    InterviewSessionResponse
)
from backend.services.ai_service import ai_service
from backend.prompts.interview_prompts import (
    INTERVIEWER_SYSTEM_PROMPT,
    INTERVIEW_QUESTION_GEN_PROMPT,
    INTERVIEW_EVALUATION_PROMPT,
    INTERVIEW_FINAL_REPORT_PROMPT
)
from backend.utils.helpers import calculate_interview_score

class InterviewService:
    def __init__(self):
        self.interview_file = settings.DATA_DIR / "interview_questions.json"
        self.hr_file = settings.DATA_DIR / "hr_questions.json"
        self.tech_file = settings.DATA_DIR / "technical_questions.json"
        self._load_banks()

    def _load_banks(self):
        self._interview_bank = {}
        if self.interview_file.exists():
            with open(self.interview_file, "r", encoding="utf-8") as f:
                self._interview_bank = json.load(f)

        self._hr_bank = []
        if self.hr_file.exists():
            with open(self.hr_file, "r", encoding="utf-8") as f:
                self._hr_bank = json.load(f)

        self._tech_bank = []
        if self.tech_file.exists():
            with open(self.tech_file, "r", encoding="utf-8") as f:
                self._tech_bank = json.load(f)

    def start_interview(self, db: Session, user_id: str, req: InterviewStartRequest) -> Dict[str, Any]:
        """Start a new interview session and initialize Question 1."""
        target_role = req.target_role or "Software Developer"
        if req.interview_type == "cloud_engineer":
            target_role = "Cloud Engineer"

        session = InterviewSession(
            user_id=user_id,
            interview_type=req.interview_type,
            target_role=target_role,
            difficulty=req.difficulty or "medium",
            resume_id=req.resume_id if req.use_resume else None,
            status="active"
        )
        db.add(session)
        db.flush()

        # Generate or pick Question 1
        q1_text, q1_cat, expected = self._get_initial_question(db, session, req)

        question1 = InterviewQuestion(
            session_id=session.id,
            question=q1_text,
            question_number=1,
            category=q1_cat,
            expected_topics=expected
        )
        db.add(question1)
        db.commit()
        db.refresh(session)
        db.refresh(question1)

        total_questions = req.total_questions or 5

        return {
            "session_id": session.id,
            "interview_type": session.interview_type,
            "target_role": session.target_role,
            "difficulty": session.difficulty,
            "total_questions": total_questions,
            "first_question": {
                "question_id": question1.id,
                "question_number": 1,
                "question": question1.question,
                "category": question1.category
            }
        }

    def _get_initial_question(self, db: Session, session: InterviewSession, req: InterviewStartRequest) -> tuple:
        """Determine initial question based on track and resume."""
        if req.use_resume and req.resume_id:
            resume = db.query(Resume).filter(Resume.id == req.resume_id).first()
            if resume and resume.potential_questions:
                return (resume.potential_questions[0], "Resume Overview", resume.skills[:3] if resume.skills else ["Project Architecture"])

        # Track based starter
        track = req.interview_type.lower()
        if track == "cloud_engineer" and "cloud_engineer" in self._interview_bank:
            q = self._interview_bank["cloud_engineer"][0]
            return (q["question"], q.get("category", "Cloud Fundamentals"), q.get("expected_topics", []))
        elif track == "software_developer" and "software_developer" in self._interview_bank:
            q = self._interview_bank["software_developer"][0]
            return (q["question"], q.get("category", "Background & Projects"), q.get("expected_topics", []))
        elif track == "hr" and self._hr_bank:
            q = self._hr_bank[0]
            return (q["question"], q.get("category", "Introduction"), q.get("ideal_points", []))
        elif track == "managerial" and "managerial" in self._interview_bank:
            q = self._interview_bank["managerial"][0]
            return (q["question"], q.get("category", "Project Leadership"), q.get("expected_topics", []))
        elif track == "technical" and "technical" in self._interview_bank:
            q = self._interview_bank["technical"][0]
            return (q["question"], q.get("category", "Introduction"), q.get("expected_topics", []))

        # Default fallback opening question
        return ("Tell me about yourself, your core technical interests, and what motivated you to prepare for this role.", "Introduction", ["Education", "Projects", "Career Motivation"])

    async def submit_answer(self, db: Session, user_id: str, req: InterviewAnswerSubmit) -> InterviewAnswerResponse:
        """
        Evaluate candidate's answer to the current question,
        update session context, adapt difficulty, and generate next question or conclude.
        """
        session = db.query(InterviewSession).filter(InterviewSession.id == req.session_id, InterviewSession.user_id == user_id).first()
        if not session:
            raise ValueError("Interview session not found.")

        current_question = db.query(InterviewQuestion).filter(InterviewQuestion.id == req.question_id).first()
        if not current_question:
            raise ValueError("Interview question not found.")

        # Evaluate Answer
        eval_result = await self._evaluate_answer(current_question, req.answer)

        # Save Answer record
        answer_record = InterviewAnswer(
            question_id=current_question.id,
            answer=req.answer,
            technical_score=eval_result["technical_accuracy"],
            content_score=eval_result["content"],
            relevance_score=eval_result["relevance"],
            clarity_score=eval_result["clarity"],
            communication_score=eval_result["communication"],
            overall_score=eval_result["overall_score"],
            feedback=eval_result["feedback"],
            strengths=eval_result["strengths"],
            improvements=eval_result["improvements"]
        )
        db.add(answer_record)
        db.flush()

        # Check total questions answered so far
        answered_count = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session.id,
            InterviewQuestion.answer != None
        ).count() + 1

        total_target = 5  # default 5 questions per session
        is_last = (answered_count >= total_target)

        next_q_data = None
        if not is_last:
            # Generate next question (adaptively based on answer)
            next_q_data = await self._generate_next_question(
                db=db,
                session=session,
                current_q_num=current_question.question_number + 1,
                total_target=total_target,
                latest_answer=req.answer,
                latest_score=eval_result["overall_score"]
            )

        db.commit()

        return InterviewAnswerResponse(
            answer_id=answer_record.id,
            question_id=current_question.id,
            overall_score=eval_result["overall_score"],
            technical_accuracy=eval_result["technical_accuracy"],
            content=eval_result["content"],
            relevance=eval_result["relevance"],
            clarity=eval_result["clarity"],
            communication=eval_result["communication"],
            feedback=eval_result["feedback"],
            strengths=eval_result["strengths"],
            improvements=eval_result["improvements"],
            is_last_question=is_last,
            next_question=next_q_data
        )

    async def _evaluate_answer(self, question: InterviewQuestion, answer: str) -> Dict[str, Any]:
        """Evaluate answer using LLM or robust heuristic NLP scorer."""
        eval_data = None
        if ai_service.is_configured():
            prompt = INTERVIEW_EVALUATION_PROMPT.format(
                question=question.question,
                category=question.category,
                expected_topics=", ".join(question.expected_topics or []),
                answer=answer
            )
            eval_data = await ai_service.generate_json(prompt)

        if not eval_data:
            words = answer.strip().split()
            word_count = len(words)

            # Heuristic scores 0-10
            # Technical accuracy: keyword overlap with expected topics
            tech_score = 7.0
            if question.expected_topics:
                matches = sum(1 for t in question.expected_topics if t.lower() in answer.lower())
                tech_score = min(9.5, 6.0 + (matches * 1.0))

            content_score = min(9.0, max(5.0, 5.0 + (word_count / 30.0)))
            relevance_score = min(9.0, 7.0 + (0.5 if word_count > 25 else -1.0))
            clarity_score = 7.5
            comm_score = 7.5

            overall = calculate_interview_score(tech_score, content_score, relevance_score, clarity_score, comm_score)

            eval_data = {
                "technical_accuracy": round(tech_score, 1),
                "content": round(content_score, 1),
                "relevance": round(relevance_score, 1),
                "clarity": round(clarity_score, 1),
                "communication": round(comm_score, 1),
                "overall_score": overall,
                "feedback": "Answer demonstrated clear intent and appropriate vocabulary. Incorporating specific system constraints or architectural trade-offs will make your responses even more compelling.",
                "strengths": [
                    "Articulated foundational concepts directly.",
                    "Maintained a professional and structured response cadence."
                ],
                "improvements": [
                    "Support high-level claims with quantitative examples or real project scenarios.",
                    "Address operational edge cases and fault tolerance."
                ]
            }

        overall = eval_data.get("overall_score") or calculate_interview_score(
            eval_data.get("technical_accuracy", 7.0),
            eval_data.get("content", 7.0),
            eval_data.get("relevance", 7.0),
            eval_data.get("clarity", 7.0),
            eval_data.get("communication", 7.0)
        )
        eval_data["overall_score"] = overall
        return eval_data

    async def _generate_next_question(
        self,
        db: Session,
        session: InterviewSession,
        current_q_num: int,
        total_target: int,
        latest_answer: str,
        latest_score: float
    ) -> Dict[str, Any]:
        """Generate or pick next question, adapting difficulty based on score."""
        # Check previous questions in this session
        existing_questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.question_number.asc()).all()
        history_text = "\n".join([f"Q{q.question_number}: {q.question}" for q in existing_questions])

        # Adapt difficulty
        adaptive_difficulty = session.difficulty
        if latest_score >= 80:
            adaptive_difficulty = "hard"
        elif latest_score <= 60:
            adaptive_difficulty = "easy"

        next_q_text = None
        next_cat = "Technical Depth"
        expected_topics = []

        if ai_service.is_configured():
            prompt = INTERVIEW_QUESTION_GEN_PROMPT.format(
                interview_type=session.interview_type,
                target_role=session.target_role,
                question_number=current_q_num,
                total_questions=total_target,
                difficulty=adaptive_difficulty,
                conversation_history=history_text,
                latest_answer=latest_answer
            )
            ai_q = await ai_service.generate_json(prompt)
            if ai_q and "question" in ai_q:
                next_q_text = ai_q["question"]
                next_cat = ai_q.get("category", "Technical")
                expected_topics = ai_q.get("expected_topics", [])

        if not next_q_text:
            # Fallback from question banks
            track = session.interview_type.lower()
            pool = []
            if track in self._interview_bank:
                pool = self._interview_bank[track]
            elif track == "hr":
                pool = self._hr_bank
            elif track == "technical":
                pool = self._tech_bank

            # Exclude already asked questions
            asked_texts = {q.question for q in existing_questions}
            candidates = [q for q in pool if q.get("question") not in asked_texts]

            if candidates:
                # Pick appropriate by difficulty or next in line
                matched = [c for c in candidates if c.get("difficulty") == adaptive_difficulty]
                pick = matched[0] if matched else candidates[0]
                next_q_text = pick["question"]
                next_cat = pick.get("category") or pick.get("topic") or "General"
                expected_topics = pick.get("expected_topics") or pick.get("expected_concepts") or []
            else:
                next_q_text = f"Can you detail a complex challenge you encountered while building a software project and how you resolved it?"
                next_cat = "Problem Solving"

        # Save to database
        new_q = InterviewQuestion(
            session_id=session.id,
            question=next_q_text,
            question_number=current_q_num,
            category=next_cat,
            expected_topics=expected_topics
        )
        db.add(new_q)
        db.flush()

        return {
            "question_id": new_q.id,
            "question_number": new_q.question_number,
            "question": new_q.question,
            "category": new_q.category
        }

    async def end_interview(self, db: Session, user_id: str, session_id: str) -> InterviewSessionResponse:
        """Conclude interview session, calculate overall scores, and generate final comprehensive report."""
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == user_id).first()
        if not session:
            raise ValueError("Interview session not found.")

        questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.question_number.asc()).all()

        answers = [q.answer for q in questions if q.answer is not None]
        if not answers:
            # Empty session fallback
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            db.commit()
            return self.get_session_details(db, session.id, user_id)

        avg_tech = round(sum(a.technical_score for a in answers) / len(answers), 1)
        avg_content = round(sum(a.content_score for a in answers) / len(answers), 1)
        avg_relevance = round(sum(a.relevance_score for a in answers) / len(answers), 1)
        avg_clarity = round(sum(a.clarity_score for a in answers) / len(answers), 1)
        avg_comm = round(sum(a.communication_score for a in answers) / len(answers), 1)

        overall_score = calculate_interview_score(avg_tech, avg_content, avg_relevance, avg_clarity, avg_comm)

        qa_summary_list = []
        for q in questions:
            if q.answer:
                qa_summary_list.append(f"Q: {q.question}\nA: {q.answer.answer}\nScore: {q.answer.overall_score}/100\nFeedback: {q.answer.feedback}")

        qa_summary = "\n\n".join(qa_summary_list)

        report_data = None
        if ai_service.is_configured():
            prompt = INTERVIEW_FINAL_REPORT_PROMPT.format(
                interview_type=session.interview_type,
                target_role=session.target_role,
                qa_summary=qa_summary,
                avg_technical=avg_tech,
                avg_content=avg_content,
                avg_relevance=avg_relevance,
                avg_clarity=avg_clarity,
                avg_communication=avg_comm,
                overall_score=overall_score
            )
            report_data = await ai_service.generate_json(prompt)

        if not report_data:
            strengths = [
                "Demonstrated solid conceptual foundation across primary interview topics.",
                "Maintained structured clarity and articulated responses methodically.",
                "Adapted well to follow-up questions and conversational progression."
            ]
            improvements = [
                "Incorporate deeper architectural trade-offs (e.g. latency vs consistency, cost vs scale).",
                "Be more precise with industry-standard terminology when describing system components.",
                "Practice active listening to cover all sub-parts of multi-layered questions."
            ]
            recommended_practice = [
                f"Review advanced concepts in {session.target_role} preparation.",
                "Conduct 2 additional mock sessions focusing on edge-case scenarios.",
                "Practice timed answer structuring using the STAR framework."
            ]
            topics_to_revise = [
                "System design fundamentals & database indexing",
                "Cloud networking, security policies, and concurrency models",
                "Behavioral alignment and situational storytelling"
            ]
            summary_assessment = (
                f"Candidate achieved an overall readiness score of {overall_score}%. "
                f"Communication and core conceptual understanding are strong. Focusing on deeper technical edge cases will position the candidate in the top percentile."
            )
            report_data = {
                "overall_score": overall_score,
                "summary_assessment": summary_assessment,
                "strengths": strengths,
                "areas_to_improve": improvements,
                "recommended_practice": recommended_practice,
                "topics_to_revise": topics_to_revise
            }

        session.score = overall_score
        session.status = "completed"
        session.feedback = report_data.get("summary_assessment", "")
        session.strengths = report_data.get("strengths", [])
        session.improvements = report_data.get("areas_to_improve", [])
        session.topics_to_revise = report_data.get("topics_to_revise", [])
        session.completed_at = datetime.utcnow()

        # Update Progress records
        skill_name = "Technical" if session.interview_type in ["technical", "cloud_engineer", "software_developer"] else "HR"
        p_tech = db.query(Progress).filter(Progress.user_id == user_id, Progress.skill == skill_name).first()
        if not p_tech:
            p_tech = Progress(user_id=user_id, skill=skill_name, score=overall_score)
            db.add(p_tech)
        else:
            p_tech.score = round((p_tech.score * 0.4) + (overall_score * 0.6), 1)

        p_comm = db.query(Progress).filter(Progress.user_id == user_id, Progress.skill == "Communication").first()
        comm_val = round(avg_comm * 10.0, 1)
        if not p_comm:
            p_comm = Progress(user_id=user_id, skill="Communication", score=comm_val)
            db.add(p_comm)
        else:
            p_comm.score = round((p_comm.score * 0.4) + (comm_val * 0.6), 1)

        db.commit()
        db.refresh(session)

        return self.get_session_details(db, session.id, user_id)

    def get_session_details(self, db: Session, session_id: str, user_id: str) -> Optional[InterviewSessionResponse]:
        """Fetch full interview session with all questions, answers, and scores."""
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == user_id).first()
        if not session:
            return None

        questions = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.question_number.asc()).all()

        q_list = []
        tech_scores, content_scores, rel_scores, clar_scores, comm_scores = [], [], [], [], []

        for q in questions:
            item = {
                "question_id": q.id,
                "question_number": q.question_number,
                "question": q.question,
                "category": q.category,
                "answer": None
            }
            if q.answer:
                ans = q.answer
                item["answer"] = {
                    "answer_id": ans.id,
                    "answer": ans.answer,
                    "overall_score": ans.overall_score,
                    "technical_score": ans.technical_score,
                    "content_score": ans.content_score,
                    "relevance_score": ans.relevance_score,
                    "clarity_score": ans.clarity_score,
                    "communication_score": ans.communication_score,
                    "feedback": ans.feedback,
                    "strengths": ans.strengths,
                    "improvements": ans.improvements
                }
                tech_scores.append(ans.technical_score)
                content_scores.append(ans.content_score)
                rel_scores.append(ans.relevance_score)
                clar_scores.append(ans.clarity_score)
                comm_scores.append(ans.communication_score)
            q_list.append(item)

        avg_tech = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else 0.0
        avg_content = round(sum(content_scores) / len(content_scores), 1) if content_scores else 0.0
        avg_rel = round(sum(rel_scores) / len(rel_scores), 1) if rel_scores else 0.0
        avg_clar = round(sum(clar_scores) / len(clar_scores), 1) if clar_scores else 0.0
        avg_comm = round(sum(comm_scores) / len(comm_scores), 1) if comm_scores else 0.0

        return InterviewSessionResponse(
            id=session.id,
            interview_type=session.interview_type,
            target_role=session.target_role,
            difficulty=session.difficulty,
            status=session.status,
            score=session.score,
            technical_accuracy=avg_tech,
            content=avg_content,
            relevance=avg_rel,
            clarity=avg_clar,
            communication=avg_comm,
            strengths=session.strengths or [],
            improvements=session.improvements or [],
            topics_to_revise=session.topics_to_revise or [],
            feedback=session.feedback,
            created_at=session.created_at,
            completed_at=session.completed_at,
            questions=q_list
        )

interview_service = InterviewService()
