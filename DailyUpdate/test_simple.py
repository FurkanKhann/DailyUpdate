# test_simple.py
import os
from dotenv import load_dotenv

print("🧪 Testing basic setup...")

# Test environment loading
load_dotenv()
print(f"✅ Environment loaded")

# Test imports
try:
    import app
    print("✅ app module imported")
    
    import models
    print("✅ models module imported")
    
    import news_service
    print("✅ news_service module imported")
    
    import email_service
    print("✅ email_service module imported")
    
    import scheduler_service
    print("✅ scheduler_service module imported")
    
    import routes
    print("✅ routes module imported")
    
    print("\n🎉 All basic tests passed!")
    print("You can now run: python run.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
