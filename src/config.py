import os

class Config:
    """Основная конфигурация для разработки"""
    DATABASE_URL = "postgresql://postgres:771772@localhost/school_original"

class TestConfig(Config):
    """Конфигурация для тестирования"""
    DATABASE_URL = "postgresql://postgres:771772@localhost/school_fortest"