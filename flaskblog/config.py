
import os
import json

with open('/etc/config.json') as config_file:
    config = json.load(config_file)

class Config:

    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = config.get('SECRET_KEY')
    #SECRET_KEY = 'f33eb5d45b89dd2e5c07a75c96835848'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
