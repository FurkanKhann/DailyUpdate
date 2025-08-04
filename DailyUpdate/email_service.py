# email_service.py
from flask import render_template
from flask_mail import Message
from app import mail
import threading
from datetime import datetime

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
            return True
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

def send_news_email(user_email, news_articles):
    """Send daily AI news email to user"""
    try:
        from flask import current_app
        
        if not current_app.config.get('MAIL_USERNAME'):
            print("⚠️  Email not configured, skipping send")
            return False
        
        msg = Message(
            subject='🤖 Your Daily AI News Update',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user_email]
        )
        
        # Get current date in a nice format
        current_date = datetime.now().strftime('%A, %B %d, %Y')
        
        # Use template for email content
        msg.html = render_template('email_template.html', 
                                 articles=news_articles, 
                                 user_email=user_email,
                                 current_date=current_date,
                                 preview=False)
        
        # Send email in background thread
        thread = threading.Thread(
            target=send_async_email, 
            args=(current_app._get_current_object(), msg)
        )
        thread.start()
        
        return True
        
    except Exception as e:
        print(f"❌ Error preparing email for {user_email}: {e}")
        return False

def test_email_config():
    """Test email configuration"""
    try:
        from flask import current_app
        
        required_configs = ['MAIL_USERNAME', 'MAIL_PASSWORD']
        missing_configs = []
        
        for config in required_configs:
            if not current_app.config.get(config):
                missing_configs.append(config)
        
        if missing_configs:
            return False, f"Missing email configurations: {', '.join(missing_configs)}"
        
        return True, "Email configuration is valid"
        
    except Exception as e:
        return False, f"Email configuration error: {e}"
