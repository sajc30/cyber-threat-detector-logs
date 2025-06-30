#!/usr/bin/env python3

print("🧪 Testing server startup...")

try:
    print("1. Importing modules...")
    from config import Config
    from ai_threat_detector import AIThreatDetector
    from database import init_db
    from flask import Flask
    from flask_socketio import SocketIO
    import eventlet
    import os
    print("✅ All imports successful")

    print("2. Creating Flask app...")
    app = Flask(__name__)
    app.config.from_object(Config)
    print("✅ Flask app created")

    print("3. Creating SocketIO...")
    socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000"], async_mode='eventlet')
    print("✅ SocketIO created")

    print("4. Initializing database...")
    init_db()
    print("✅ Database initialized")

    print("5. Starting server...")
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    socketio.run(app, host='localhost', port=5001, debug=debug_mode)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 