from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150))
    is_manager = db.Column(db.Boolean, default=False)
    tasks_assigned = db.relationship('Task', backref='manager', lazy=True, foreign_keys='Task.manager_id')
    tasks_working_on = db.relationship('Task', backref='assigned_worker', lazy=True, foreign_keys='Task.worker_id')

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150))
    contact_number = db.Column(db.String(50))
    business_category = db.Column(db.String(100))
    social_media_handles = db.Column(db.String(150))
    goals = db.Column(db.String(250))
    specific_requests = db.Column(db.String(250))
    status = db.Column(db.String(50))  # Add this line to ensure status column is present
    onboarding_tasks = db.relationship('OnboardingTask', backref='client', lazy=True)
    content_ideas = db.relationship('ContentIdea', backref='client', lazy=True)
    metrics = db.relationship('Metric', backref='client', lazy=True)

class OnboardingTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    task_name = db.Column(db.String(150))
    responsible = db.Column(db.String(50))
    deadline = db.Column(db.String(50))

class ContentIdea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    idea_source = db.Column(db.String(100))
    description = db.Column(db.String(250))
    link = db.Column(db.String(250))
    sound = db.Column(db.String(250))
    status = db.Column(db.String(50))

class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    platform = db.Column(db.String(100))
    post_date = db.Column(db.String(50))
    views = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    comments = db.Column(db.Integer)
    shares = db.Column(db.Integer)

from datetime import datetime, timezone
from app import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    task_description = db.Column(db.String(255), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    completion_description = db.Column(db.Text)
    completion_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    in_progress_time = db.Column(db.DateTime)
    completion_time = db.Column(db.DateTime)




class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(250))
    type = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    read = db.Column(db.Boolean, default=False)
