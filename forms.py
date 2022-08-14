from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, URL, Email, EqualTo, Length
from flask_ckeditor import CKEditorField

##WTForm
class RegisterForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    email = EmailField("Email:", validators=[DataRequired(), Email()])
    password = PasswordField("Password:", validators=[DataRequired(), Length(min=5)], id="password")
    confirm_password = PasswordField("Confirm Password:", validators=[DataRequired(), EqualTo('password', message="Passwords don't match")],
                                     id="conpassword")
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = EmailField("Email:", validators=[DataRequired(), Email()])
    password = PasswordField("Password:", validators=[DataRequired(), Length(min=5)], id="password")
    submit = SubmitField("Log In")


class CommentForm(FlaskForm):
    comment = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Add comment")