#!/usr/bin/env python3
import os
import sys

# إضافة المجلد الحالي إلى مسار Python
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import app
    
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 8080))
        print(f"Starting app on port {port}")
        app.run(host="0.0.0.0", port=port, debug=False)
        
except Exception as e:
    print(f"Error starting app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
