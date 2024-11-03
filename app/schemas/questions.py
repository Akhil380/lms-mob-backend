from datetime import datetime

from pydantic import BaseModel, EmailStr
from typing import Optional, List

# Schema for question creation
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    mobile: str
    registered_on: datetime

    class Config:
        orm_mode = True
class QuestionBase(BaseModel):
    description: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    category: Optional[str] = None
    test_no: str
    test_time: Optional[int] = None
    test_availability: Optional[str] = None
    exam_master_id: int


class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int

    class Config:
        from_attributes = True  # For SQLAlchemy compatibility


# Schema for question set type creation
class QuestionSetTypeCreate(BaseModel):
    name: str

class QuestionSetType(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # For SQLAlchemy compatibility


class ExamMasterBase(BaseModel):
    name: str
    description: Optional[str] = None


class ExamMasterCreate(ExamMasterBase):
    pass

class ExamMasterResponse(ExamMasterBase):
    id: int

    class Config:
        from_attributes = True

class TestNoWithCategoryResponse(BaseModel):
    test_no: str
    category: str

    class Config:
        orm_mode = True



class CategoryResponse(BaseModel):
    category_id: str

    class Config:
        orm_mode = True

# class QuestionResult(BaseModel):
#     question_id: int
#     description: str
#     category: str
#     test_no: str
#     userSelectedAnswer: Optional[str] = None
#     correct_option: str
#     isAttendedFlag: bool
#
# # Schema for the request body
# class TestResultCreate(BaseModel):
#     user_id: int
#     results: List[QuestionResult]
#
# # Response schema
# class TestResultResponse(BaseModel):
#     id: int
#     user_id: int
#     question_id: int
#     category: str
#     test_no: str
#     user_selected_answer: Optional[str] = None
#     correct_option: str
#     is_attended: bool
#     description: str
#     is_user_answer_true: bool
#
#     class Config:
#         orm_mode = True

from pydantic import BaseModel
from typing import List, Optional

# Schema for the question results
class QuestionResult(BaseModel):
    question_id: int
    description: str
    category: str
    test_no: str
    userSelectedAnswer: Optional[str] = None
    correct_option: str
    isAttendedFlag: bool
    is_user_answer_true: Optional[bool] = None  # Make this field optional

    class Config:
        orm_mode = True


# Schema for the test result create
class TestResultCreate(BaseModel):
    user_id: int
    results: List[QuestionResult]

class TestResultResponse(BaseModel):
    id: int
    user_id: int
    question_id: int
    category: str
    test_no: str
    user_selected_answer: Optional[str] = None
    correct_option: str
    is_attended: bool
    description: str
    is_user_answer_true: bool

    # Include options from the Question model
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    class Config:
        from_attributes = True

class TestSummaryResponse(BaseModel):
    user_id: int
    test_no: str
    set_no: str
    total_questions: int
    attended_questions: int
    unattended_questions: int
    right_answers: int
    wrong_answers: int

    class Config:
        orm_mode = True



class ReviewQuestion(BaseModel):
    question_id: int
    description: str
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_option: str
    user_selected_answer: Optional[str] = None
    is_user_answer_true: bool
    is_attended: bool

    class Config:
        orm_mode = True
class ReviewSummaryResponse(BaseModel):
    user_id: int
    test_no: str
    set_no: str
    questions: List[ReviewQuestion]

class UserSubscriptionCreate(BaseModel):
    user_id: int
    question_set_ids: List[int]  # List of question set IDs

class UserSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    question_set_id: int

    class Config:
        orm_mode = True

class TimeAndAvailabilityResponse(BaseModel):
    set_no: str
    test_no: str
    test_time: Optional[int]  # Test time (in minutes)
    test_availability: Optional[str]  # Test availability (free/paid)

    class Config:
        orm_mode = True


class GenerateOTPRequest(BaseModel):
    email: EmailStr  # Ensure that the email is valid

class VerifyOTPRequest(BaseModel):
    email: EmailStr  # The email to verify the OTP against
    otp: str  # The OTP code to verify