#
#
# from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
# from sqlalchemy.orm import relationship
#
# from app.db.base import Base
# from datetime import datetime
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