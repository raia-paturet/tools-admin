
from flask_wtf import FlaskForm
from wtforms import Form, ValidationError
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from app_tools.models import User
from flask_wtf.file import FileField




class User_createForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('signup')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CheckEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Check')

    def validate_email2(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Please use a different email address.')

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('signup')



class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('signup')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Please use a different email address.')



class EditProfileForm(FlaskForm):
    """User  profil  Form """
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('lastname', validators=[DataRequired()])
    address = StringField('address', validators=[Length(min=0, max=140), DataRequired()])
    city_code = IntegerField('postal', validators=[DataRequired()])
    city = StringField('city', validators=[Length(min=0, max=140),DataRequired()])
    phone = IntegerField('Phone', validators=[DataRequired()])
    submit = SubmitField('Submit')


    
class LoginForm(FlaskForm):
    """User Log-in Form."""
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message='Enter a valid email.')
        ]
    )
    password = PasswordField(
        'Password',
         validators=[DataRequired()]
    )
    submit = SubmitField('Log In')

    