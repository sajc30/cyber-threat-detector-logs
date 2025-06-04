#!/usr/bin/env python3

import json
import random
import re
import time
import threading
from datetime import datetime
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

print("🚀 WebSocket Server Starting...")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cyberguard-secret-key'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Global state
active_connections = {}
monitoring_active = False
log_stream_thread = None

def detect_threats(log_entry):
    """Analyze log entry for cybersecurity threats"""
    threats = []
    threat_score = 0.0
    confidence = 0.0
    
    # SQL Injection patterns
    sql_patterns = [
        r"(\bSELECT\b.*\bFROM\b)", 
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bOR\b.*1\s*=\s*1)",
        r"(\bAND\b.*1\s*=\s*1)",
        r"(1\s*=\s*1)",
        r"(admin\s*=\s*1)",
        r"('.*OR.*'.*=.*')",
        r"(--|\#|\/\*)"
    ]
    
    # XSS patterns
    xss_patterns = [
        r"<script[^>]*>",
        r"javascript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"alert\s*\(",
        r"document\.cookie"
    ]
    
    # Directory traversal patterns
    traversal_patterns = [
        r"\.\.\/",
        r"\.\.\\",
        r"\/etc\/passwd",
        r"\/windows\/system32"
    ]
    
    # Brute force patterns
    brute_force_patterns = [
        r"(failed.*login.*attempt)",
        r"(authentication.*failed)",
        r"(invalid.*password)",
        r"(login.*failed.*user)"
    ]
    
    log_lower = log_entry.lower()
    
    # Check SQL Injection
    for pattern in sql_patterns:
        if re.search(pattern, log_lower, re.IGNORECASE):
            threats.append("SQL Injection")
            threat_score += 0.8
            confidence += 0.9
            break
    
    # Check XSS
    for pattern in xss_patterns:
        if re.search(pattern, log_lower, re.IGNORECASE):
            threats.append("Cross-Site Scripting (XSS)")
            threat_score += 0.7
            confidence += 0.85
            break
    
    # Check Directory Traversal
    for pattern in traversal_patterns:
        if re.search(pattern, log_lower, re.IGNORECASE):
            threats.append("Directory Traversal")
            threat_score += 0.6
            confidence += 0.8
            break
    
    # Check Brute Force
    for pattern in brute_force_patterns:
        if re.search(pattern, log_lower, re.IGNORECASE):
            threats.append("Brute Force Attack")
            threat_score += 0.5
            confidence += 0.75
            break
    
    # Normalize scores
    threat_score = min(threat_score, 1.0)
    confidence = min(confidence / len([sql_patterns, xss_patterns, traversal_patterns, brute_force_patterns]), 1.0)
    
    # Determine threat level
    if threat_score >= 0.7:
        threat_level = "high"
    elif threat_score >= 0.4:
        threat_level = "medium"
    elif threat_score >= 0.1:
        threat_level = "low"
    else:
        threat_level = "none"
    
    return {
        'threat_detected': len(threats) > 0,
        'threat_types': threats,
        'threat_level': threat_level,
        'threat_score': round(threat_score, 3),
        'confidence': round(confidence, 3),
        'analysis_details': f"Analyzed for {len(sql_patterns + xss_patterns + traversal_patterns + brute_force_patterns)} threat patterns"
    }

# Simulated log entries for live streaming
SAMPLE_LOGS = [
    'GET /index.html HTTP/1.1 200 192.168.1.10',
    'POST /login HTTP/1.1 200 192.168.1.15',
    'GET /admin HTTP/1.1 404 192.168.1.100',
    'SELECT * FROM users WHERE id=1; DROP TABLE users;--',
    'Failed login attempt for user admin from 192.168.1.50',
    'Normal web request GET /api/data HTTP/1.1 200',
    'POST /upload HTTP/1.1 200 application/json',
    'Multiple failed SSH attempts from 10.0.0.45',
    'Malicious file upload attempt: exploit.php',
    'User successfully logged in: john.doe',
    '<script>alert("XSS attack")</script>',
    'SELECT password FROM admin_users WHERE username="admin"',
    '../../../etc/passwd directory traversal attempt',
    'Normal user activity: file download completed',
    'GET /api/users HTTP/1.1 200 192.168.1.25',
    'Database backup completed successfully',
    'Firewall blocked suspicious traffic from 10.0.0.99',
    'System health check passed',
    'New user registration: alice@company.com',
    'Session expired for user: bob123',
]

def generate_live_logs():
    """Generate and stream live log entries"""
    global monitoring_active
    
    while monitoring_active:
        try:
            # Generate a random log entry
            log_entry = random.choice(SAMPLE_LOGS)
            
            # Add realistic timestamp and IP variations
            timestamp = datetime.now().isoformat()
            source_ip = f"192.168.1.{random.randint(10, 200)}"
            
            # Enhanced log entry with metadata
            enhanced_log = {
                'id': f"log_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
                'timestamp': timestamp,
                'content': log_entry,
                'source_ip': source_ip,
                'user_agent': 'Mozilla/5.0 (compatible; WebBot/1.0)',
                'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                'status_code': random.choice([200, 404, 401, 403, 500]),
                'response_time_ms': round(random.uniform(10, 500), 2)
            }
            
            # Analyze for threats
            start_time = time.time()
            analysis_result = detect_threats(log_entry)
            end_time = time.time()
            
            analysis_result['inference_time_ms'] = round((end_time - start_time) * 1000, 2)
            analysis_result['timestamp'] = timestamp
            analysis_result['log_entry_length'] = len(log_entry)
            
            # Combine log and analysis
            live_log_data = {
                'log': enhanced_log,
                'analysis': analysis_result
            }
            
            # Emit to all connected clients
            socketio.emit('live_log', live_log_data, room='monitoring')
            
            # Emit threat alert if detected
            if analysis_result['threat_detected']:
                threat_alert = {
                    'id': enhanced_log['id'],
                    'timestamp': timestamp,
                    'threat_type': ', '.join(analysis_result['threat_types']),
                    'severity': analysis_result['threat_level'],
                    'source_ip': source_ip,
                    'target': 'Application Server',
                    'description': f"Detected {', '.join(analysis_result['threat_types'])} in log entry",
                    'threat_score': analysis_result['threat_score'],
                    'confidence': analysis_result['confidence'],
                    'response_time_ms': analysis_result['inference_time_ms'],
                    'blocked': analysis_result['threat_score'] > 0.6,
                    'investigated': False,
                    'log_content': log_entry
                }
                
                socketio.emit('threat_alert', threat_alert, room='monitoring')
                print(f"🚨 Threat Alert: {threat_alert['threat_type']} - {threat_alert['severity']}")
            
            # Wait between logs (2-8 seconds for realistic pace)
            time.sleep(random.uniform(2, 8))
            
        except Exception as e:
            print(f"❌ Error in log generation: {e}")
            time.sleep(5)

# Flask routes (for compatibility)
@app.route('/api/health')
def health():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'CyberGuard AI WebSocket Server Running',
        'active_connections': len(active_connections),
        'monitoring_active': monitoring_active
    }

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        start_time = time.time()
        
        data = request.get_json()
        if not data or 'log_entry' not in data:
            return {'error': 'Missing log_entry in request'}, 400
        
        log_entry = data['log_entry']
        if not log_entry.strip():
            return {'error': 'Empty log entry'}, 400
        
        # Perform threat analysis
        result = detect_threats(log_entry)
        
        # Calculate inference time
        end_time = time.time()
        inference_time_ms = (end_time - start_time) * 1000
        
        result['timestamp'] = datetime.now().isoformat()
        result['log_entry_length'] = len(log_entry)
        result['inference_time_ms'] = round(inference_time_ms, 2)
        
        return result
    
    except Exception as e:
        return {'error': f'Analysis failed: {str(e)}'}, 500

