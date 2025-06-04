#!/usr/bin/env python3
"""
CyberGuard AI - Advanced Cybersecurity Threat Detection System
Enhanced Flask REST API with Real-Time WebSocket Support
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Flask and related imports
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from flask_socketio import SocketIO
import eventlet

# Application modules
from config import Config
from ai_threat_detector import AIThreatDetector
from database import init_db, get_recent_threats, log_threat
from realtime_service import init_realtime_service, get_realtime_service
from websocket_handlers import register_websocket_handlers, register_general_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app with WebSocket support
app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS for WebSocket support
CORS(app, resources={
    r"/api/*": {"origins": [
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://frontend:3000",
        "http://ctd-frontend:3000",
        "http://192.168.65.1:3000",
        "file://", 
        "*"
    ]},
    r"/socket.io/*": {"origins": [
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://frontend:3000",
        "http://ctd-frontend:3000",
        "http://192.168.65.1:3000",
        "file://", 
        "*"
    ]},
    r"/*": {"origins": [
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://frontend:3000",
        "http://ctd-frontend:3000",
        "http://192.168.65.1:3000",
        "file://", 
        "*"
    ]}
})

# Initialize SocketIO with CORS support
socketio = SocketIO(
    app,
    cors_allowed_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://frontend:3000",
        "http://ctd-frontend:3000",
        "http://192.168.65.1:3000",
        "*"
    ],
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

# Initialize database
init_db()

# Initialize AI threat detector
try:
    threat_detector = AIThreatDetector()
    logger.info("✅ AI Threat Detector initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize AI Threat Detector: {e}")
    threat_detector = None

# Initialize real-time service
try:
    realtime_service = init_realtime_service(socketio)
    logger.info("✅ Real-time WebSocket service initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize real-time service: {e}")
    realtime_service = None

# Register WebSocket event handlers
register_websocket_handlers(socketio)
register_general_handlers(socketio)

# ==================== REST API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with system status"""
    try:
        rt_service = get_realtime_service()
        system_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'flask_api': 'online',
                'websocket_server': 'online' if socketio else 'offline',
                'real_time_service': 'online' if rt_service else 'offline',
                'ai_threat_detector': 'online' if threat_detector else 'offline',
                'database': 'online'
            },
            'version': '1.0.0',
            'features': [
                'Real-time threat detection',
                'WebSocket live monitoring', 
                'Multi-user collaboration',
                'AI-powered analysis',
                'Historical threat tracking'
            ]
        }
        
        if rt_service:
            system_status.update({
                'active_connections': len(rt_service.active_users),
                'total_threats_detected': rt_service.stats['total_threats_detected'],
                'uptime_hours': (datetime.now() - rt_service.stats['uptime_start']).total_seconds() / 3600
            })
        
        return jsonify(system_status), 200
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_log():
    """Enhanced log analysis with real-time broadcasting"""
    try:
        data = request.get_json()
        if not data or 'log_entry' not in data:
            return jsonify({'error': 'Missing log_entry in request body'}), 400
        
        log_entry = data['log_entry'].strip()
        if not log_entry:
            return jsonify({'error': 'Log entry cannot be empty'}), 400
        
        # Perform threat analysis
        if threat_detector:
            result = threat_detector.analyze_log(log_entry)
            
            # Broadcast through real-time service if available
            rt_service = get_realtime_service()
            if rt_service:
                result = rt_service.handle_threat_detection(log_entry, result)
                
            # Log threat to database if detected
            if result.get('threat_detected', False):
                log_threat(
                    log_entry=log_entry,
                    threat_level=result.get('threat_level', 'unknown'),
                    threat_score=result.get('threat_score', 0),
                    confidence=result.get('confidence', 0)
                )
            
            logger.info(f"Analysis completed: {'THREAT' if result.get('threat_detected') else 'SAFE'}")
            return jsonify(result), 200
            
        else:
            # Fallback analysis if AI detector not available
            mock_result = {
                'threat_detected': 'error' in log_entry.lower() or 'failed' in log_entry.lower(),
                'threat_level': 'low',
                'threat_score': 0.3,
                'confidence': 0.5,
                'inference_time_ms': 1.0,
                'features_extracted': 0,
                'message': 'AI detector unavailable - using basic keyword detection'
            }
            return jsonify(mock_result), 200
            
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({
            'error': f'Analysis failed: {str(e)}',
            'threat_detected': False
        }), 500

