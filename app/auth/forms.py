from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"class": "form-control",
                                                                               "placeholder": "Enter Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "form-control",
                                                                                 "placeholder": "Enter Password"})
    submit = SubmitField('Sign In', render_kw={
        "class": "btn btn-lg btn-primary btn-block btn-login text-uppercase font-weight-bold mb-2", "value": "Login"})


class ChangePasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],
                           render_kw={"placeholder": "Enter Username"})
    prev_password = PasswordField('Previous Password', validators=[DataRequired()],
                                  render_kw={"class": "form-control", "placeholder": "Enter Current Password"})
    new_password = PasswordField('New Password', validators=[DataRequired()],
                                 render_kw={"class": "form-control", "placeholder": "Enter New Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()],
                                     render_kw={"class": "form-control", "placeholder": "Confirm New Password"})
    submit = SubmitField('Change Password', render_kw={
        "class": "btn btn-lg btn-primary btn-block btn-login text-uppercase font-weight-bold mb-2", "value": "Change Password"})


class EditEvent(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired()],
                      render_kw={"readonly": "readonly", "class": "uneditable_input"})
    orig_date = DateField('Original Date', validators=[DataRequired()], format="%d/%m/%Y %H:%M",
                          render_kw={"readonly": "readonly", "class": "uneditable_input"})
    date = DateField('New Date', validators=[DataRequired()], format="%d/%m/%Y %H:%M",
                     render_kw={"placeholder": "eg 01/01/2020 18:00"})
    venue = StringField('Venue', validators=[DataRequired()],
                        render_kw={"placeholder": "Venue details"})
    link = StringField('Link', validators=[DataRequired()],
                       render_kw={"placeholder": "Ticket page"})
    on_the_door = BooleanField('On The Door?', validators=[DataRequired()], )
    sold_out = BooleanField('Sold Out?', validators=[DataRequired()], )
    submit = SubmitField('Save', render_kw={"class": "btn btn-primary", "value": "Save"})
    delete = SubmitField('Delete', render_kw={"class": "btn btn-danger", "value": "Delete"})


class NewEvent(FlaskForm):
    id = IntegerField('ID', validators=[DataRequired()],
                      render_kw={"readonly": "readonly", "class": "uneditable_input"})
    date = DateField('Date', validators=[DataRequired()], default=datetime.now(), format="%d/%m/%Y %H:%M",
                     render_kw={"placeholder": "eg 01/01/2020 18:00"})
    venue = StringField('Venue', validators=[DataRequired()],
                        render_kw={"placeholder": "Venue details"})
    link = StringField('Link', validators=[DataRequired()],
                       render_kw={"placeholder": "Ticket page"})
    on_the_door = BooleanField('On The Door?', validators=[DataRequired()], )
    sold_out = BooleanField('Sold Out?', validators=[DataRequired()], )
    submit = SubmitField('Save', render_kw={"class": "btn btn-primary", "value": "Save"})
