from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from app.models.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
              'Usernames must start with a letter and can only contain '
              'letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class ContactForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email', validators=[Length(0, 120), Email()])
    phone = StringField('Phone', validators=[Length(0, 20)])
    company = StringField('Company', validators=[Length(0, 100)])
    position = StringField('Position', validators=[Length(0, 100)])
    linkedin_url = StringField('LinkedIn URL', validators=[Length(0, 255)])
    notes = TextAreaField('Notes')
    tags = StringField('Tags (comma separated)')
    submit = SubmitField('Save Contact')

class InteractionForm(FlaskForm):
    interaction_type = SelectField('Type', choices=[
        ('email', 'Email'),
        ('call', 'Call'),
        ('meeting', 'Meeting'),
        ('note', 'Note')
    ])
    notes = TextAreaField('Notes', validators=[DataRequired()])
    submit = SubmitField('Add Interaction') 