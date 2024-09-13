from typing import List, Optional
import chardet
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import csv
from io import StringIO
from app.schemas.questions import Question, QuestionCreate, QuestionSetType, TestNoWithCategoryResponse, \
    UserAnswerSchema
from app.crud.questions import create_question, get_questions, get_questions_by_cat, get_question_set_types, \
    delete_question_set_type_by_name, get_distinct_testno_with_category
from app.db.session import get_db
from app.security import get_current_user, TokenData
import logging

from app.models.questions import QuestionSetType as SQLAlchemyQuestionSetType, UserAnswer
from app.schemas.questions import QuestionSetTypeCreate
from app.models.questions import Question as QuestionModel  # Use the model, not the schema
from app.schemas.questions import Question as QuestionSchema

logger = logging.getLogger(__name__)
router = APIRouter()

# Endpoint for uploading questions via CSV
@router.post("/upload_questions/", response_model=List[Question])
async def upload_csv(
    file: UploadFile = File(...),
    category: Optional[str] = None,
    test_no: str = None,  # Accept test number
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    questions = []
    print(f"Received file: {file.filename}")
    print(f"Received category: {category}")
    print(f"Received test number: {test_no}")

    if not test_no:
        raise HTTPException(status_code=400, detail="Test number is required")

    try:
        content = await file.read()
        result = chardet.detect(content)
        encoding = result.get('encoding', 'utf-8')

        try:
            text_content = content.decode(encoding)
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Unable to decode file content with detected encoding.")

        csv_file = StringIO(text_content)
        reader = csv.DictReader(csv_file, delimiter=',')

        expected_headers = ["Description", "OptionA", "OptionB", "OptionC", "OptionD", "CorrectOption"]
        headers = [header.strip() for header in reader.fieldnames if header.strip()]

        if set(headers) != set(expected_headers):
            raise HTTPException(status_code=400, detail=f"CSV file headers are not as expected. Detected: {headers}")

        for row in reader:
            cleaned_row = {key: value.strip() for key, value in row.items() if key in expected_headers}
            if any(value == "" for value in cleaned_row.values()):
                print(f"Skipping row with missing data: {cleaned_row}")
                continue
            question_data = QuestionCreate(
                description=cleaned_row["Description"],
                option_a=cleaned_row["OptionA"],
                option_b=cleaned_row["OptionB"],
                option_c=cleaned_row["OptionC"],
                option_d=cleaned_row["OptionD"],
                correct_option=cleaned_row["CorrectOption"],
                category=category,
                test_no=test_no  # Include test number
            )
            created_question = create_question(db=db, question=question_data)
            questions.append(created_question)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

    return questions

# Endpoint to get all questions
@router.get("/questions/", response_model=List[Question])
def read_questions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    return get_questions(db, skip=skip, limit=limit)


# Endpoint to get questions by category
@router.get("/questions_by_cat/", response_model=List[Question])
def read_questions_by_cat(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return get_questions_by_cat(db, category=category, skip=skip, limit=limit)


@router.get("/testno_with_category/", response_model=List[str])
def get_testno_category(
        category: str,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)  # Token validation if needed
):
    testnos = get_distinct_testno_with_category(db, category)
    if not testnos:
        raise HTTPException(status_code=404, detail="No test numbers found for this category")

    # Extract only test_no values from the result and return them
    return [test_no[0] for test_no in testnos]
@router.post("/question_set_type/", response_model=QuestionSetTypeCreate)
def create_question_set(
        question_set: QuestionSetTypeCreate,
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    # Use the SQLAlchemy model to query the database
    existing_question_set = db.query(SQLAlchemyQuestionSetType).filter(
        SQLAlchemyQuestionSetType.name == question_set.name).first()

    if existing_question_set:
        raise HTTPException(status_code=400, detail="Question Set Type already exists.")

    # Create a new instance of the SQLAlchemy model
    new_question_set = SQLAlchemyQuestionSetType(name=question_set.name)

    db.add(new_question_set)
    db.commit()
    db.refresh(new_question_set)

    return new_question_set


# Endpoint to get all question set types
@router.get("/question_set_types/", response_model=List[QuestionSetType])
def get_question_sets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    return get_question_set_types(db, skip=skip, limit=limit)

@router.get("/questions_by_set_and_test", response_model=List[QuestionSchema])
def get_questions_by_set_and_test(
    category: Optional[str],  # setName/category
    test_no: Optional[int],  # testNo
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):

    print(category,test_no)
    if not category or not test_no:
        raise HTTPException(status_code=400, detail="Category and test number must be provided.")

    # Convert test_no to a string if necessary
    questions = (
        db.query(QuestionModel)
        .filter(QuestionModel.category == category)
        .filter(QuestionModel.test_no == str(test_no))  # Convert test_no to string
        .all()
    )

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for the provided set and test number.")

    return questions

@router.delete("/question_set_type/{set_name}")
def delete_question_set_type(
    set_name: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)  # Token validation
):
    return delete_question_set_type_by_name(db=db, set_name=set_name)


@router.post("/save_answers/")
def save_answers(
        answers: List[dict],
        db: Session = Depends(get_db),
        current_user: TokenData = Depends(get_current_user)
):
    """
    Endpoint to save the user's answers to the database.
    Expected format for answers: [{'question_id': 1, 'answer': 'A'}, {'question_id': 2, 'answer': 'B'}, ...]
    """
    saved_answers = []
    for answer_data in answers:
        question_id = answer_data.get('question_id')
        user_answer = answer_data.get('answer')

        # Check if question exists
        question = db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question with ID {question_id} not found.")

        # Save the answer in the database
        new_answer = UserAnswer(
            user_id=current_user.id,
            question_id=question_id,
            answer=user_answer,
            test_no=question.test_no,
            set_name=question.category  # Assuming set_name is equivalent to the category
        )
        db.add(new_answer)
        saved_answers.append(new_answer)

    db.commit()
    return {"detail": "Answers saved successfully", "saved_answers": saved_answers}


@router.get("/get_answers/{user_id}/{test_no}/{set_name}", response_model=List[UserAnswerSchema])
def get_user_answers(
    user_id: int,
    test_no: str,
    set_name: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all saved answers for a user based on test number and set name.
    """
    answers = (
        db.query(UserAnswer)
        .filter(UserAnswer.user_id == user_id)
        .filter(UserAnswer.test_no == test_no)
        .filter(UserAnswer.set_name == set_name)
        .all()
    )
    if not answers:
        raise HTTPException(status_code=404, detail="No answers found for the specified test and set.")
    return answers
