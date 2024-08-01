# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import models
import schemas


def get_student(db: Session, student_id: int):
    """
    Получает студента по ID.
    :param db: Сессия SQLAlchemy.
    :param student_id: ID студента.
    :return: Объект студента или None, если не найден.
    """
    try:
        return db.query(models.Student).filter(models.Student.id == student_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error occurred: {e}")


def get_students(db: Session, skip: int = 0, limit: int = 10):
    """
    Получает список студентов.
    :param db: Сессия SQLAlchemy.
    :param skip: Количество пропущенных записей.
    :param limit: Количество возвращаемых записей.
    :return: Список студентов.
    """
    try:
        return db.query(models.Student).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error occurred: {e}")


def create_student(db: Session, student: schemas.StudentCreate):
    """
    Создает нового студента в базе данных.
    :param db: Сессия SQLAlchemy.
    :param student: Данные студента для создания.
    :return: Созданный студент.
    """
    db_student = models.Student(**student.dict())
    try:
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error occurred: {e}")


def update_student(db: Session, student_id: int, student: schemas.StudentCreate):
    """
    Обновляет данные существующего студента.
    :param db: Сессия SQLAlchemy.
    :param student_id: ID студента для обновления.
    :param student: Новые данные студента.
    :return: Обновленный студент.
    :raises HTTPException: Если студент не найден.
    """
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise Exception("Student not found")
    try:
        for key, value in student.dict().items():
            setattr(db_student, key, value)
        db.commit()
        db.refresh(db_student)
        return db_student
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error occurred: {e}")


def delete_student(db: Session, student_id: int):
    """
    Удаляет студента по ID.
    :param db: Сессия SQLAlchemy.
    :param student_id: ID студента для удаления.
    :return: Удаленный студент.
    :raises HTTPException: Если студент не найден.
    """
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise Exception("Student not found")
    try:
        db.delete(db_student)
        db.commit()
        return db_student
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error occurred: {e}")
