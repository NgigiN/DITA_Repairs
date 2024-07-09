from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app import db
import sqlalchemy as sa
from app.models import User


class LoginForm(FlaskForm):
    admission_number = StringField(
        'Admission Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    admission_number = StringField(
        'Admission Number', validators=[DataRequired()])
#     name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_admission_number(self, admission_number):
        user = db.session.scalar(sa.select(User).where(
            User.admission_number == admission_number.data))
        if user is not None:
            raise ValidationError('Please use a different admission number.')

    def validate_email(self, email):
        user = db.session.scalar(
            sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email')


class RepairsForm(FlaskForm):
    laptop_brand = StringField('Laptop Brand', validators=[DataRequired()])
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    admission_number = StringField(
        'Admission Number', validators=[DataRequired()])
    description = TextAreaField('Provide a detailed description of the problem you are experiencing with your laptop', validators=[
                                DataRequired(), Length(min=1, max=300)])
    submit = SubmitField('Submit')


class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