# WebSocket event handlers
@socketio.event
def connect():
    print(f"🔌 Client connected: {request.sid}")
    active_connections[request.sid] = {
        'connected_at': datetime.now().isoformat(),
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    }
    
    emit('connected', {
        'session_id': request.sid,
        'status': 'connected',
        'timestamp': datetime.now().isoformat(),
        'message': 'Welcome to CyberGuard AI Real-Time Monitoring'
    })

@socketio.event
def disconnect():
    print(f"🔌 Client disconnected: {request.sid}")
    if request.sid in active_connections:
        del active_connections[request.sid]
    leave_room('monitoring')

@socketio.event
def join_monitoring(data):
    print(f"📊 Client {request.sid} joining monitoring room")
    join_room('monitoring')
    
    emit('monitoring_joined', {
        'status': 'success',
        'room': 'monitoring',
        'timestamp': datetime.now().isoformat(),
        'message': 'Successfully joined real-time monitoring'
    })

@socketio.event
def start_monitoring(data):
    global monitoring_active, log_stream_thread
    
    print("🚀 Starting live log monitoring...")
    
    if not monitoring_active:
        monitoring_active = True
        
        if log_stream_thread is None or not log_stream_thread.is_alive():
            log_stream_thread = threading.Thread(target=generate_live_logs)
            log_stream_thread.daemon = True
            log_stream_thread.start()
        
        socketio.emit('monitoring_status', {
            'status': 'started',
            'timestamp': datetime.now().isoformat(),
            'message': 'Live log monitoring started'
        }, room='monitoring')
        
        emit('monitoring_started', {
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
    else:
        emit('monitoring_already_active', {
            'status': 'info',
            'message': 'Monitoring is already active'
        })

@socketio.event
def stop_monitoring(data):
    global monitoring_active
    
    print("🛑 Stopping live log monitoring...")
    monitoring_active = False
    
    socketio.emit('monitoring_status', {
        'status': 'stopped',
        'timestamp': datetime.now().isoformat(),
        'message': 'Live log monitoring stopped'
    }, room='monitoring')
    
    emit('monitoring_stopped', {
        'status': 'success',
        'timestamp': datetime.now().isoformat()
    })

@socketio.event
def analyze_manual_log(data):
    print(f"🔍 Manual log analysis requested: {data.get('log_entry', '')[:50]}...")
    
    try:
        log_entry = data.get('log_entry', '')
        if not log_entry.strip():
            emit('analysis_error', {'error': 'Empty log entry'})
            return
        
        start_time = time.time()
        result = detect_threats(log_entry)
        end_time = time.time()
        
        result['inference_time_ms'] = round((end_time - start_time) * 1000, 2)
        result['timestamp'] = datetime.now().isoformat()
        result['log_entry_length'] = len(log_entry)
        
        emit('analysis_result', result)
        
    except Exception as e:
        emit('analysis_error', {'error': str(e)})

if __name__ == '__main__':
    print("🌐 Starting WebSocket server on http://localhost:5001")
    socketio.run(app, host='localhost', port=5001, debug=False) 