from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import QuizSession, User
from app.schemas import QuizRequest, QuizResult, QuizSubmission
from app.services.quiz import evaluate_submission, generate_quiz_session, get_active_settings, release_images

router = APIRouter()


@router.get("/quiz", response_model=QuizRequest)
def request_quiz(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> QuizRequest:
    active_session = (
        db.query(QuizSession)
        .filter(QuizSession.user_id == user.id, QuizSession.submitted_at.is_(None))
        .first()
    )
    if active_session:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Active session in progress")

    latest_submitted = (
        db.query(QuizSession)
        .filter(QuizSession.user_id == user.id, QuizSession.submitted_at.is_not(None))
        .order_by(QuizSession.created_at.desc())
        .first()
    )
    if latest_submitted and not latest_submitted.passed and not user.can_retake:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Retake not permitted")

    session, question_set = generate_quiz_session(db, user)

    return QuizRequest(
        session_id=session.id,
        questions=[
            {
                "question_id": question["question_id"],
                "options": question["options"],
            }
            for question in question_set
        ],
    )


@router.post("/quiz/submit", response_model=QuizResult)
def submit_quiz(
    payload: QuizSubmission,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuizResult:
    session = db.query(QuizSession).filter(QuizSession.id == payload.session_id).first()
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.submitted_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session already submitted")

    settings = get_active_settings(db)
    score, passed, image_ids = evaluate_submission(session, [answer.dict() for answer in payload.answers], settings.passing_score)

    session.score = score
    session.passed = passed
    session.submitted_at = datetime.utcnow()
    db.add(session)
    db.commit()

    release_images(db, image_ids)

    return QuizResult(session_id=session.id, score=score, passed=passed)
