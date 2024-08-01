# tests/test_main.py
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from faker import Faker
from pydantic import ValidationError
from sqlalchemy import text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from random import randint, choice
from main import app
from database import engine, SessionLocal, Base

@pytest.fixture(scope="session")
def test_db():
    """Создание тестовой базы данных и очистка после выполнения всех тестов"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_db):
    """Фикстура для управления транзакциями в тестах"""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для клиента с использованием тестовой базы данных"""
    from fastapi.testclient import TestClient
    from main import app  # импортируйте ваше приложение FastAPI
    yield TestClient(app)


def test_database_connection(test_db):
    """Простой тест для проверки правильности подключения и использования базы данных"""
    with engine.connect() as conn:
        # Попробуйте создать таблицу и вставить данные
        conn.execute(text("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name TEXT);"))
        print("Table created or already exists.")

        conn.execute(text("INSERT INTO test_table (name) VALUES ('test');"))
        print("Inserted data into table.")

        result = conn.execute(text("SELECT name FROM test_table;")).fetchall()
        print(f"Query result: {result}")

        assert result == [('test',)]

        # Убедитесь, что данные удаляются после выполнения теста
        conn.execute(text("DROP TABLE IF EXISTS test_table;"))
        print("Table dropped.")

faker = Faker()

def generate_random_student_data():
    """Функция - генератор базовых тестовых полей"""
    return {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "grade": randint(1, 12),
        "class_code": choice(["A", "B", "C", "D", "E"]),
        "subjects": {faker.word(): randint(1, 5) for _ in range(randint(1, 5))}
    }

def calculate_average_score(subjects):
    return sum(subjects.values()) / len(subjects)

@pytest.mark.parametrize(
    "student_data",
    [generate_random_student_data() for _ in range(30)])
def test_create_student(student_data, client):
    """Тест который принимает данные из функции создающей тесткейсы и проверяет их"""
    response = client.post("/students/", json=student_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == student_data["first_name"]
    assert data["last_name"] == student_data["last_name"]
    assert round(data["average_score"], 2) == round(calculate_average_score(student_data["subjects"]), 2)

def test_create_student_invalid_first_name(client):
    """Тест проверяющий длину поля ввода имени"""
    invalid_data = {
        "first_name": "A" * 51,
        "last_name": "Иванов",
        "grade": 8,
        "class_code": "A"
    }
    response = client.post("/students/", json=invalid_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should have at most 50 characters"

def test_create_student_invalid_last_name(client):
    """Тест проверяющий длину поля ввода фамилии"""
    invalid_data = {
        "first_name": "Иван",
        "last_name": "И" * 51,
        "grade": 8,
        "class_code": "A"
    }
    response = client.post("/students/", json=invalid_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should have at most 50 characters"

def test_create_student_invalid_grade_more(client):
    """Тест проверяющий значение поля ввода класса (выше границы)"""
    invalid_data = {
        "first_name": "Иван",
        "last_name": "Хитрый",
        "grade": 13,
        "class_code": "A"
    }
    response = client.post("/students/", json=invalid_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be less than or equal to 12"

def test_create_student_invalid_grade_less(client):
    """Тест проверяющий значение поля ввода класса (ниже границы)"""
    invalid_data = {
        "first_name": "Иван",
        "last_name": "Хитрый",
        "grade": 0,
        "class_code": "A"
    }
    response = client.post("/students/", json=invalid_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be greater than or equal to 1"


def test_create_student_valid_class_code(client):
    """Тест проверяющий перевод буквы при вводе в верхний регистр"""
    valid_data = {
        "first_name": "Иванцй",
        "last_name": "Ивы",
        "grade": 8,
        "class_code": "b"
    }
    response = client.post("/students/", json=valid_data)
    assert response.status_code == 200
    data = response.json()
    assert data["class_code"] == "B"


def test_create_student_invalid_class_code_too_long(client):
    """Тест проверяющий длинну поля ввода класса (в большую сторону)"""
    invalid_data = {
        "first_name": "Ивангыч",
        "last_name": "Иванов",
        "grade": 8,
        "class_code": "ABВ"
    }
    response = client.post("/students/", json=invalid_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should have at most 1 character"
