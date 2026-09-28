import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.aptitude import AptitudeQuestion, AptitudeAttempt, AptitudeAnswer
from backend.models.progress import Progress
from backend.schemas.aptitude import (
    AptitudeQuestionItem,
    AptitudeStartRequest,
    AptitudeSubmitRequest,
    AptitudeAttemptResponse,
    AptitudeReviewItem
)
from backend.services.ai_service import ai_service
from backend.prompts.aptitude_prompts import APTITUDE_GENERATION_PROMPT
from backend.utils.helpers import calculate_aptitude_score

class AptitudeService:
    def __init__(self):
        self.questions_file = settings.DATA_DIR / "aptitude_questions.json"
        self._cached_questions: List[Dict[str, Any]] = []
        self._load_questions()

    def _load_questions(self):
        """Load questions from json file."""
        if self.questions_file.exists():
            with open(self.questions_file, "r", encoding="utf-8") as f:
                self._cached_questions = json.load(f)

    def get_categories(self) -> List[Dict[str, str]]:
        """Return distinct categories available."""
        return [
            {"id": "all", "name": "All Categories", "description": "Comprehensive mix of Quantitative, Logical, Verbal, and DI"},
            {"id": "quantitative", "name": "Quantitative Aptitude", "description": "Numbers, Percentages, Time & Work, Algebra, P&C"},
            {"id": "logical", "name": "Logical Reasoning", "description": "Series, Syllogisms, Blood Relations, Seating Arrangement"},
            {"id": "verbal", "name": "Verbal Ability", "description": "Vocabulary, Grammar, Reading Comprehension, Sentence Correction"},
            {"id": "data_interpretation", "name": "Data Interpretation", "description": "Tables, Bar Charts, Pie Charts, Trend Analysis"}
        ]

    def get_question_by_id(self, question_id: str) -> Optional[Dict[str, Any]]:
        for q in self._cached_questions:
            if q["id"] == question_id:
                return q
        return None

    def start_test(self, req: AptitudeStartRequest) -> List[AptitudeQuestionItem]:
        """Select questions for a test attempt based on category, difficulty, and count."""
        pool = list(self._cached_questions)

        if req.category and req.category != "all":
            pool = [q for q in pool if q.get("category") == req.category]

        if req.difficulty and req.difficulty != "all":
            pool = [q for q in pool if q.get("difficulty") == req.difficulty]

        if not pool:
            pool = list(self._cached_questions)

        # Shuffle and pick num_questions
        selected = random.sample(pool, min(len(pool), req.num_questions))

        # Map to items without correct answer for test taking
        items = []
        for q in selected:
            items.append(AptitudeQuestionItem(
                id=q["id"],
                category=q["category"],
                category_display=q.get("category_display", q["category"].title()),
                difficulty=q["difficulty"],
                question=q["question"],
                options=q["options"],
                time_limit_seconds=60
            ))
        return items

    def submit_test(self, db: Session, user_id: str, req: AptitudeSubmitRequest) -> AptitudeAttemptResponse:
        """Evaluate submitted answers, record attempt and answers in DB, update progress."""
        total_questions = len(req.answers)
        correct_count = 0
        review_items: List[AptitudeReviewItem] = []
        category_stats: Dict[str, Dict[str, int]] = {}

        for ans in req.answers:
            q = self.get_question_by_id(ans.question_id)
            if not q:
                continue

            cat = q.get("category", "general")
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "correct": 0}
            category_stats[cat]["total"] += 1

            correct_ans = q.get("correct_answer", "")
            is_correct = (ans.selected_answer is not None and ans.selected_answer.strip() == correct_ans.strip())

            if is_correct:
                correct_count += 1
                category_stats[cat]["correct"] += 1

            review_items.append(AptitudeReviewItem(
                question_id=q["id"],
                question=q["question"],
                category=cat,
                options=q["options"],
                selected_answer=ans.selected_answer,
                correct_answer=correct_ans,
                is_correct=is_correct,
                explanation=q.get("explanation", "No explanation available."),
                shortcut=q.get("shortcut")
            ))

        score = calculate_aptitude_score(correct_count, total_questions)
        accuracy = round((correct_count / total_questions * 100.0), 1) if total_questions > 0 else 0.0

        # Save Attempt to Database
        attempt = AptitudeAttempt(
            user_id=user_id,
            category=req.category,
            difficulty=req.difficulty,
            total_questions=total_questions,
            correct_answers=correct_count,
            score=score,
            time_taken=req.time_taken
        )
        db.add(attempt)
        db.flush()

        # Save individual answers
        for r in review_items:
            db_answer = AptitudeAnswer(
                attempt_id=attempt.id,
                question_id=r.question_id,
                selected_answer=r.selected_answer,
                is_correct=r.is_correct,
                time_taken=0
            )
            db.add(db_answer)

        # Update User's Aptitude Progress
        progress = db.query(Progress).filter(Progress.user_id == user_id, Progress.skill == "Aptitude").first()
        if not progress:
            progress = Progress(user_id=user_id, skill="Aptitude", score=score)
            db.add(progress)
        else:
            # Exponential moving average / smoothed score
            progress.score = round((progress.score * 0.4) + (score * 0.6), 1)

        db.commit()
        db.refresh(attempt)

        return AptitudeAttemptResponse(
            id=attempt.id,
            user_id=attempt.user_id,
            category=attempt.category,
            difficulty=attempt.difficulty,
            score=attempt.score,
            accuracy=accuracy,
            total_questions=attempt.total_questions,
            correct_answers=attempt.correct_answers,
            incorrect_answers=attempt.total_questions - attempt.correct_answers,
            time_taken=attempt.time_taken,
            created_at=attempt.created_at,
            category_breakdown=category_stats,
            review=review_items
        )

    def get_attempt_result(self, db: Session, attempt_id: str, user_id: str) -> Optional[AptitudeAttemptResponse]:
        """Fetch past attempt with complete review."""
        attempt = db.query(AptitudeAttempt).filter(AptitudeAttempt.id == attempt_id, AptitudeAttempt.user_id == user_id).first()
        if not attempt:
            return None

        answers = db.query(AptitudeAnswer).filter(AptitudeAnswer.attempt_id == attempt_id).all()
        review_items: List[AptitudeReviewItem] = []
        category_stats: Dict[str, Dict[str, int]] = {}

        for ans in answers:
            q = self.get_question_by_id(ans.question_id)
            if not q:
                continue
            cat = q.get("category", "general")
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "correct": 0}
            category_stats[cat]["total"] += 1
            if ans.is_correct:
                category_stats[cat]["correct"] += 1

            review_items.append(AptitudeReviewItem(
                question_id=q["id"],
                question=q["question"],
                category=cat,
                options=q["options"],
                selected_answer=ans.selected_answer,
                correct_answer=q.get("correct_answer", ""),
                is_correct=ans.is_correct,
                explanation=q.get("explanation", ""),
                shortcut=q.get("shortcut")
            ))

        accuracy = round((attempt.correct_answers / attempt.total_questions * 100.0), 1) if attempt.total_questions > 0 else 0.0

        return AptitudeAttemptResponse(
            id=attempt.id,
            user_id=attempt.user_id,
            category=attempt.category,
            difficulty=attempt.difficulty,
            score=attempt.score,
            accuracy=accuracy,
            total_questions=attempt.total_questions,
            correct_answers=attempt.correct_answers,
            incorrect_answers=attempt.total_questions - attempt.correct_answers,
            time_taken=attempt.time_taken,
            created_at=attempt.created_at,
            category_breakdown=category_stats,
            review=review_items
        )

aptitude_service = AptitudeService()
