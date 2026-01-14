from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.utils.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False) # Storing hashed password
    email = Column(String(120), unique=True, nullable=False)
    role = Column(String(20), default='student') # student or admin

    submissions = relationship("Submission", back_populates="user")
    problems = relationship("Problem", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
