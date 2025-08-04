# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
mail = Mail()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ai_news.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Email configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
    app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
    
    # Initialize extensions with app
    db.init_app(app)
    mail.init_app(app)
    
    # Import and register routes
    from routes import main
    app.register_blueprint(main)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"⚠️  Database creation warning: {e}")
    
    return app

# For backward compatibility and direct running
app = None

def get_app():
    """Get or create app instance"""
    global app
    if app is None:
        app = create_app()
    return app

# Create app instance for direct imports
app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
