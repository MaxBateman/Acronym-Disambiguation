import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    #SECRET_KEY = 'f33eb5d45b89dd2e5c07a75c96835848'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'