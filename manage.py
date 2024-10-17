import sys
import os

# Add the project directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from app.models import User, Client, OnboardingTask, ContentIdea, Metric, Task


# Create the database and tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully.")
