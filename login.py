from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import sqlite3

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")
    signup = SubmitField("SignUp")
    
    # def validate_email(self, email):
    #     conn = sqlite3.connect("FinalProject.db")
    #     curs = conn.cursor()
    #     curs.execute("SELECT email FROM UserDim WHERE email = (?)", [email.data])
    #     valuemail = curs.fetchone()
    #     if valuemail is None:
    #         raise ValidationError("Email is not registered, please register.")
        
class SignUpForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_confirm = PasswordField("Password Confirm", validators=[DataRequired()])
    submit = SubmitField("SignUp")
    
    # def validate_and_create_user(self, name, email, password, password_confirm):
    #     conn = sqlite3.connect("FinalProject.db")
    #     curs = conn.cursor()
    #     curs.execute("SELECT email FROM UserDim WHERE email = (?)", [email.data])
    #     valuemail = curs.fetchone()
    #     if password != password_confirm:
    #         raise ValidationError("Password did not match")        
    #     elif valuemail is None:
    #         curs.execute("INSERT INTO UserDim(name, email, password) VALUES((?), (?), (?))", [name.data, email.data, password.data])
    #     else:
    #         raise ValidationError("Email is not registered, please register.")