# -*- coding: utf-8 -*-
from pydantic import BaseModel, constr, conint, validator
from typing import Dict, Optional


class StudentBase(BaseModel):
    first_name: constr(max_length=50)
    last_name: constr(max_length=50)
    grade: conint(ge=1, le=12)
    class_code: constr(max_length=1)
    subjects: Optional[Dict[str, conint(ge=1, le=5)]] = None

    @validator('class_code', pre=True, always=True)
    def uppercase_class_code(cls, v):
        return v.upper() if v else v

    @validator('subjects', always=True)
    def check_subjects(cls, v):
        if v:
            for subject, score in v.items():
                if not (1 <= score <= 5):
                    raise ValueError(f"Score for subject '{subject}' must be between 1 and 5")
        return v

    @validator('grade', always=True)
    def check_grade(cls, v):
        if v < 1 or v > 12:
            raise ValueError("Grade must be between 1 and 12")
        return v


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    id: int
    average_score: Optional[float] = None

    class Config:
        orm_mode = True
