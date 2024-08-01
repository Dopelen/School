# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from database import Base
import os

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    grade = Column(Integer, index=True)
    class_code = Column(String(5), index=True)
    average_score = Column(Numeric, nullable=True)
    subjects = Column(JSONB, nullable=True)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key == 'subjects':
            self.average_score = Student.calculate_average_score(value)

    @staticmethod
    def calculate_average_score(subjects):
        if subjects:
            scores = subjects.values()
            if scores:
                return round(sum(scores) / len(scores), 2)
        return None
