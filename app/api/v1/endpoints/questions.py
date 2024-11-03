import os
from datetime import datetime, timedelta
import random
from typing import List, Optional
import chardet
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.openapi.models import Response
from fastapi.params import Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload
import csv
from io import StringIO

from starlette.responses import StreamingResponse

from app import crud, schemas
from app.core.config import settings
from app.schemas.questions import Question, QuestionCreate, QuestionSetType, TestNoWithCategoryResponse, \
    TestResultCreate, TestResultResponse, TestSummaryResponse, ReviewSummaryResponse, UserSubscriptionResponse, \
    UserSubscriptionCreate, UserResponse, TimeAndAvailabilityResponse, VerifyOTPRequest, GenerateOTPRequest, \
    ExamMasterResponse, ExamMasterCreate, CategoryResponse
from app.crud.questions import create_question, get_questions, get_questions_by_cat, get_question_set_types, \
    delete_question_set_type_by_name, get_distinct_testno_with_category, create_test_result, \
    get_review_summary, fetch_test_summary, create_user_subscriptions, get_user_details, get_exam_master, \
    get_exam_masters, create_exam_master_deatils, delete_exam_master_data, get_categories_by_exam_master
from app.db.session import get_db
from app.security import get_current_user, TokenData
import logging

from app.models.questions import QuestionSetType as SQLAlchemyQuestionSetType, TestResult, User, \
    user_question_set_association, Otp, ExamMaster
from app.schemas.questions import QuestionSetTypeCreate
from app.models.questions import Question as QuestionModel
from app.schemas.questions import Question as QuestionSchema

from sqlalchemy.future import select  # Import select for async queries
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, APIRouter, Depends
from datetime import datetime, timedelta


from pydantic import BaseModel
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
logger = logging.getLogger(__name__)
router = APIRouter()


# Endpoint for uploading questions via CSV
@router.post("/upload_questions/", response_model=List[Question])
async def upload_csv(
        file: UploadFile = File(...),

        category: Optional[str] = None,
        test_no: str = None,
        test_time: Optional[int] = None,  # Accept test duration
        test_availability: Optional[str] = None,  # Accept test availability (e.g., 'free', 'paid')
        exam_master_id: int = None,
        db: Session = Depends(get_db),
        #current_user: TokenData = Depends(get_current_user)
):
    questions = []
    print(f"Received file: {file.filename}")
    print(f"Received category: {category}")
    print(f"Received test number: {test_no}")
    print(f"Received test time: {test_time}")
    print(f"Received test availability: {test_availability}")

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
                test_no=test_no,
                test_time=test_time,  # Include test time
                test_availability=test_availability , # Include test availability
                exam_master_id = exam_master_id
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


@router.get("/exam/{exam_master_id}/categories", response_model=List[CategoryResponse])
def read_categories_by_exam_master(exam_master_id: int, db: Session = Depends(get_db)):
    categories = get_categories_by_exam_master(db=db, exam_master_id=exam_master_id)
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found for the given exam_master_id")
    return [{"category_id": category} for category in categories]
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

# Endpoint to create an exam master
@router.post("/exam_masters/", response_model=ExamMasterResponse)
def create_exam_master(exam: ExamMasterCreate, db: Session = Depends(get_db)):
    return create_exam_master_deatils(db=db, exam=exam)

# Endpoint to get an exam master by ID
@router.get("/exam_masters/{exam_id}", response_model=ExamMasterResponse)
def read_exam_master(exam_id: int, db: Session = Depends(get_db)):
    db_exam = get_exam_master(db, exam_id=exam_id)
    if db_exam is None:
        raise HTTPException(status_code=404, detail="Exam master not found")
    return db_exam

