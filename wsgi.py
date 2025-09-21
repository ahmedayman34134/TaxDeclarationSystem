#!/usr/bin/env python3
import os
import sys

# إضافة المجلد الحالي إلى مسار Python
sys.path.insert(0, os.path.dirname(__file__))

print("Starting wsgi.py...")
print(f"Python path: {sys.path}")
print(f"Environment variables:")
print(f"PORT: {os.environ.get('PORT', 'Not set')}")
print(f"DATABASE_URL: {'Set' if os.environ.get('DATABASE_URL') else 'Not set'}")
print(f"SECRET_KEY: {'Set' if os.environ.get('SECRET_KEY') else 'Not set'}")

try:
    print("Importing app...")
    from app import app
    print("App imported successfully!")
    
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 8080))
        print(f"Starting app on port {port}")
        app.run(host="0.0.0.0", port=port, debug=False)
        
except Exception as e:
    print(f"Error starting app: {e}")
    import traceback
    traceback.print_exc()
    
    # محاولة إنشاء تطبيق بسيط للاختبار
    try:
        from flask import Flask
        test_app = Flask(__name__)
        
        @test_app.route('/')
        def test():
            return f"Test app working! Error was: {str(e)}"
            
        port = int(os.environ.get("PORT", 8080))
        print(f"Starting test app on port {port}")
        test_app.run(host="0.0.0.0", port=port, debug=False)
        
    except Exception as test_e:
        print(f"Even test app failed: {test_e}")
        sys.exit(1)
