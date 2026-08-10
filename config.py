import os
from dotenv import load_dotenv

load_dotenv()
class Config():
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///projectmaster.db'

    if SECRET_KEY is None:
        raise RuntimeError("Secret Env key is required for configuration")