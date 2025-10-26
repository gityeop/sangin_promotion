from app.core.config import get_settings
from app.db.session import SessionLocal, engine
from app.models import Setting
from app.models.base import Base  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    settings = get_settings()
    db = SessionLocal()
    try:
        if not db.query(Setting).first():
            default_setting = Setting(
                passing_score=settings.default_passing_score,
                num_questions=settings.default_num_questions,
                num_options=settings.default_num_options,
            )
            db.add(default_setting)
            db.commit()
    finally:
        db.close()
