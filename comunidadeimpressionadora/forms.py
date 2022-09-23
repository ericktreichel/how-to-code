from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from comunidadeimpressionadora.models import Usuario
from flask_login import current_user

class FormCriarConta(FlaskForm):

    username = StringField('Username', validators=[DataRequired(), Length(3, 25)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Password', validators=[Length(6, 20)])
    confirmacao_passwd = PasswordField('Re-enter the password', validators=[EqualTo('senha')])
    submit_create_button = SubmitField('Create account')

    def validate_email(self, email):
        email_existente = Usuario.query.filter_by(email=email.data).first()
        if email_existente:
            raise ValidationError('E-mail already registered. Log in, or try to sign up using another e-mail.')

    def validate_username(self, username):
        user_existente = Usuario.query.filter_by(username=username.data).first()
        if user_existente:
            raise ValidationError('Username already taken. Please choose a different username.')


class FormLogin(FlaskForm):

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Password', validators=[Length(6, 20)])
    lembrar_sessao = BooleanField('Remember me?')
    submit_login_button = SubmitField('Log in')


class FormEditProfile(FlaskForm):

    fullname = StringField('Full name', validators=[Length(0, 50)])
    username = StringField('Username', validators=[DataRequired(), Length(3, 25)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    birth_date = DateField('Birth date', format='%Y-%m-%d')
    profile_pic = FileField('Change Picture', [FileAllowed(['jpg', 'jpeg', 'png'], 'JPG, JPEG and PNG only!')], description='SEM')
    remove_pic = SelectField('', choices=['', "I don't want a picture"])
    curso_excel = BooleanField('Excel Av')
    curso_powerbi = BooleanField('Power BI')
    curso_python = BooleanField('Python')
    curso_sql = BooleanField('SQL')
    submit_edit_button = SubmitField('Apply changes')


    def validate_new_email(self, email):
        # verificando se ele alterou o email ou não
        if current_user.email != email.data:
            email_exists = Usuario.query.filter_by(email=email.data).first()
            if email_exists:
                raise ValidationError('E-mail already registered. Please choose another e-mail.')

    def validate_new_username(self, username):
        # verificando se ele alterou o email ou não
        if current_user.username != username.data:
            user_exists = Usuario.query.filter_by(email=username.data).first()
            if user_exists:
                raise ValidationError('Username already taken. Please choose a different one.')

class FormNewPost(FlaskForm):

    title = StringField('Post title:', render_kw={"placeholder": "up to 50 characters..."}, validators=[DataRequired(), Length(2,50)])
    body = TextAreaField('Body:', render_kw={"placeholder": "write up to 3000 characters here...", "rows": 5}, validators=[DataRequired(), Length(3,3000)])
    submit_button = SubmitField('Create')
    save_edits_button = SubmitField('Save Edits')
    testarea = TextAreaField()
