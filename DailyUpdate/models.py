# models.py
from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    date_subscribed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_email_sent = db.Column(db.DateTime)
    
    def __repr__(self):
        return f"User('{self.email}', active={self.is_active})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'date_subscribed': self.date_subscribed,
            'is_active': self.is_active,
            'last_email_sent': self.last_email_sent
        }

class NewsArticle(db.Model):
    __tablename__ = 'news_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    url = db.Column(db.String(500), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100))
    published_at = db.Column(db.DateTime)
    date_fetched = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50), default='AI')
    
    def __repr__(self):
        return f"NewsArticle('{self.title[:50]}...')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'source': self.source,
            'published_at': self.published_at,
            'date_fetched': self.date_fetched,
            'category': self.category
        }

class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email_sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    articles_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='sent')  # sent, failed, pending
    error_message = db.Column(db.Text)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('email_logs', lazy=True))
    
    def __repr__(self):
        return f"EmailLog(user_id={self.user_id}, status='{self.status}')"
