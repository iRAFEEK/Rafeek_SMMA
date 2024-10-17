from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
print(f"DATABASE_URI: {os.getenv('DATABASE_URI')}")

class Config:
    SECRET_KEY = 'Test'  # Replace with the key you generated
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
