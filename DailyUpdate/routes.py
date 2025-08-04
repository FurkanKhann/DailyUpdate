# routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from models import User, NewsArticle, EmailLog
from app import db
from news_service import NewsService
from datetime import datetime, timedelta
import re

# Create Blueprint
main = Blueprint('main', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Home Routes
@main.route('/')
def home():
    """Home page"""
    total_subscribers = User.query.filter_by(is_active=True).count()
    recent_articles = NewsArticle.query.order_by(NewsArticle.date_fetched.desc()).limit(3).all()
    
    return render_template('index.html', 
                         total_subscribers=total_subscribers,
                         recent_articles=recent_articles)

# Subscription Routes
@main.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    """Handle user subscription"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        # Validation
        if not email:
            flash('Please enter an email address.', 'danger')
            return redirect(url_for('main.subscribe'))
        
        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('main.subscribe'))
        
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            
            if existing_user:
                if existing_user.is_active:
                    flash('This email is already subscribed! 📧', 'info')
                else:
                    # Reactivate subscription
                    existing_user.is_active = True
                    existing_user.date_subscribed = datetime.utcnow()
                    db.session.commit()
                    flash('Welcome back! Your subscription has been reactivated. 🎉', 'success')
            else:
                # Create new user
                new_user = User(email=email)
                db.session.add(new_user)
                db.session.commit()
                flash('Successfully subscribed to daily AI news! 🚀', 'success')
            
            return redirect(url_for('main.home'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again later.', 'danger')
            print(f"Subscription error: {e}")
            return redirect(url_for('main.subscribe'))
    
    return render_template('subscribe.html')

@main.route('/unsubscribe/<email>')
def unsubscribe(email):
    """Handle user unsubscription"""
    try:
        user = User.query.filter_by(email=email.lower()).first()
        
        if user and user.is_active:
            user.is_active = False
            db.session.commit()
            flash('Successfully unsubscribed from daily AI news. We\'ll miss you! 👋', 'info')
        elif user and not user.is_active:
            flash('This email is already unsubscribed.', 'info')
        else:
            flash('Email not found in our subscription list.', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during unsubscription.', 'danger')
        print(f"Unsubscription error: {e}")
    
    return redirect(url_for('main.home'))

# Email Preview Routes
@main.route('/preview-email')
def preview_email():
    """Preview how the email will look"""
    sample_articles = [
        {
            'title': 'Breakthrough in Large Language Models: New Architecture Achieves Human-Level Performance',
            'url': 'https://example.com/llm-breakthrough',
            'description': 'Researchers at MIT have developed a revolutionary neural network architecture that demonstrates human-level performance across multiple cognitive tasks, marking a significant milestone in artificial intelligence development.'
        },
        {
            'title': 'AI-Powered Drug Discovery Platform Reduces Development Time by 60%',
            'url': 'https://example.com/ai-drug-discovery',
            'description': 'A new AI system has successfully identified potential drug candidates for rare diseases in months rather than years, using advanced molecular modeling and machine learning algorithms to predict drug efficacy.'
        },
        {
            'title': 'OpenAI Releases Enhanced GPT Model with Improved Reasoning Capabilities',
            'url': 'https://example.com/gpt-enhanced',
            'description': 'The latest update introduces advanced reasoning mechanisms, better context understanding, and reduced hallucination rates, setting new benchmarks for conversational AI performance.'
        }
    ]
    
    return render_template('email_template.html', 
                         articles=sample_articles, 
                         preview=True,
                         preview_date=datetime.now().strftime('%A, %B %d, %Y'))

# API Routes
@main.route('/api/stats')
def api_stats():
    """API endpoint for subscription statistics"""
    try:
        total_subscribers = User.query.filter_by(is_active=True).count()
        total_emails_sent = EmailLog.query.filter_by(status='sent').count()
        recent_subscribers = User.query.filter(
            User.date_subscribed >= datetime.utcnow() - timedelta(days=7)
        ).filter_by(is_active=True).count()
        
        latest_articles = NewsArticle.query.order_by(
            NewsArticle.date_fetched.desc()
        ).limit(5).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_subscribers': total_subscribers,
                'total_emails_sent': total_emails_sent,
                'recent_subscribers': recent_subscribers,
                'latest_articles': [article.to_dict() for article in latest_articles]
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/subscribe', methods=['POST'])
def api_subscribe():
    """API endpoint for subscription"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email or not validate_email(email):
            return jsonify({
                'success': False,
                'error': 'Invalid email address'
            }), 400
        
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user and existing_user.is_active:
            return jsonify({
                'success': False,
                'error': 'Email already subscribed'
            }), 400
        
        if existing_user and not existing_user.is_active:
            existing_user.is_active = True
            existing_user.date_subscribed = datetime.utcnow()
        else:
            existing_user = User(email=email)
            db.session.add(existing_user)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Successfully subscribed to daily AI news!'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'An error occurred during subscription'
        }), 500

# Test Routes
@main.route('/test-news')
def test_news():
    """Test news fetching"""
    try:
        news_service = NewsService()
        articles = news_service.fetch_ai_news()
        
        return jsonify({
            'success': True,
            'articles_count': len(articles),
            'articles': articles
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/test-email')
def test_email():
    """Test email functionality"""
    try:
        from email_service import test_email_config
        
        is_valid, message = test_email_config()
        
        return jsonify({
            'success': is_valid,
            'message': message
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Manual test route for immediate email sending
@main.route('/test-send-now')
def test_send_now():
    """Manually trigger email sending for immediate testing"""
    try:
        from news_service import NewsService
        from email_service import send_news_email
        from models import User
        
        # Get all active users
        users = User.query.filter_by(is_active=True).all()
        
        if not users:
            return jsonify({
                'success': False,
                'message': 'No active subscribers found. Subscribe first at the homepage!'
            })
        
        # Get news articles
        news_service = NewsService()
        articles = news_service.fetch_ai_news()
        
        if not articles:
            articles = news_service.get_fallback_news()
        
        # Send to all users
        results = []
        for user in users:
            success = send_news_email(user.email, articles)
            results.append({
                'email': user.email,
                'success': success
            })
        
        return jsonify({
            'success': True,
            'message': f'Sent emails to {len(users)} subscribers',
            'results': results,
            'articles_count': len(articles),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Admin Routes (Basic)
@main.route('/admin')
def admin_dashboard():
    """Basic admin dashboard"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        inactive_users = total_users - active_users
        
        recent_subscribers = User.query.order_by(
            User.date_subscribed.desc()
        ).limit(10).all()
        
        total_articles = NewsArticle.query.count()
        recent_articles = NewsArticle.query.order_by(
            NewsArticle.date_fetched.desc()
        ).limit(5).all()
        
        email_stats = {
            'total_sent': EmailLog.query.filter_by(status='sent').count(),
            'total_failed': EmailLog.query.filter_by(status='failed').count(),
            'last_batch': EmailLog.query.order_by(EmailLog.email_sent_at.desc()).first()
        }
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'total_articles': total_articles,
                'email_stats': {
                    'total_sent': email_stats['total_sent'],
                    'total_failed': email_stats['total_failed'],
                    'last_batch_time': email_stats['last_batch'].email_sent_at.isoformat() if email_stats['last_batch'] else None
                }
            },
            'recent_subscribers': [user.to_dict() for user in recent_subscribers],
            'recent_articles': [article.to_dict() for article in recent_articles]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error Handlers
@main.errorhandler(404)
def not_found_error(error):
    return render_template('index.html'), 404

@main.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('index.html'), 500

# Health Check Route
@main.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500
