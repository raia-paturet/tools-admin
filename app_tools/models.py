from app_tools import db, app
from datetime import datetime
#from flask_login import (LoginManager, UserMixin, login_required,
                          #login_user, current_user, logout_user)
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from flask_user import login_required, SQLAlchemyAdapter, UserManager, UserMixin


class Folder_type(db.Model):
    __tablename__ = 'folder_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)

    # Relationships
    folder_promo = db.relationship('Folder_promo', backref='folder_type', uselist=False)
    document_folder = db.relationship('Document_folder', backref='folder_type', uselist=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<folder_type {self.name}>"

class Formation(db.Model):
    __tablename__ = 'formation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    # Relationships
    promo = db.relationship('Promo', backref='formation', uselist=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<formation {self.name}>"


class Step(enum.Enum):
  step1 = 'Candidat'
  step2 = 'Etudiant'
  step3 = 'Diplomé'
  step4 = 'Abandon'

  def __str__(self):
        return self.name  # value string

class Promo(db.Model):
    __tablename__ = 'promo'
    id = db.Column(db.Integer, primary_key=True)
    iteration = db.Column(db.String(64), nullable=False)
    formation_id = db.Column(db.Integer(), db.ForeignKey('formation.id'))

    # Relationships
    folder_promo = db.relationship('Folder_promo', backref='promo', uselist=False)
    promo_user = db.relationship('Promo_user', backref='promo', uselist=False)

    def __init__(self, iteration, formation_id):
        self.iteration = iteration
        self.formation_id = formation_id

    # def __repr__(self):
    #     #return "{}_{}".format(self.formation.name, self.iteration)
    #     return f"{self.formation.name}_{self.iteration}"
    def __repr__(self):
        return f"{self.formation_id}_{self.iteration}"



class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    email = db.Column(db.Unicode(255), nullable=False, server_default=u'', unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=True, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    promo_user = db.relationship('Promo_user', backref='users')
    user_detail = db.relationship('User_detail', backref='users', uselist=False)
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))
    document_user = db.relationship('Document_user', backref='users')
    #folder_user = db.relationship('Folder_user', backref='users')

    #def is_authenticated(self):
        #return True

    def get_id(self):
        return int(self.id)
#defini les attributs il est execute que lors de la creation d'objets
    def __init__(self, email):
        self.email = email

# lors du print du user 
    def __repr__(self):
        return "<{}:{}>".format(self.id, self.email)




# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))



class User_detail(db.Model, UserMixin):   
    __tablename__ = 'user_detail'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    firstname = db.Column(db.String(100), nullable=True)
    lastname = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(100), nullable=True)
    city_code = db.Column(db.Integer(), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.Integer(), nullable=True)

    def __repr__(self):
        return f"<User_detail {self.id}{self.lastname}>"




class Promo_user(db.Model):
    __tablename__ = 'promo_user'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    promo_id = db.Column(db.Integer(), db.ForeignKey('promo.id'))
    user_step = db.Column(db.Enum(Step), nullable=True)

    def __repr__(self):
        return '<promo_user {}>'.format(self.user_id)

# Define the status_document data-model
class Status(enum.Enum):
  status1 = 'à envoyer'
  status2 = 'en attente de validation'
  status3 = 'validé'
  status4 = 'non conforme'
  status5 = 'non concerné'

# Define the documnets data-model
class Document_type(db.Model):
    __tablename__ = 'document_type'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(200))

    # Relationships
    document_folder = db.relationship('Document_folder', backref='document_type', uselist=False)
    document_user = db.relationship('Document_user', backref='document_type', uselist=False)

# Define the documents of a folder data-model
class Document_folder(db.Model):
    __tablename__ = 'document_folder'
    id = db.Column(db.Integer(), primary_key=True)
    document_type_id = db.Column(db.Integer(), db.ForeignKey('document_type.id'))
    folder_type_id = db.Column(db.Integer(), db.ForeignKey('folder_type.id'))


    def __init__(self, document_type_id, folder_type_id):
        self.document_type_id = document_type_id
        self.folder_type_id = folder_type_id

# Define the folders of a user data-model
class Folder_promo(db.Model):
    __tablename__ = 'folder_promo'
    id = db.Column(db.Integer, primary_key=True)
    promo_id = db.Column(db.Integer(), db.ForeignKey('promo.id'))
    folder_type_id = db.Column(db.Integer(), db.ForeignKey('folder_type.id'))

# Define the documents of a user data-model
class Document_user(db.Model):
    __tablename__ = 'document_user'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    document_type_id = db.Column(db.Integer(), db.ForeignKey('document_type.id'))
    file = db.Column(db.String(100), unique=True, nullable=True)
    datetime = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.Enum(Status), server_default="à envoyer")








   