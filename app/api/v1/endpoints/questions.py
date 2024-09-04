

from typing import Optional, List
import chardet
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import csv
from io import StringIO
from app.schemas.questions import Question, QuestionCreate
from app.crud.questions import create_question, get_questions, get_questions_by_cat
from app.db.session import get_db
from app.security import get_current_user, TokenData

router = APIRouter()

@router.post("/upload_questions/", response_model=List[Question])
async def upload_csv(
    file: UploadFile = File(...),
    category: str = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    questions = []
    print(f"Received file: {file.filename}")
    print(f"Received category: {category}")

    try:
        content = await file.read()
        print(f"File content: {content[:100]}...")

        result = chardet.detect(content)
        encoding = result.get('encoding', 'utf-8')
        if not isinstance(encoding, str):
            encoding = 'utf-8'
        try:
            text_content = content.decode(encoding)
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Unable to decode file content with detected encoding.")

        csv_file = StringIO(text_content)
        reader = csv.DictReader(csv_file, delimiter=',')

        headers = [header.strip() for header in reader.fieldnames if header.strip()]
        print(f"Detected headers: {headers}")

        expected_headers = ["Description", "OptionA", "OptionB", "OptionC", "OptionD", "CorrectOption"]
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
                category=category
            )
            created_question = create_question(db=db, question=question_data)
            questions.append(created_question)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

    return questions

@router.get("/questions/", response_model=List[Question])
def read_questions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    questions = get_questions(db, skip=skip, limit=limit)
    print(f"Retrieved questions: {questions}")
    return questions

@router.get("/questions_by_cat/", response_model=List[Question])
def read_questions_by_cat(
    current_user: TokenData = Depends(get_current_user),
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),

):
    questions = get_questions_by_cat(db, category=category, skip=skip, limit=limit)
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found")
    print(f"Retrieved questions: {questions}")
    return questions
