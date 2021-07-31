import os
from flask_mail import Mail
app_dir = os.path.abspath(os.path.dirname(__file__))
from flask_user import login_required, SQLAlchemyAdapter, UserManager, UserMixin
from flask_user import roles_required

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A SECRET KEY'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail settings
    MAIL_USERNAME =           os.getenv('MAIL_USERNAME',        'youremail@example.com')
    MAIL_PASSWORD =           os.getenv('MAIL_PASSWORD',        'yourpassword')
    MAIL_DEFAULT_SENDER =     os.getenv('MAIL_DEFAULT_SENDER',  '"MyApp" <noreply@example.com>')
    MAIL_SERVER =             os.getenv('MAIL_SERVER',          'smtp.gmail.com')
    MAIL_PORT =           int(os.getenv('MAIL_PORT',            '465'))
    MAIL_USE_SSL =        int(os.getenv('MAIL_USE_SSL',         True))

    # Flask-User settings
    USER_APP_NAME        = "app_tools"                # Used by email templates

    APP_NAME = "Flask-User starter app"
    # Flask-User settings
    USER_APP_NAME = APP_NAME
    USER_ENABLE_CHANGE_PASSWORD = True  # Allow users to change their password
    USER_ENABLE_CHANGE_USERNAME = False  # Allow users to change their username
    USER_ENABLE_CONFIRM_EMAIL = True  # Force users to confirm their email
    USER_ENABLE_FORGOT_PASSWORD = True  # Allow users to reset their passwords
    USER_ENABLE_EMAIL = True  # Register with Email
    USER_ENABLE_REGISTRATION = True  # Allow new users to register
    USER_REQUIRE_RETYPE_PASSWORD = True  # Prompt for `retype password` in:
    USER_ENABLE_USERNAME = False  # Register and Login with username
    USER_AFTER_LOGIN_ENDPOINT = 'user_id'
    USER_AFTER_LOGOUT_ENDPOINT = 'login'

    






class DevelopementConfig(BaseConfig):
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DEVELOPMENT_DATABASE_URI') or  \
        #'mysql+pymysql://root:pass@localhost/flask_app_db'
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost:5432/tools_admin"
    

class TestingConfig(BaseConfig):
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DATABASE_URI') or \
                              #'mysql+pymysql://root:pass@localhost/flask_app_db'    
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost:5432/tools_admin"

class ProductionConfig(BaseConfig):
    DEBUG = False
    #SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DATABASE_URI') or  \
        #'mysql+pymysql://root:pass@localhost/flask_app_db'