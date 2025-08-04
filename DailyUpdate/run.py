import os
import sys
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main application entry point"""
    try:
        # Import after loading environment variables
        from app import create_app
        from scheduler_service import start_scheduler
        
        print("🚀 Starting AI News Application...")
        
        # Create Flask application
        app = create_app()
        
        # Start background scheduler
        print("📅 Initializing scheduler...")
        scheduler = start_scheduler(app)
        
        # Get configuration from environment
        debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        port = int(os.environ.get('PORT', 5000))
        
        # FIXED: Use 0.0.0.0 for production (Render) and localhost for development
        host = os.environ.get('HOST', '0.0.0.0')  # Changed from 127.0.0.1
        
        print(f"📧 Email service: {app.config.get('MAIL_USERNAME', 'Not configured')}")
        print(f"🌐 Running on: http://{host}:{port}")
        print(f"🐛 Debug mode: {debug_mode}")
        print("=" * 50)
        
        # Run the Flask application
        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            use_reloader=False  # Prevent scheduler from starting twice
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required files are present")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Shutting down application...")
    except Exception as e:
        print(f"❌ Application error: {e}")
        return 1
    finally:
        # Shutdown scheduler gracefully
        try:
            if 'scheduler' in locals() and scheduler:
                scheduler.shutdown()
                print("📅 Scheduler shut down successfully")
        except:
            pass
        print("👋 Application stopped")
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
