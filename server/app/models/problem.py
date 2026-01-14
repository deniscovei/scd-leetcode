from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.db import Base

class Problem(Base):
    __tablename__ = 'problems'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(50), nullable=False)
    tags = Column(String(255), nullable=True)
    test_cases = Column(Text, nullable=True) # JSON string of test cases
    templates = Column(Text, nullable=True) # JSON string of code templates
    drivers = Column(Text, nullable=True) # JSON string of driver codes
    time_limits = Column(Text, nullable=True) # JSON string of time limits
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    submissions = relationship("Submission", back_populates="problem")
    owner = relationship("User", back_populates="problems")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'tags': self.tags,
            'test_cases': self.test_cases,
            'templates': self.templates,
            'drivers': self.drivers,
            'time_limits': self.time_limits,
            'owner_id': self.owner_id,
            'owner_username': self.owner.username if self.owner else None
        }




    def __repr__(self):
        return f"<Problem(id={self.id}, title={self.title}, difficulty={self.difficulty})>"