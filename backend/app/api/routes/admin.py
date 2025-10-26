import csv
import io
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models import Image, QuizSession, Setting, User
from app.schemas import ImageCreate, ImageRead, SessionResult, SettingRead, SettingUpdate

router = APIRouter()


@router.get("/settings", response_model=SettingRead)
def get_settings(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> SettingRead:  # noqa: ARG001
    setting = db.query(Setting).first()
    if setting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not configured")
    return setting


@router.post("/settings", response_model=SettingRead)
def update_settings(
    payload: SettingUpdate,
    admin: User = Depends(require_admin),  # noqa: ARG001
    db: Session = Depends(get_db),
) -> SettingRead:
    setting = db.query(Setting).first()
    if setting is None:
        setting = Setting()
        db.add(setting)
    setting.passing_score = payload.passing_score
    setting.num_questions = payload.num_questions
    setting.num_options = payload.num_options
    db.commit()
    db.refresh(setting)
    return setting


@router.post("/images", response_model=List[ImageRead])
def upload_images(
    images: List[ImageCreate],
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> List[ImageRead]:
    stored_images: List[Image] = []
    for image in images:
        stored = Image(file_url=str(image.file_url), type=image.type, uploaded_by=admin.id)
        db.add(stored)
        stored_images.append(stored)
    db.commit()
    for image in stored_images:
        db.refresh(image)
    return stored_images


@router.post("/images/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_image_usage(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> Response:  # noqa: ARG001
    db.query(Image).update({Image.used_in_session: False})
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/results", response_model=List[SessionResult])
def list_results(
    status_filter: Optional[str] = Query(None, description="Filter by pass/fail/retest"),
    admin: User = Depends(require_admin),  # noqa: ARG001
    db: Session = Depends(get_db),
) -> List[SessionResult]:
    query = db.query(QuizSession, User).join(User, QuizSession.user_id == User.id)
    if status_filter == "pass":
        query = query.filter(QuizSession.passed.is_(True))
    elif status_filter == "fail":
        query = query.filter(QuizSession.passed.is_(False))
    elif status_filter == "retest":
        query = query.filter(QuizSession.is_retest.is_(True))

    results = []
    for session, user in query.order_by(QuizSession.created_at.desc()).all():
        results.append(
            SessionResult(
                session_id=session.id,
                employee_id=user.employee_id,
                name=user.name,
                score=session.score,
                passed=session.passed,
                created_at=session.created_at,
                submitted_at=session.submitted_at,
                is_retest=session.is_retest,
            )
        )
    return results


@router.get("/results/csv")
def export_results_csv(
    admin: User = Depends(require_admin),  # noqa: ARG001
    db: Session = Depends(get_db),
) -> StreamingResponse:
    sessions = (
        db.query(QuizSession, User)
        .join(User, QuizSession.user_id == User.id)
        .order_by(QuizSession.created_at.desc())
        .all()
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["사원번호", "이름", "점수", "합격여부", "응시일", "재시험여부"])
    for session, user in sessions:
        writer.writerow(
            [
                user.employee_id,
                user.name,
                session.score if session.score is not None else "",
                "합격" if session.passed else "불합격",
                session.created_at.isoformat(),
                "Y" if session.is_retest else "N",
            ]
        )
    buffer.seek(0)
    headers = {"Content-Disposition": "attachment; filename=quiz_results.csv"}
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers=headers)


@router.post("/retest", status_code=status.HTTP_204_NO_CONTENT)
def approve_retest(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> Response:  # noqa: ARG001
    latest_sessions = (
        db.query(QuizSession.user_id, func.max(QuizSession.id).label("latest_id"))
        .filter(QuizSession.submitted_at.is_not(None))
        .group_by(QuizSession.user_id)
        .subquery()
    )
    failed_user_ids = (
        db.query(QuizSession.user_id)
        .join(latest_sessions, QuizSession.id == latest_sessions.c.latest_id)
        .filter(QuizSession.passed.is_(False))
        .all()
    )
    user_ids = [row[0] for row in failed_user_ids]
    if user_ids:
        db.query(User).filter(User.id.in_(user_ids)).update({User.can_retake: True}, synchronize_session=False)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