# Endpoint to get all exam masters
@router.get("/exam_masters/", response_model=List[ExamMasterResponse])
def read_exam_masters(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_exam_masters(db, skip=skip, limit=limit)

@router.delete("/exam_masters/{exam_id}", response_model=ExamMasterResponse)
def delete_exam_master(exam_id: int, db: Session = Depends(get_db)):
    db_exam = delete_exam_master_data(db, exam_id=exam_id)
    if db_exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    return db_exam


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
    print(category, test_no)
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


@router.post("/save_answers", response_model=List[TestResultResponse])
def save_test_results(test_result: TestResultCreate, db: Session = Depends(get_db),
                      current_user: TokenData = Depends(get_current_user)
                      ):
    """
    Endpoint to save user's test results
    """
    db_test_results = create_test_result(db=db, test_result=test_result)
    return db_test_results


@router.get("/test_summary/", response_model=TestSummaryResponse)
def get_test_summary(user_id: int, test_no: str, set_no: str,
                     db: Session = Depends(get_db),
                     current_user: TokenData = Depends(get_current_user)
                     ):
    """
    Endpoint to retrieve the test summary based on user_id, test_no, and set_no.
    """
    summary = fetch_test_summary(db=db, user_id=user_id, test_no=test_no, set_no=set_no)

    if not summary:
        raise HTTPException(status_code=404, detail="No test results found for the given user, test, and set.")

    return summary


@router.get("/review_summary", response_model=List[TestResultResponse])
def review_summary(user_id: int, test_no: int, set_no: int, db: Session = Depends(get_db),
                   current_user: TokenData = Depends(get_current_user)):
    return get_review_summary(db=db, user_id=user_id, test_no=test_no, set_no=set_no)


# @router.post("/subscribe", response_model=List[UserSubscriptionResponse])
# def subscribe_to_question_sets(
#     subscription: UserSubscriptionCreate,
#     db: Session = Depends(get_db)
# ):
#     return create_user_subscriptions(db=db, subscription=subscription)

@router.post("/subscribe/")
def subscribe_to_question_sets(user_id: int, question_set_ids: List[int], db: Session = Depends(get_db)):
    return create_user_subscriptions(db, user_id, question_set_ids)




@router.get("/check_subscription/")
def check_subscription(user_id: int, set_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to check if a user is subscribed to a specific question set.
    """
    # Corrected SQLAlchemy syntax using `select(1)`
    subscription_exists = db.execute(
        select(1)
        .select_from(user_question_set_association)
        .where(user_question_set_association.c.user_id == user_id)
        .where(user_question_set_association.c.question_set_id == set_id)
    ).first()

    if not subscription_exists:
        return {"is_subscribed": False}

    return {"is_subscribed": True}
@router.get("/test_access_details/", response_model=TimeAndAvailabilityResponse)
def get_test_details(
        category: Optional[str],  # setName/category
        test_no: Optional[int],  # testNo
        db: Session = Depends(get_db)
    ):
    # Validate inputs
    if not category or not test_no:
        raise HTTPException(status_code=400, detail="Category and test number must be provided.")

    # Query the database
    data = (
        db.query(QuestionModel)
        .filter(QuestionModel.category == category)
        .filter(QuestionModel.test_no == str(test_no))  # Convert test_no to string
        .first()
    )

    # If no matching test found
    if not data:
        raise HTTPException(status_code=404, detail="Test not found for the provided category and test_no.")

    # Return the response using the Pydantic model
    return TimeAndAvailabilityResponse(
        set_no=data.category,
        test_no=data.test_no,
        test_time=data.test_time,
        test_availability=data.test_availability
    )


# Brevo API configuration
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = settings.sendinblue_api_key
print("key",settings.sendinblue_api_key)

# Pydantic model for the email data
class EmailRequest(BaseModel):
    to_email: str
    to_name: str
    subject: str
    content: str


@router.post("/send-email")
async def send_email(email_request: EmailRequest):

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email_request.to_email, "name": email_request.to_name}],
        sender={"email": "nursinghopesneverends@gmail.com", "name": "Nursing Pro"},
        subject=email_request.subject,
        html_content=email_request.content
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
        return {"message": "Email sent successfully!"}
    except ApiException as e:
        print(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")


class SMSRequest(BaseModel):
    recipient: str  # Phone number in international format (e.g., +33123456789)
    content: str    # SMS content (max 160 characters)
    sender: str     # Sender name (max 11 characters for alphanumeric, 17 for numeric)
    tag: str = None # Optional tag



@router.post("/send-sms")
async def send_sms(request: SMSRequest):
    api_instance = sib_api_v3_sdk.TransactionalSMSApi(sib_api_v3_sdk.ApiClient(configuration))
    sender_name = request.sender[:11]  # Limit to 11 characters
    send_sms = sib_api_v3_sdk.SendTransacSms(
        sender=sender_name,
        recipient=request.recipient,
        content=request.content,
        tag=request.tag if request.tag else "default-tag"
    )
    try:
        api_response = api_instance.send_transac_sms(send_sms)
        return {"status": "success", "message": "SMS sent successfully", "response": api_response.to_dict()}
    except ApiException as e:
        if e.status == 400 and 'invalid_parameter' in e.body:
            return HTTPException(status_code=400, detail="Invalid sender name. Please ensure it is 11 characters or less.")
        else:
            return HTTPException(status_code=400, detail=f"Failed to send SMS: {e}")


def generate_otp():
    return str(random.randint(100000, 999999))




@router.post("/generate-otp")
async def generate_otp_for_user(request: GenerateOTPRequest, db: AsyncSession = Depends(get_db)):
    # Check if the user exists
    result = db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=3)

    otp_record = Otp(
        user_id=user.id,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(otp_record)
    db.commit()

    email_request = EmailRequest(
        to_email=user.email,
        to_name=user.name,
        subject="Your OTP Code",
        content=f"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="format-detection" content="telephone=no">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your OTP Code</title>
            <style type="text/css" emogrify="no">
                body {{ width:100% !important; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; margin:0; padding:0; }}
                a {{ color: #3f3d56; text-decoration: none; }}
                .nl2go-default-textstyle {{ color: #3f3d56; font-family: Montserrat, Arial, Helvetica, sans-serif; font-size: 20px; line-height: 1.4; }}
                .header {{ background-color: #007bff; color: #ffffff; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; border-radius: 8px; }}
                .footer {{ 
                    background-color: #007bff; 
                    color: #ffffff; 
                    padding: 20px; 
                    text-align: center; 
                    font-size: 12px; 
                    border-radius: 0 0 8px 8px;
                    position: relative; 
                }}
                .footer p {{ margin: 5px 0; }}
                .footer img {{ width: 100px; margin-top: 10px; }}
                .background-image {{
                    background-image: url('https://example.com/your-background-image.jpg'); /* Replace with your image URL */
                    background-size: cover;
                    background-position: center;
                    height: 100%;
                    padding: 20px;
                }}
            </style>
        </head>
        <body bgcolor="#ffffff" text="#3f3d56" link="#3f3d56">
            <div class="background-image">
                <table cellspacing="0" cellpadding="0" border="0" role="presentation" width="100%">
                    <tr>
                        <td class="header">
                            <h1 style="margin:0; font-size:50px; font-weight:700;">Nursing Pro</h1>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table cellspacing="0" cellpadding="0" border="0" width="600" align="center">
                                <tr>
                                    <td class="content">
                                        <h2>Hello {user.name},</h2>
                                        <p class="nl2go-default-textstyle">Your OTP code is <strong>{otp_code}</strong>. It is valid for 3 minutes.</p>
                                        <p class="nl2go-default-textstyle">Please use this code to complete your verification.</p>
                                        <p class="nl2go-default-textstyle">If you did not request this code, please ignore this email.</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td class="footer">
                            <p>Contact Us:</p>
                            <p>Email: <a href="mailto:nursinghopesneverends@gmail.com" style="color: #ffffff;">nursinghopesneverends@gmail.com</a></p>
                            <p>Phone: <a href="tel:+16238575717" style="color: #ffffff;">623-857-5717</a></p>
                            <p>© 2024 Nursing Pro. All rights reserved.</p>
                            <img src="https://example.com/your-logo.png" alt="Nursing Pro Logo" /> <!-- Replace with your logo URL -->
                        </td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
    )
    # Send the email
    await send_email(email_request)
    return {"message": "OTP generated and sent to email."}





@router.post("/verify-otp")
async def verify_otp_endpoint(request: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    # Fetch OTP from the database
    result = db.execute(
        select(Otp).where(Otp.user_id == (select(User.id).where(User.email == request.email)).scalar_subquery())
    )
    otp_entry = result.scalars().first()

    if not otp_entry:
        raise HTTPException(status_code=400, detail="OTP not found or expired")

    if datetime.utcnow() > otp_entry.expires_at:
        db.execute(
            delete(Otp).where(Otp.user_id == (select(User.id).where(User.email == request.email)).scalar_subquery())
        )
        db.commit()
        raise HTTPException(status_code=400, detail="OTP has expired")

    if otp_entry.otp_code != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    db.execute(
        delete(Otp).where(Otp.user_id == (select(User.id).where(User.email == request.email)).scalar_subquery())
    )
    db.commit()

    return {"is_verified": True}

