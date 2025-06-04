#!/usr/bin/env python3
"""
Quick Start WebSocket Server for CyberGuard AI
"""

import os
import json
import time
import random
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import eventlet

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

print("🚀 Starting CyberGuard AI Quick Server...")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cyberguard-demo-secret'

# Enable CORS
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

# Initialize SocketIO
socketio = SocketIO(
    app, 
    cors_allowed_origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
    async_mode='eventlet'
)

# Simple threat generator for demo
threat_types = ['SQL Injection', 'XSS Attack', 'Brute Force', 'Malware Upload', 'DDoS Attack']
severity_levels = ['low', 'medium', 'high', 'critical']

def generate_threat():
    """Generate a random threat for demo"""
    return {
        'id': f"threat_{int(time.time())}_{random.randint(1000, 9999)}",
        'timestamp': datetime.now().isoformat(),
        'threat_type': random.choice(threat_types),
        'severity': random.choice(severity_levels),
        'source_ip': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
        'target': f"server-{random.randint(1, 10)}.internal",
        'description': f"Suspicious activity detected",
        'threat_score': random.uniform(0.6, 0.95),
        'confidence': random.uniform(0.8, 0.99),
        'response_time_ms': random.uniform(1.0, 5.0),
        'blocked': random.choice([True, False])
    }

# ================== REST API ENDPOINTS ==================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'flask_api': 'online',
            'websocket_server': 'online',
            'real_time_service': 'online'
        },
        'version': '1.0.0-quick',
        'features': ['Real-time threat detection', 'WebSocket monitoring']
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_log():
    """Analyze log entry"""
    try:
        data = request.get_json()
        log_entry = data.get('log_entry', '')
        
        # Simple threat detection
        threat_detected = any(keyword in log_entry.lower() 
                            for keyword in ['select', 'union', 'drop', 'delete', 'script', 'alert', 'admin', 'password'])
        
        result = {
            'threat_detected': threat_detected,
            'threat_level': random.choice(['medium', 'high']) if threat_detected else 'low',
            'threat_score': random.uniform(0.6, 0.9) if threat_detected else random.uniform(0.1, 0.4),
            'confidence': random.uniform(0.8, 0.95),
            'inference_time_ms': random.uniform(1.0, 3.0),
            'features_extracted': random.randint(45, 55)
        }
        
        # Broadcast via WebSocket if threat detected
        if threat_detected:
            threat = generate_threat()
            socketio.emit('threat_alert', {'alert': threat}, namespace='/monitoring')
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e), 'threat_detected': False}), 500

@app.route('/api/dashboard', methods=['GET'])
def dashboard_data():
    """Get dashboard data"""
    return jsonify({
        'recent_threats': [generate_threat() for _ in range(5)],
        'statistics': {
            'total_threats': random.randint(50, 200),
            'threats_blocked': random.randint(30, 150),
            'detection_rate': random.uniform(75, 95),
            'active_sessions': random.randint(1, 5),
            'uptime_hours': random.uniform(1, 24),
            'average_response_time': random.uniform(1.5, 3.0)
        },
        'threat_distribution': {
            'SQL Injection': random.randint(10, 30),
            'XSS Attack': random.randint(5, 20),
            'Brute Force': random.randint(15, 35)
        },
        'system_performance': {
            'status': 'operational',
            'websocket_enabled': True
        }
    })

# ================== WEBSOCKET HANDLERS ==================

@socketio.on('connect', namespace='/monitoring')
def handle_connect():
    """Handle client connection"""
    print(f"🔌 Client connected: {request.sid}")
    emit('connection_status', {
        'status': 'connected',
        'message': 'Connected to CyberGuard AI real-time monitoring',
        'session_id': request.sid
    })

@socketio.on('disconnect', namespace='/monitoring')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"🔌 Client disconnected: {request.sid}")

@socketio.on('join_monitoring', namespace='/monitoring')
def handle_join_monitoring():
    """Handle joining monitoring room"""
    print(f"📊 Client joined monitoring: {request.sid}")
    emit('room_joined', {'room': 'monitoring_room'})

@socketio.on('manual_threat_analysis', namespace='/monitoring')
def handle_manual_analysis(data):
    """Handle manual threat analysis"""
    log_entry = data.get('log_entry', '')
    
    # Simple analysis
    threat_detected = any(keyword in log_entry.lower() 
                        for keyword in ['select', 'union', 'drop', 'script', 'admin'])
    
    result = {
        'threat_detected': threat_detected,
        'threat_level': random.choice(['medium', 'high']) if threat_detected else 'normal',
        'threat_score': random.uniform(0.6, 0.9) if threat_detected else random.uniform(0.1, 0.4),
        'confidence': random.uniform(0.8, 0.95),
        'inference_time_ms': random.uniform(1.0, 3.0),
        'log_entry': log_entry
    }
    
    emit('analysis_result', result)
    print(f"🔍 Manual analysis: {'THREAT' if threat_detected else 'SAFE'}")

# ================== BACKGROUND TASKS ==================

def broadcast_random_threats():
    """Broadcast random threats every 15-30 seconds"""
    while True:
        try:
            eventlet.sleep(random.uniform(15, 30))
            if random.random() < 0.4:  # 40% chance
                threat = generate_threat()
                socketio.emit('threat_alert', {'alert': threat}, namespace='/monitoring')
                print(f"🚨 Broadcasting threat: {threat['threat_type']} ({threat['severity']})")
        except Exception as e:
            print(f"❌ Error in threat broadcast: {e}")

def broadcast_system_metrics():
    """Broadcast system metrics every 5 seconds"""
    while True:
        try:
            eventlet.sleep(5)
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': random.uniform(20, 80),
                'memory_usage': random.uniform(40, 85),
                'network_io': {
                    'bytes_in': random.uniform(1000, 50000),
                    'bytes_out': random.uniform(500, 25000)
                },
                'active_connections': random.randint(1, 10),
                'threats_per_minute': random.randint(0, 15),
                'model_inference_time': random.uniform(1.5, 5.0),
                'queue_size': random.randint(0, 25)
            }
            socketio.emit('system_metrics_update', metrics, namespace='/monitoring')
        except Exception as e:
            print(f"❌ Error in metrics broadcast: {e}")

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🛡️  CYBERGUARD AI - QUICK START SERVER")
    print("="*70)
    print("🌐 API Server: http://localhost:5001")
    print("🔌 WebSocket: ws://localhost:5001/socket.io")
    print("📊 Monitoring: /monitoring namespace")
    print("="*70)
    print("🎯 Starting server with real-time features...")
    print("="*70 + "\n")
    
    # Start background tasks
    socketio.start_background_task(broadcast_random_threats)
    socketio.start_background_task(broadcast_system_metrics)
    
    # Start the server
    socketio.run(
        app,
        host='localhost',
        port=5001,
        debug=False,
        use_reloader=False
    ) 