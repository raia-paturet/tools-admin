import os

from app_tools import app, db
from app_tools.models import User, Formation
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate
from flask_user import SQLAlchemyAdapter, UserManager

manager = Manager(app)

# these names will be available inside the shell without explicit import
def make_shell_context():
    return dict(app=app,  db=db, User=User, Formation=Formation)

manager.add_command('shell', Shell(make_context=make_shell_context))

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
user_manager = UserManager(db_adapter, app)
  # Initialize Flask-User
assert db_adapter is user_manager.db_adapter
assert user_manager is app.user_manager

if __name__ == '__main__':
    manager.run()