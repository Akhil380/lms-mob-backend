from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base

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

    def __repr__(self):
        return f"<Question(description={self.description}, correct_option={self.correct_option})>"
