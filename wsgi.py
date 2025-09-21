#!/usr/bin/env python3
import os
import sys

# إضافة المجلد الحالي إلى مسار Python
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    try:
        # استيراد التطبيق
        from app import app
        
        # تشغيل التطبيق
        port = int(os.environ.get("PORT", 8080))
        print(f"Starting Tax Declaration System on port {port}")
        app.run(host="0.0.0.0", port=port, debug=False)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # تطبيق اختبار بسيط
        from flask import Flask
        test_app = Flask(__name__)
        
        @test_app.route('/')
        def home():
            return '''
            <h1>Tax Declaration System - Debug Mode</h1>
            <p>Main app failed to start. Error:</p>
            <pre>{}</pre>
            <p>Check Railway logs for more details.</p>
            '''.format(str(e))
            
        port = int(os.environ.get("PORT", 8080))
        test_app.run(host="0.0.0.0", port=port, debug=False)
