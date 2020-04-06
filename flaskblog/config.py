
import os
import json
from datetime import timedelta


with open('/etc/config.json') as config_file:
    config = json.load(config_file)

class Config:
    RQ_ASYNC = True
    SESSION_TYPE = 'redis'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=21600)
    #SERVER_NAME = '151.236.220.136:5000'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = config.get('SECRET_KEY')
    #SECRET_KEY = 'f33eb5d45b89dd2e5c07a75c96835848'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
