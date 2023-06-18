from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegisterForm(FlaskForm):
    email = StringField('Email' ,
                        validators=[
                            DataRequired(),
                            Email()
                        ]
    )
    name = StringField('Name' ,
                        validators=[
                            DataRequired(),
                        ]
    )
    password1 = PasswordField('Password' ,
                              validators=[
                                  DataRequired(),
                              ]
    )
    password2 = PasswordField('Password Confirmation' , 
                              validators=[
                              DataRequired(),
                              EqualTo('password1')
                              ]
    )
    image = FileField('Profile Picture', validators=[
            FileRequired(),
            FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])    
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Length(min=2, max=20),
            Email()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField(
        'Login'
    )