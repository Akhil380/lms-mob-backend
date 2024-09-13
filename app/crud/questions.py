from fastapi import HTTPException
from sqlalchemy import distinct, asc
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.questions import Question, QuestionSetType, UserAnswer
from app.schemas.questions import QuestionCreate, QuestionSetTypeCreate, SaveAnswersSchema


# CRUD for creating a question
def create_question(db: Session, question: QuestionCreate) -> Question:
    db_question = Question(
        description=question.description,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        correct_option=question.correct_option,
        category=question.category,
        test_no=question.test_no
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


# CRUD for retrieving all questions
def get_questions(db: Session, skip: int = 0, limit: int = 100) -> List[Question]:
    return db.query(Question).offset(skip).limit(limit).all()


# CRUD for retrieving questions by category
def get_questions_by_cat(db: Session, category: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Question]:
    query = db.query(Question)
    if category:
        query = query.filter(Question.category == category)
    return query.offset(skip).limit(limit).all()


# CRUD for creating a question set type
def create_question_set_type(db: Session, question_set: QuestionSetTypeCreate) -> QuestionSetType:
    db_question_set = QuestionSetType(name=question_set.name)
    db.add(db_question_set)
    db.commit()
    db.refresh(db_question_set)
    return db_question_set


# CRUD for retrieving all question set types
def get_question_set_types(db: Session, skip: int = 0, limit: int = 100) -> List[QuestionSetType]:
    return db.query(QuestionSetType).offset(skip).limit(limit).all()


def delete_question_set_type_by_name(db: Session, set_name: str):
    # Find the Question Set Type by name
    question_set_type = db.query(QuestionSetType).filter(QuestionSetType.name == set_name).first()

    if not question_set_type:
        raise HTTPException(status_code=404, detail="Question Set Type not found.")

    # Delete the Question Set Type if found
    db.delete(question_set_type)
    db.commit()

    return {"message": f"Question Set Type '{set_name}' deleted successfully"}

def get_distinct_testno_with_category(db: Session, category: str):
    return db.query(distinct(Question.test_no)).filter(Question.category == category).order_by(asc(Question.test_no)).all()


def create_user_answer(db: Session, answer_data: SaveAnswersSchema):
    db_answer = UserAnswer(
        user_id=answer_data.user_id,
        question_id=answer_data.question_id,
        answer=answer_data.answer,
        test_no=answer_data.test_no,
        set_name=answer_data.set_name,
        status="attended" if answer_data.answer else "unattended"
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer

# 2. READ: Get user answers by user ID, test_no, and set_name
def get_user_answers(db: Session, user_id: int, test_no: int, set_name: str):
    return db.query(UserAnswer).filter(
        UserAnswer.user_id == user_id,
        UserAnswer.test_no == test_no,
        UserAnswer.set_name == set_name
    ).all()

# 3. UPDATE: Update user answer for a specific question
def update_user_answer(db: Session, answer_id: int, new_answer: str):
    user_answer = db.query(UserAnswer).filter(UserAnswer.id == answer_id).first()
    if user_answer:
        user_answer.answer = new_answer
        user_answer.status = "attended" if new_answer else "unattended"
        db.commit()
        db.refresh(user_answer)
    return user_answer

# 4. DELETE: Delete a user answer by ID
def delete_user_answer(db: Session, answer_id: int):
    user_answer = db.query(UserAnswer).filter(UserAnswer.id == answer_id).first()
    if user_answer:
        db.delete(user_answer)
        db.commit()
    return user_answer