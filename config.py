import os
import boto3
from dotenv import load_dotenv
import json
from boto3.session import Session

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.flaskenv'))


class Config(object):
    APP_root = basedir
    APP_STATIC = os.path.join(basedir, 'app/static')
    APPS_STATIC = os.path.join(basedir, 'app/apps/apps_static')
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')
    boto_sess = Session(
        region_name=AWS_DEFAULT_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    DYNAMO_SESSION = boto_sess
    DYNAMO_CLIENT = boto3.resource('dynamodb', region_name=AWS_DEFAULT_REGION,
                                   aws_access_key_id=AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    COGNITO_REGION = os.environ.get('COGNITO_REGION')
    COGNITO_USERPOOL_ID = os.environ.get('COGNITO_USERPOOL_ID')
    AWS_COGNITO_DOMAIN = os.environ.get('AWS_COGNITO_DOMAIN')
    AWS_COGNITO_USER_POOL_ID = os.environ.get('AWS_COGNITO_USER_POOL_ID')
    AWS_COGNITO_USER_POOL_CLIENT_ID = os.environ.get('AWS_COGNITO_USER_POOL_CLIENT_ID')
    AWS_COGNITO_USER_POOL_CLIENT_SECRET = os.environ.get('AWS_COGNITO_USER_POOL_CLIENT_SECRET')
    AWS_COGNITO_REDIRECT_URL = os.environ.get('AWS_COGNITO_REDIRECT_URL')
