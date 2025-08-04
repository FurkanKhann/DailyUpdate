# scheduler_service.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime
import atexit

def send_daily_news(app):
    """Function to send daily news to all active users"""
    with app.app_context():
        try:
            # Import inside function to avoid circular imports
            from models import User, EmailLog
            from app import db
            from news_service import NewsService
            from email_service import send_news_email
            
            print(f"📧 Starting daily news job at {datetime.now()}")
            
            # Get all active users
            users = User.query.filter_by(is_active=True).all()
            print(f"👥 Found {len(users)} active subscribers")
            
            if not users:
                print("ℹ️  No active subscribers found")
                return
            
            # Fetch latest AI news
            news_service = NewsService()
            news_articles = news_service.fetch_ai_news()
            
            if not news_articles:
                print("⚠️  No news articles available")
                return
            
            print(f"📰 Sending {len(news_articles)} articles to subscribers")
            
            # Track email sending
            successful_sends = 0
            failed_sends = 0
            
            # Send emails to all users
            for user in users:
                try:
                    success = send_news_email(user.email, news_articles)
                    
                    # Log email attempt
                    email_log = EmailLog(
                        user_id=user.id,
                        articles_count=len(news_articles),
                        status='sent' if success else 'failed'
                    )
                    
                    if success:
                        successful_sends += 1
                        user.last_email_sent = datetime.utcnow()
                        print(f"✅ News sent to {user.email}")
                    else:
                        failed_sends += 1
                        email_log.error_message = "Failed to send email"
                        print(f"❌ Failed to send to {user.email}")
                    
                    db.session.add(email_log)
                    
                except Exception as e:
                    failed_sends += 1
                    print(f"❌ Error sending to {user.email}: {e}")
                    
                    # Log the error
                    try:
                        error_log = EmailLog(
                            user_id=user.id,
                            articles_count=len(news_articles),
                            status='failed',
                            error_message=str(e)
                        )
                        db.session.add(error_log)
                    except:
                        pass
            
            # Commit all changes
            try:
                db.session.commit()
            except Exception as e:
                print(f"❌ Error committing to database: {e}")
                db.session.rollback()
            
            print(f"📊 Daily news job completed:")
            print(f"   ✅ Successful: {successful_sends}")
            print(f"   ❌ Failed: {failed_sends}")
            print(f"   📰 Articles: {len(news_articles)}")
            
        except Exception as e:
            print(f"❌ Error in send_daily_news: {e}")
            try:
                from app import db
                db.session.rollback()
            except:
                pass

def start_scheduler(app):
    """Start the background scheduler"""
    try:
        scheduler = BackgroundScheduler(daemon=True)
        
        # Schedule for 10:00 AM IST daily
        ist = pytz.timezone('Asia/Kolkata')
        
        scheduler.add_job(
            func=lambda: send_daily_news(app),
            trigger=CronTrigger(hour=22, minute=22, timezone=ist),
            id='daily_news_job',
            name='Send daily AI news at 10:00 AM IST',
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )
        
        # Optional: Test job (uncomment to test every 2 minutes)
        # scheduler.add_job(
        #     func=lambda: send_daily_news(app),
        #     trigger=CronTrigger(minute='*/2'),
        #     id='test_news_job',
        #     name='Test news job every 2 minutes',
        #     replace_existing=True
        # )
        
        scheduler.start()
        
        # Ensure scheduler shuts down when application exits
        atexit.register(lambda: scheduler.shutdown())
        
        print("✅ Scheduler started successfully")
        print("⏰ Daily news scheduled for 10:00 AM IST")
        
        return scheduler
        
    except Exception as e:
        print(f"❌ Error starting scheduler: {e}")
        return None

