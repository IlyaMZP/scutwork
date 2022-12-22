from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, EqualTo, Regexp

from scutwork.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 30),
                                                   Regexp('^[a-zA-Z0-9-_]*$',
                                                          message='The username should contain only a-z, A-Z and 0-9.')])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 64)])
    username = StringField('Username', validators=[DataRequired(), Length(1, 30),
                                                   Regexp('^[a-zA-Z0-9-_]*$',
                                                          message='The username should contain only a-z, A-Z and 0-9.')])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(6, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    group = StringField('Group', validators=[Length(0, 128)])
    submit = SubmitField()