@app.route('/api/dashboard', methods=['GET'])
def dashboard_data():
    """Enhanced dashboard data with real-time statistics"""
    try:
        # Get recent threats from database
        recent_threats = get_recent_threats(limit=10)
        
        # Get real-time statistics if available
        rt_service = get_realtime_service()
        realtime_stats = {}
        if rt_service:
            realtime_stats = rt_service.get_threat_statistics()
        
        # Combine database and real-time data
        dashboard_response = {
            'recent_threats': recent_threats,
            'statistics': {
                'total_threats': realtime_stats.get('total_threats', len(recent_threats)),
                'threats_blocked': realtime_stats.get('threats_blocked', 0),
                'detection_rate': realtime_stats.get('detection_rate', 75.0),
                'active_sessions': realtime_stats.get('active_sessions', 0),
                'uptime_hours': realtime_stats.get('uptime_hours', 0),
                'model_requests': realtime_stats.get('model_requests', 0),
                'average_response_time': realtime_stats.get('average_response_time', 2.1)
            },
            'threat_distribution': realtime_stats.get('threat_distribution', {}),
            'severity_distribution': realtime_stats.get('severity_distribution', {}),
            'system_performance': {
                'status': 'operational',
                'websocket_enabled': realtime_service is not None,
                'ai_model_status': 'active' if threat_detector else 'offline'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(dashboard_response), 200
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({
            'error': f'Dashboard data failed: {str(e)}',
            'recent_threats': [],
            'statistics': {}
        }), 500

@app.route('/api/threats/recent', methods=['GET'])
def get_threats():
    """Get recent threats with pagination"""
    try:
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        
        threats = get_recent_threats(limit=limit, offset=offset)
        
        return jsonify({
            'threats': threats,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': len(threats) == limit
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Get threats error: {e}")
        return jsonify({
            'error': f'Failed to get threats: {str(e)}',
            'threats': []
        }), 500

@app.route('/api/realtime/status', methods=['GET'])
def realtime_status():
    """Get real-time service status and statistics"""
    try:
        rt_service = get_realtime_service()
        if not rt_service:
            return jsonify({
                'status': 'offline',
                'message': 'Real-time service not available'
            }), 503
        
        status_data = {
            'status': 'online',
            'statistics': rt_service.get_threat_statistics(),
            'active_users': len(rt_service.active_users),
            'user_list': [
                {
                    'username': user.username,
                    'active_page': user.active_page,
                    'join_time': user.join_time
                }
                for user in rt_service.active_users.values()
            ],
            'uptime': (datetime.now() - rt_service.stats['uptime_start']).total_seconds(),
            'threat_feed_active': True,
            'websocket_connections': len(rt_service.active_users)
        }
        
        return jsonify(status_data), 200
        
    except Exception as e:
        logger.error(f"Real-time status error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/system/metrics', methods=['GET'])
def system_metrics():
    """Get current system performance metrics"""
    try:
        rt_service = get_realtime_service()
        if rt_service and rt_service.metrics_history:
            latest_metrics = rt_service.metrics_history[-1]
            return jsonify({
                'metrics': latest_metrics.__dict__,
                'history_available': len(rt_service.metrics_history),
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'error': 'System metrics not available',
                'metrics': None
            }), 503
            
    except Exception as e:
        logger.error(f"System metrics error: {e}")
        return jsonify({
            'error': f'Failed to get system metrics: {str(e)}'
        }), 500

@app.route('/test')
def serve_test_page():
    """Serve the streaming test page"""
    try:
        # Try to read the test file from the project root
        import os
        test_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test-streaming.html')
        
        if os.path.exists(test_file_path):
            with open(test_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/html'}
        else:
            # Fallback: serve inline HTML
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>CyberGuard AI - Stream Test</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
                    .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                    .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                    .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
                    .log-entry { padding: 8px; margin: 5px 0; background: white; border-left: 4px solid #007bff; }
                    .threat { border-left-color: #dc3545; background: #fff5f5; }
                    button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
                    .btn-primary { background: #007bff; color: white; }
                    .btn-success { background: #28a745; color: white; }
                    .btn-danger { background: #dc3545; color: white; }
                    #logs { max-height: 400px; overflow-y: auto; }
                    .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
                    .metric-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🛡️ CyberGuard AI - Real-Time Stream Test</h1>
                    
                    <div class="status info">
                        <strong>Status:</strong> <span id="connection-status">Initializing...</span>
                    </div>

                    <div>
                        <button class="btn-primary" onclick="testBackendHealth()">Test Backend Health</button>
                        <button class="btn-success" onclick="startMonitoring()">Start Monitoring</button>
                        <button class="btn-danger" onclick="stopMonitoring()">Stop Monitoring</button>
                        <button class="btn-primary" onclick="connectStream()">Connect Stream</button>
                        <button class="btn-danger" onclick="disconnectStream()">Disconnect Stream</button>
                        <button onclick="clearLogs()">Clear Logs</button>
                    </div>

                    <div class="metrics">
                        <div class="metric-card">
                            <h3>Stream Events</h3>
                            <div id="stream-count">0</div>
                        </div>
                        <div class="metric-card">
                            <h3>Threats Detected</h3>
                            <div id="threat-count">0</div>
                        </div>
                        <div class="metric-card">
                            <h3>Connection Status</h3>
                            <div id="stream-status">Disconnected</div>
                        </div>
                        <div class="metric-card">
                            <h3>Last Update</h3>
                            <div id="last-update">Never</div>
                        </div>
                    </div>

                    <h3>Live Log Stream</h3>
                    <div id="logs"></div>
                </div>

                <script>
                    let eventSource = null;
                    let streamCount = 0;
                    let threatCount = 0;

                    function log(message, type = 'info', isTime = true) {
                        const logs = document.getElementById('logs');
                        const div = document.createElement('div');
                        div.className = `log-entry ${type === 'threat' ? 'threat' : ''}`;
                        const timestamp = isTime ? `[${new Date().toLocaleTimeString()}] ` : '';
                        div.innerHTML = `${timestamp}${message}`;
                        logs.insertBefore(div, logs.firstChild);
                    }

                    function updateStatus(message, type = 'info') {
                        const status = document.getElementById('connection-status');
                        status.textContent = message;
                        status.parentElement.className = `status ${type}`;
                    }

                    function updateMetrics() {
                        document.getElementById('stream-count').textContent = streamCount;
                        document.getElementById('threat-count').textContent = threatCount;
                        document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                    }

                    function clearLogs() {
                        document.getElementById('logs').innerHTML = '';
                        streamCount = 0;
                        threatCount = 0;
                        updateMetrics();
                    }

                    async function testBackendHealth() {
                        try {
                            log('🔍 Testing backend health...', 'info');
                            const response = await fetch('/api/health');
                            
                            if (!response.ok) {
                                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                            }
                            
                            const data = await response.json();
                            log(`✅ Backend healthy! Services: ${JSON.stringify(data.services)}`, 'info');
                            updateStatus('Backend Connected', 'success');
                            
                            // Test real-time service
                            const rtStatus = await fetch('/api/realtime/status');
                            const rtData = await rtStatus.json();
                            log(`📊 Real-time service: ${rtData.status} (${rtData.active_users} users)`, 'info');
                            
                        } catch (error) {
                            log(`❌ Backend test failed: ${error.message}`, 'info');
                            updateStatus('Backend Error', 'error');
                        }
                    }

                    async function startMonitoring() {
                        try {
                            log('🚀 Starting monitoring...', 'info');
                            const response = await fetch('/api/monitoring/start', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' }
                            });
                            
                            if (!response.ok) {
                                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                            }
                            
                            const data = await response.json();
                            log(`✅ Monitoring started: ${data.message}`, 'info');
                            
                        } catch (error) {
                            log(`❌ Start monitoring failed: ${error.message}`, 'info');
                        }
                    }

                    async function stopMonitoring() {
                        try {
                            log('🛑 Stopping monitoring...', 'info');
                            const response = await fetch('/api/monitoring/stop', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' }
                            });
                            
                            const data = await response.json();
                            log(`✅ Monitoring stopped: ${data.message}`, 'info');
                            
                        } catch (error) {
                            log(`❌ Stop monitoring failed: ${error.message}`, 'info');
                        }
                    }

                    function connectStream() {
                        if (eventSource) {
                            log('⚠️ Stream already connected', 'info');
                            return;
                        }

                        try {
                            log('📡 Connecting to stream...', 'info');
                            eventSource = new EventSource('/api/stream/logs');

                            eventSource.onopen = function() {
                                log('✅ Stream connected successfully!', 'info');
                                updateStatus('Stream Connected', 'success');
                                document.getElementById('stream-status').textContent = 'Connected';
                            };

                            eventSource.onmessage = function(event) {
                                try {
                                    const data = JSON.parse(event.data);
                                    streamCount++;
                                    
                                    if (data.event_type === 'live_log') {
                                        const logEntry = data.log;
                                        const analysis = data.analysis;
                                        
                                        let message = `📝 [${logEntry.source_ip}] ${logEntry.content}`;
                                        let type = 'info';
                                        
                                        if (analysis.threat_detected) {
                                            threatCount++;
                                            type = 'threat';
                                            message += ` 🚨 THREAT: ${analysis.threat_level} (${analysis.threat_score})`;
                                        }
                                        
                                        log(message, type);
                                    } else if (data.event_type === 'error') {
                                        log(`❌ Stream error: ${data.error}`, 'info');
                                    }
                                    
                                    updateMetrics();
                                    
                                } catch (error) {
                                    log(`❌ Failed to parse stream data: ${error.message}`, 'info');
                                }
                            };

                            eventSource.onerror = function(error) {
                                log(`❌ Stream error occurred`, 'info');
                                updateStatus('Stream Error', 'error');
                                document.getElementById('stream-status').textContent = 'Error';
                                
                                if (eventSource.readyState === EventSource.CLOSED) {
                                    log('🔌 Stream connection closed', 'info');
                                    eventSource = null;
                                    document.getElementById('stream-status').textContent = 'Disconnected';
                                }
                            };

                        } catch (error) {
                            log(`❌ Failed to connect to stream: ${error.message}`, 'info');
                            updateStatus('Stream Failed', 'error');
                        }
                    }

                    function disconnectStream() {
                        if (eventSource) {
                            eventSource.close();
                            eventSource = null;
                            log('🔌 Stream disconnected', 'info');
                            updateStatus('Stream Disconnected', 'info');
                            document.getElementById('stream-status').textContent = 'Disconnected';
                        } else {
                            log('⚠️ No stream to disconnect', 'info');
                        }
                    }

                    // Auto-connect on page load
                    window.addEventListener('load', function() {
                        log('🌐 Page loaded - Testing system...', 'info');
                        testBackendHealth();
                    });

                    // Cleanup on page unload
                    window.addEventListener('beforeunload', function() {
                        if (eventSource) {
                            eventSource.close();
                        }
                    });
                </script>
            </body>
            </html>
            ''', 200, {'Content-Type': 'text/html'}
            
    except Exception as e:
        logger.error(f"Error serving test page: {e}")
        return jsonify({'error': f'Failed to serve test page: {str(e)}'}), 500

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start live monitoring"""
    try:
        rt_service = get_realtime_service()
        if not rt_service:
            return jsonify({
                'status': 'error',
                'message': 'Real-time service not available'
            }), 503
        
        # Enable monitoring in the real-time service
        rt_service.monitoring_active = True
        
        # Emit WebSocket event to all connected clients
        socketio.emit('monitoring_status', {
            'status': 'started',
            'timestamp': datetime.now().isoformat(),
            'message': 'Live log monitoring started'
        }, room='monitoring_room', namespace='/monitoring')
        
        # Also emit to general namespace for backward compatibility
        socketio.emit('monitoring_started', {
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }, namespace='/monitoring')
        
        return jsonify({
            'status': 'started',
            'timestamp': datetime.now().isoformat(),
            'message': 'Live log monitoring started'
        }), 200
        
    except Exception as e:
        logger.error(f"Start monitoring error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop live monitoring"""
    try:
        rt_service = get_realtime_service()
        if not rt_service:
            return jsonify({
                'status': 'error',
                'message': 'Real-time service not available'
            }), 503
        
        # Disable monitoring in the real-time service
        rt_service.monitoring_active = False
        
        # Emit WebSocket event to all connected clients
        socketio.emit('monitoring_status', {
            'status': 'stopped',
            'timestamp': datetime.now().isoformat(),
            'message': 'Live log monitoring stopped'
        }, room='monitoring_room', namespace='/monitoring')
        
        # Also emit to general namespace for backward compatibility
        socketio.emit('monitoring_stopped', {
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }, namespace='/monitoring')
        
        return jsonify({
            'status': 'stopped',
            'timestamp': datetime.now().isoformat(),
            'message': 'Live log monitoring stopped'
        }), 200
        
    except Exception as e:
        logger.error(f"Stop monitoring error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/stream/logs')
def stream_logs():
    """Server-Sent Events endpoint for live log streaming"""
    def event_stream():
        import time
        import random
        import json
        
        # Sample log entries for demonstration
        sample_logs = [
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
        ]
        
        counter = 0
        while True:
            try:
                # Generate a random log entry
                log_entry = random.choice(sample_logs)
                timestamp = datetime.now().isoformat()
                source_ip = f"192.168.1.{random.randint(10, 200)}"
                
                # Create enhanced log entry
                enhanced_log = {
                    'id': f"log_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
                    'timestamp': timestamp,
                    'content': log_entry,
                    'source_ip': source_ip,
                    'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                    'status_code': random.choice([200, 404, 401, 403, 500]),
                }
                
                # Analyze for threats using the AI detector
                analysis_result = {'threat_detected': False, 'threat_level': 'none'}
                if threat_detector:
                    analysis_result = threat_detector.analyze_log(log_entry)
                
                # Combine log and analysis
                stream_data = {
                    'event_type': 'live_log',
                    'log': enhanced_log,
                    'analysis': analysis_result,
                    'counter': counter
                }
                
                yield f"data: {json.dumps(stream_data)}\n\n"
                
                counter += 1
                time.sleep(2)  # Send update every 2 seconds
                
            except Exception as e:
                logger.error(f"Stream error: {e}")
                error_data = {'error': str(e), 'event_type': 'error'}
                yield f"data: {json.dumps(error_data)}\n\n"
                break
    
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/api/health',
            '/api/analyze',
            '/api/dashboard',
            '/api/threats/recent',
            '/api/realtime/status',
            '/api/system/metrics'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'Please check server logs for details'
    }), 500

# ==================== APPLICATION STARTUP ====================

def create_log_directory():
    """Ensure logs directory exists"""
    os.makedirs('logs', exist_ok=True)

if __name__ == '__main__':
    try:
        # Create necessary directories
        create_log_directory()
        
        # Print startup information
        print("\n" + "="*70)
        print("🛡️  CYBERGUARD AI - ADVANCED THREAT DETECTION SYSTEM")
        print("="*70)
        print("🚀 Phase 5A: Real-Time WebSocket Integration")
        print("="*70)
        print(f"🌐 API Server: http://localhost:5001")
        print(f"🔌 WebSocket: ws://localhost:5001/socket.io")
        print(f"📊 Monitoring: /monitoring namespace")
        print(f"🤖 AI Model: {'✅ Active' if threat_detector else '❌ Offline'}")
        print(f"⚡ Real-time: {'✅ Active' if realtime_service else '❌ Offline'}")
        print("="*70)
        print("📋 Available Features:")
        print("   • Live threat detection and alerts")
        print("   • Real-time system monitoring")
        print("   • Multi-user collaboration")
        print("   • WebSocket-based updates")
        print("   • Historical threat analysis")
        print("   • Interactive threat investigation")
        print("="*70)
        print("🎯 Ready for connections! Open React dashboard at http://localhost:3000")
        print("="*70 + "\n")
        
        # Start the application with WebSocket support
        socketio.run(
            app,
            host='0.0.0.0',
            port=5001,
            debug=False,  # Disable debug in production
            use_reloader=False,  # Disable reloader with eventlet
            log_output=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested by user")
        logger.info("Server shutdown by user")
    except Exception as e:
        print(f"\n❌ Server startup failed: {e}")
        logger.error(f"Server startup failed: {e}")
        sys.exit(1) 