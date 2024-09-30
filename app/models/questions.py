# from datetime import datetime
#
# from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Table, DateTime
# from sqlalchemy.orm import relationship
#
# from app.db.base import Base
#
# # Association table for the many-to-many relationship
# user_question_set_association = Table(
#     'user_question_set_association',
#     Base.metadata,
#     Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
#     Column('question_set_id', Integer, ForeignKey('question_set_types.id'), primary_key=True)
# )
#
#
# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
#     email = Column(String, unique=True, index=True, nullable=False)
#     mobile = Column(String, unique=True, index=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     registered_on = Column(DateTime, default=datetime.utcnow)
#
#     # Define the relationship to test results
#     test_results = relationship("TestResult", back_populates="user")
#     # Relationship to subscribed question sets
#     subscriptions = relationship(
#         "QuestionSetType",
#         secondary=user_question_set_association,
#         back_populates="subscribers"
#     )
# class QuestionSetType(Base):
#     __tablename__ = "question_set_types"
#
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True, index=True, nullable=False)
#     # Relationship to users who have subscribed to this question set
#     subscribers = relationship(
#         "User",
#         secondary=user_question_set_association,
#         back_populates="subscriptions"
#     )
#
# # SQLAlchemy model for questions
# class Question(Base):
#     __tablename__ = "questions"
#
#     id = Column(Integer, primary_key=True, index=True)
#     description = Column(Text, nullable=False)
#     option_a = Column(String, nullable=False)
#     option_b = Column(String, nullable=False)
#     option_c = Column(String, nullable=False)
#     option_d = Column(String, nullable=False)
#     correct_option = Column(String, nullable=False)
#     category = Column(String, nullable=True)
#     test_no = Column(String, nullable=False)
#     test_time = Column(Integer, nullable=True)  # Test duration in minutes
#     test_availability = Column(String, nullable=True)
#
#     # Relationship to TestResult
#     test_results = relationship("TestResult", back_populates="question")
#
#     def __repr__(self):
#         return f"<Question(description={self.description}, correct_option={self.correct_option})>"
#
# # SQLAlchemy model for test results
# class TestResult(Base):
#     __tablename__ = "test_results"
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
#     category = Column(String, nullable=False)
#     test_no = Column(String, nullable=False)
#     user_selected_answer = Column(String, nullable=True)  # Allow null if unanswered
#     correct_option = Column(String, nullable=False)
#     is_attended = Column(Boolean, default=False)
#     description = Column(String, nullable=False)
#
#     # New field to track if the user's answer is correct
#     is_user_answer_true = Column(Boolean, default=False)
#
#     # Relationships
#     user = relationship("User", back_populates="test_results")
#     question = relationship("Question", back_populates="test_results")
#
# class UserMapperWithQuestionSetSubscribed(Base):
#     __tablename__ = "user_mapper_with_question_set_subscribed"
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     question_set_id = Column(Integer, ForeignKey("question_set_types.id"), nullable=False)
#
#     user = relationship("User", back_populates="subscriptions")
#     question_set = relationship("QuestionSetType", back_populates="subscribers")

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Table, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

# Association table for the many-to-many relationship
user_question_set_association = Table(
    'user_question_set_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('question_set_id', Integer, ForeignKey('question_set_types.id'), primary_key=True)
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    registered_on = Column(DateTime, default=datetime.utcnow)

    # Define the relationship to test results
    test_results = relationship("TestResult", back_populates="user")

    # Relationship to subscribed question sets
    subscriptions = relationship(
        "QuestionSetType",
        secondary=user_question_set_association,
        back_populates="subscribers"
    )


class QuestionSetType(Base):
    __tablename__ = "question_set_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # Relationship to users who have subscribed to this question set
    subscribers = relationship(
        "User",
        secondary=user_question_set_association,
        back_populates="subscriptions"
    )


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
    test_no = Column(String, nullable=False)
    test_time = Column(Integer, nullable=True)  # Test duration in minutes
    test_availability = Column(String, nullable=True)

    # Relationship to TestResult
    test_results = relationship("TestResult", back_populates="question")

    def __repr__(self):
        return f"<Question(description={self.description}, correct_option={self.correct_option})>"


# SQLAlchemy model for test results
class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    category = Column(String, nullable=False)
    test_no = Column(String, nullable=False)
    user_selected_answer = Column(String, nullable=True)  # Allow null if unanswered
    correct_option = Column(String, nullable=False)
    is_attended = Column(Boolean, default=False)
    description = Column(String, nullable=False)

    # New field to track if the user's answer is correct
    is_user_answer_true = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="test_results")
    question = relationship("Question", back_populates="test_results")

