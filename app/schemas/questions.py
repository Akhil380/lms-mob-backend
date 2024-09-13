from pydantic import BaseModel
from typing import Optional, List

# Schema for question creation
class QuestionBase(BaseModel):
    description: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    category: Optional[str] = None
    test_no: str
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

class TestNoWithCategoryResponse(BaseModel):
    test_no: str
    category: str

    class Config:
        orm_mode = True


class SaveAnswersSchema(BaseModel):
    user_id: int
    question_id: int
    answer: str = ""
    test_no: int
    set_name: str

class UserAnswerSchema(BaseModel):
    id: int
    user_id: int
    question_id: int
    answer: str
    test_no: int
    set_name: str
    status: str

    class Config:
        orm_mode = True

# Schema to handle update operations
class UpdateAnswerSchema(BaseModel):
    new_answer: str