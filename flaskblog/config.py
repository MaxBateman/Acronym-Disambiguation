
import os
import json
from datetime import timedelta

ADMINS = ['acrpubmed@gmail.com']
with open('/etc/config.json') as config_file:
    config = json.load(config_file)

class Config:
    RQ_ASYNC = True
    SESSION_TYPE = 'redis'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=21600)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = config.get('SECRET_KEY')

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'acrpubmed@gmail.com'
    MAIL_PASSWORD = 'Poohbiecuteacr123'
    
