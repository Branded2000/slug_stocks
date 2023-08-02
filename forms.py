from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    username = StringField('username', validators =[DataRequired()])
    email = StringField('Email', validators=[DataRequired(),Email()])
    password1 = PasswordField('Password', validators = [DataRequired()])
    password2 = PasswordField('Confirm Password', validators = [DataRequired(),EqualTo('password1')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me',validators= [DataRequired()])
    submit = SubmitField('Login')

# Create form to search for stocks on Market.html page
# using API from financial modeling prep
class SearchForm(FlaskForm):
    # Search for stock
    search = StringField('Search For a Ticker', validators=[DataRequired()])
    submit = SubmitField('Search')

# Creates form to take input from a user for their about_me
class EditProfileForm(FlaskForm):
    about_me = TextAreaField('About me', validators=[Length(min=0, max=200)])
    favorite_stocks = TextAreaField('Favorite stocks', validators=[Length(min=0, max=200)])
    submit = SubmitField('Submit')