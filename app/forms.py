
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Client
from wtforms.fields import HiddenField
from wtforms.fields import DateField
from wtforms.validators import Optional
from app.models import User



def client_choices():
    return Client.query.all()

class ClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    business_category = StringField('Business Category', validators=[DataRequired()])
    social_media_handles = StringField('Social Media Handles', validators=[DataRequired()])
    goals = TextAreaField('Goals', validators=[DataRequired()])
    specific_requests = TextAreaField('Specific Requests', validators=[DataRequired()])
    submit = SubmitField('Add Client')

class OnboardingTaskForm(FlaskForm):
    task_name = StringField('Task Name', validators=[DataRequired()])
    responsible = StringField('Responsible', validators=[DataRequired()])
    deadline = StringField('Deadline', validators=[DataRequired()])
    submit = SubmitField('Add Task')

class ContentIdeaForm(FlaskForm):
    idea_source = StringField('Idea Source', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    link = StringField('Link', validators=[DataRequired()])
    sound = StringField('Sound', validators=[DataRequired()])
    status = StringField('Status', validators=[DataRequired()])
    submit = SubmitField('Add Content Idea')

class MetricForm(FlaskForm):
    platform = StringField('Platform', validators=[DataRequired()])
    post_date = StringField('Post Date', validators=[DataRequired()])
    views = IntegerField('Views', validators=[DataRequired()])
    likes = IntegerField('Likes', validators=[DataRequired()])
    comments = IntegerField('Comments', validators=[DataRequired()])
    shares = IntegerField('Shares', validators=[DataRequired()])
    submit = SubmitField('Add Metric')



class TaskForm(FlaskForm):
    worker_email = SelectField('Worker Email', validators=[DataRequired()])
    client_id = SelectField('Client', validators=[DataRequired()], coerce=int)
    task_description = TextAreaField('Task Description', validators=[DataRequired()])
    deadline = DateField('Deadline', validators=[DataRequired()])
    submit = SubmitField('Assign Task')


    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.worker_email.choices = [(worker.email, worker.name) for worker in User.query.filter_by(is_manager=False).all()]

class TaskSubmissionForm(FlaskForm):
    completion_description = TextAreaField('Completion Description', validators=[DataRequired()])
    completion_link = StringField('Completion Link', validators=[DataRequired()])
    submit = SubmitField('Submit Task')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    name = StringField('Name', validators=[DataRequired(), Length(max=150)])
    manager_password = PasswordField('Manager Password', validators=[Length(max=150)])
    submit = SubmitField('Register')


