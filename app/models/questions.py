from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

# SQLAlchemy model for questions
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_option = Column(String, nullable=False)
    category = Column(String, nullable=True)
    test_no = Column(String, nullable=False)  # Add test number

    # Relationship to UserAnswer
    answers = relationship("UserAnswer", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question(description={self.description}, correct_option={self.correct_option})>"


# SQLAlchemy model for question set types
class QuestionSetType(Base):
    __tablename__ = "question_set_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Assuming users are logged in
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer = Column(String, nullable=False)  # Stores the selected answer
    test_no = Column(Integer, nullable=False)
    set_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default='attended')  # 'attended' or 'unattended'

    # Relationship to Question and User
    question = relationship("Question", back_populates="answers")
    user = relationship("User", back_populates="answers")  # Assuming you have a User model

    def __repr__(self):
        return f"<UserAnswer(user_id={self.user_id}, question_id={self.question_id}, answer={self.answer})>"
