from fastapi import HTTPException
from sqlalchemy import distinct, asc
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.questions import Question, QuestionSetType, TestResult, User
from app.schemas.questions import QuestionCreate, QuestionSetTypeCreate, TestResultCreate, TestResultResponse, \
    UserSubscriptionCreate, UserSubscriptionResponse

def get_user_details(db: Session, user_id: int = None, email: str = None, mobile: str = None):
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
    elif email:
        user = db.query(User).filter(User.email == email).first()
    elif mobile:
        user = db.query(User).filter(User.mobile == mobile).first()
    else:
        raise HTTPException(status_code=400, detail="At least one of user_id, email, or mobile must be provided")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
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


    user_answer = db.query(UserAnswer).filter(UserAnswer.id == answer_id).first()
    if user_answer:
        user_answer.answer = new_answer
        user_answer.status = "attended" if new_answer else "unattended"
        db.commit()
        db.refresh(user_answer)
    return user_answer

# 4. DELETE: Delete a user answer by ID
# def create_test_result(db: Session, test_result: TestResultCreate):
#     db_test_results = []
#
#     for result in test_result.results:
#         # Prepare fields
#         user_selected_answer = result.userSelectedAnswer
#         correct_option = result.correct_option
#         is_attended = result.isAttendedFlag
#         description = result.description
#
#         # Compare correct_option with userSelectedAnswer
#         is_user_answer_true = user_selected_answer == correct_option
#
#         # Check if the record already exists (same user, test_no, and question_id)
#         existing_test_result = db.query(TestResult).filter_by(
#             user_id=test_result.user_id,
#             test_no=result.test_no,
#             question_id=result.question_id
#         ).first()
#
#         if existing_test_result:
#             # Update the existing test result
#             existing_test_result.user_selected_answer = user_selected_answer
#             existing_test_result.correct_option = correct_option
#             existing_test_result.is_attended = is_attended
#             existing_test_result.description = description
#             existing_test_result.is_user_answer_true = is_user_answer_true
#         else:
#             # Create a new test result if not exists
#             db_test_result = TestResult(
#                 user_id=test_result.user_id,
#                 question_id=result.question_id,
#                 category=result.category,
#                 test_no=result.test_no,
#                 user_selected_answer=user_selected_answer,
#                 correct_option=correct_option,
#                 is_attended=is_attended,
#                 description=description,
#                 is_user_answer_true=is_user_answer_true  # Set the new field
#             )
#             db.add(db_test_result)
#             db_test_results.append(db_test_result)
#
#     db.commit()
#     return db_test_results
#
#

def create_test_result(db: Session, test_result: TestResultCreate):
    db_test_results = []

    for result in test_result.results:
        user_selected_answer = result.userSelectedAnswer
        correct_option = result.correct_option
        is_attended = result.isAttendedFlag
        description = result.description

        # Calculate if the user's answer is correct
        is_user_answer_true = user_selected_answer == correct_option

        # Check if the result already exists for the user, test, and question
        existing_result = db.query(TestResult).filter(
            TestResult.user_id == test_result.user_id,
            TestResult.test_no == result.test_no,
            TestResult.question_id == result.question_id
        ).first()

        if existing_result:
            # Update existing result
            existing_result.user_selected_answer = user_selected_answer
            existing_result.is_attended = is_attended
            existing_result.is_user_answer_true = is_user_answer_true
        else:
            # Create new result
            db_test_result = TestResult(
                user_id=test_result.user_id,
                question_id=result.question_id,
                category=result.category,
                test_no=result.test_no,
                user_selected_answer=user_selected_answer,
                correct_option=correct_option,
                is_attended=is_attended,
                description=description,
                is_user_answer_true=is_user_answer_true
            )
            db.add(db_test_result)
            db_test_results.append(db_test_result)

    db.commit()
    return db_test_results


from sqlalchemy import cast, String

def get_review_summary(db: Session, user_id: int, test_no: int, set_no: int) -> List[TestResultResponse]:
    try:
        # Cast test_no and set_no to string if needed
        test_no_str = str(test_no)
        set_no_str = str(set_no)

        # Query to retrieve all test results for a specific user, test_no, and set_no
        results = db.query(
            TestResult,
            Question.option_a,
            Question.option_b,
            Question.option_c,
            Question.option_d,
        ).join(Question, TestResult.question_id == Question.id).filter(
            TestResult.user_id == user_id,
            cast(TestResult.test_no, String) == test_no_str,  # Explicit cast to string
            cast(TestResult.category, String) == set_no_str   # Explicit cast to string
        ).all()

        if not results:
            raise HTTPException(status_code=404, detail="Test results not found")

        response = [
            TestResultResponse(
                id=result.TestResult.id,
                user_id=result.TestResult.user_id,
                question_id=result.TestResult.question_id,
                category=result.TestResult.category,
                test_no=result.TestResult.test_no,
                user_selected_answer=result.TestResult.user_selected_answer,
                correct_option=result.TestResult.correct_option,
                is_attended=result.TestResult.is_attended,
                description=result.TestResult.description,
                is_user_answer_true=result.TestResult.is_user_answer_true,
                option_a=result.option_a,
                option_b=result.option_b,
                option_c=result.option_c,
                option_d=result.option_d
            ) for result in results
        ]

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



def fetch_test_summary(db: Session, user_id: int, test_no: int, set_no: int):
    """
    Retrieve the test summary based on user_id, test_no, and set_no (category).
    Returns total questions, attended, unattended, right answers, and wrong answers.
    """
    test_results = db.query(TestResult).filter(
        TestResult.user_id == user_id,
        TestResult.test_no == str(test_no),  # Convert to string to match the database schema
        TestResult.category == str(set_no)  # Convert to string to match the database schema
    ).all()

    if not test_results:
        return None

    total_questions = len(test_results)
    attended_questions = len([result for result in test_results if result.is_attended])
    unattended_questions = total_questions - attended_questions
    right_answers = len([result for result in test_results if result.is_user_answer_true])
    wrong_answers = attended_questions - right_answers

    return {
        "user_id": user_id,
        "test_no": test_no,
        "set_no": set_no,
        "total_questions": total_questions,
        "attended_questions": attended_questions,
        "unattended_questions": unattended_questions,
        "right_answers": right_answers,
        "wrong_answers": wrong_answers
    }


def create_user_subscriptions(db: Session, user_id: int, question_set_ids: List[int]):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch the question sets by their IDs
    question_sets = db.query(QuestionSetType).filter(QuestionSetType.id.in_(question_set_ids)).all()

    if not question_sets:
        raise HTTPException(status_code=404, detail="Question sets not found")

    # Add the subscriptions
    for question_set in question_sets:
        if question_set not in user.subscriptions:
            user.subscriptions.append(question_set)

    db.commit()
    db.refresh(user)

    # Prepare response
    response = [{"user_id": user_id, "question_set_id": qs.id} for qs in question_sets]

    return response