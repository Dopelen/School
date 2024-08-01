# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud
import models
import schemas
from database import get_db, engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def check_root():
    return {"message": "The server is ready for your requests"}


@app.post("/students/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    existing_student = db.query(models.Student).filter(
        models.Student.first_name == student.first_name,
        models.Student.last_name == student.last_name,
        models.Student.class_code == student.class_code
    ).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Student with this data already exists")
    return crud.create_student(db=db, student=student)


@app.get("/students/", response_model=List[schemas.StudentResponse])
def read_students(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    students = crud.get_students(db, skip=skip, limit=limit)
    return students


@app.get("/students/{student_id}", response_model=schemas.StudentResponse)
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student


@app.put("/students/{student_id}", response_model=schemas.StudentResponse)
def update_student(student_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return crud.update_student(db=db, student_id=student_id, student=student)


@app.delete("/students/{student_id}", response_model=schemas.StudentResponse)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return crud.delete_student(db=db, student_id=student_id)
