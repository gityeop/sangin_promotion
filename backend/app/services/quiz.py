from __future__ import annotations

import random
import uuid
from typing import Iterable, List, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Image, ImageType, QuizSession, Setting, User


def get_active_settings(db: Session) -> Setting:
    setting = db.query(Setting).first()
    if setting is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Quiz settings missing")
    return setting


def generate_quiz_session(db: Session, user: User) -> Tuple[QuizSession, List[dict]]:
    settings = get_active_settings(db)
    correct_images = (
        db.query(Image)
        .filter(Image.type == ImageType.CORRECT, Image.used_in_session.is_(False))
        .all()
    )
    incorrect_images = (
        db.query(Image)
        .filter(Image.type == ImageType.INCORRECT, Image.used_in_session.is_(False))
        .all()
    )

    if len(correct_images) < settings.num_questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient correct images")
    if len(incorrect_images) < settings.num_questions * (settings.num_options - 1):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient incorrect images")

    question_set: List[dict] = []

    for _ in range(settings.num_questions):
        correct = random.choice(correct_images)
        correct_images.remove(correct)

        incorrect_choices = random.sample(incorrect_images, settings.num_options - 1)
        for incorrect in incorrect_choices:
            incorrect_images.remove(incorrect)

        all_options = [correct] + incorrect_choices
        for image in all_options:
            image.used_in_session = True

        question_id = str(uuid.uuid4())
        shuffled = all_options[:]
        random.shuffle(shuffled)

        question_set.append(
            {
                "question_id": question_id,
                "answer_id": correct.id,
                "options": [
                    {
                        "image_id": image.id,
                        "file_url": image.file_url,
                    }
                    for image in shuffled
                ],
            }
        )

    session = QuizSession(user_id=user.id, question_set=question_set, is_retest=user.can_retake)
    user.can_retake = False
    db.add(session)
    db.commit()
    db.refresh(session)

    return session, question_set


def evaluate_submission(session: QuizSession, answers: List[dict], passing_score: int) -> Tuple[int, bool, List[int]]:
    question_map = {q["question_id"]: q for q in session.question_set}
    total_questions = len(question_map)
    correct_count = 0
    used_image_ids: List[int] = []

    for question in session.question_set:
        for option in question["options"]:
            used_image_ids.append(option["image_id"])

    for answer in answers:
        question = question_map.get(answer["question_id"])
        if question and answer["selected_image_id"] == question["answer_id"]:
            correct_count += 1

    score = int((correct_count / total_questions) * 100) if total_questions else 0
    passed = score >= passing_score
    return score, passed, used_image_ids


def release_images(db: Session, image_ids: Iterable[int]) -> None:
    if not image_ids:
        return
    (
        db.query(Image)
        .filter(Image.id.in_(set(image_ids)))
        .update({Image.used_in_session: False}, synchronize_session=False)
    )
    db.commit()

