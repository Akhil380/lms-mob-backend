from typing import Optional

from sqlalchemy.orm import Session
from app.models.questions import Question
from app.schemas.questions import QuestionCreate


def create_question(db: Session, question: QuestionCreate):
    db_question = Question(
        description=question.description,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        correct_option=question.correct_option,
        category=question.category
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def get_questions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Question).offset(skip).limit(limit).all()

def get_questions_by_cat(db: Session, category: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = db.query(Question)
    if category:
        query = query.filter(Question.category == category)
    return query.offset(skip).limit(limit).all()