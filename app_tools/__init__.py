from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Command, Shell
#from flask_login import LoginManager
import os, config
from flask_babel import Babel

# create application instance
app = Flask(__name__)
app.config.from_object(os.environ.get('FLASK_ENV') or 'config.DevelopementConfig')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

MAX_CONTENT_LENGTH = 1024 * 1024

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
# Initialize Flask-BabelEx
babel = Babel(app)

# initializes extensions
db = SQLAlchemy(app)
email = Mail(app)


migrate = Migrate(app, db)
#login_manager = LoginManager(app)
#login_manager.login_view = 'login'
#login_manager.login_message = 'You Must Login to Access This Page!'

# Flask settings
#CSRF_ENABLED = True

#upload settings
#app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
#app.config['ALLOWED_EXTENSIONS'] = ['jpg', 'pdf', 'png', 'jpeg', 'txt']
#app.config['UPLOAD_PATH'] = 'uploads'




# import views
from . import views
# from . import forum_views
# from . import admin_views