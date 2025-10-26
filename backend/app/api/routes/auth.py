from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models import QuizSession, Setting, User, UserRole
from app.schemas import AdminLoginRequest, Token, UserLogin

router = APIRouter()
settings = get_settings()


@router.post("/login", response_model=Token)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = (
        db.query(User)
        .filter(User.employee_id == payload.employee_id, User.name == payload.name)
        .one_or_none()
    )
    if user is None:
        user = User(employee_id=payload.employee_id, name=payload.name, role=UserRole.USER)
        db.add(user)
        db.commit()
        db.refresh(user)

    active_session = (
        db.query(QuizSession)
        .filter(QuizSession.user_id == user.id, QuizSession.submitted_at.is_(None))
        .first()
    )
    if active_session:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Active session exists")

    token, expire = create_access_token({"user_id": user.id, "role": user.role})
    return Token(access_token=token, expires_at=expire)


@router.post("/admin/login", response_model=Token)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)) -> Token:
    if payload.username != settings.admin_username or payload.password != settings.admin_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    admin_user = db.query(User).filter(User.role == UserRole.ADMIN, User.name == payload.username).first()
    if admin_user is None:
        admin_user = User(employee_id=f"admin-{payload.username}", name=payload.username, role=UserRole.ADMIN)
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

    if not db.query(Setting).first():
        setting = Setting(
            passing_score=settings.default_passing_score,
            num_questions=settings.default_num_questions,
            num_options=settings.default_num_options,
        )
        db.add(setting)
        db.commit()

    token, expire = create_access_token({"user_id": admin_user.id, "role": admin_user.role})
    return Token(access_token=token, expires_at=expire)
