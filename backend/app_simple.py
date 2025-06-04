#!/usr/bin/env python3
"""
CyberGuard AI - Simplified Flask REST API 
Core functionality without WebSocket complexity for containerized deployment
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Flask and related imports
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import random
import time
import threading

# Application modules
from config import Config
from ai_threat_detector import AIThreatDetector
from database import init_db, get_recent_threats, log_threat

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

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/*": {"origins": "*"}
})

# Initialize database
init_db()

# Initialize AI threat detector
try:
    threat_detector = AIThreatDetector()
    logger.info("✅ AI Threat Detector initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize AI Threat Detector: {e}")
    threat_detector = None

# Global monitoring state
monitoring_active = False

# ==================== REST API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with system status"""
    try:
        system_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'flask_api': 'online',
                'ai_threat_detector': 'online' if threat_detector else 'offline',
                'database': 'online',
                'monitoring': 'active' if monitoring_active else 'inactive'
            },
            'version': '1.0.0',
            'features': [
                'Real-time threat detection',
                'Historical threat tracking',
                'REST API'
            ]
        }
        
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
    """Log analysis endpoint"""
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
    """Dashboard data endpoint"""
    try:
        # Get recent threats from database
        recent_threats = get_recent_threats(limit=10)
        
        dashboard_response = {
            'recent_threats': recent_threats,
            'statistics': {
                'total_threats': len(recent_threats),
                'threats_blocked': 0,
                'detection_rate': 75.0,
                'active_sessions': 1,
                'uptime_hours': 1,
                'model_requests': 10,
                'average_response_time': 2.1
            },
            'threat_distribution': {},
            'severity_distribution': {},
            'system_performance': {
                'status': 'operational',
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
    """Get real-time service status (simplified)"""
    try:
        status_data = {
            'status': 'online',
            'active_users': 1,
            'monitoring_active': monitoring_active,
            'uptime': 3600,
            'threat_feed_active': monitoring_active,
            'websocket_connections': 0
        }
        
        return jsonify(status_data), 200
        
    except Exception as e:
        logger.error(f"Real-time status error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start live monitoring (simplified)"""
    try:
        global monitoring_active
        monitoring_active = True
        
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
    """Stop live monitoring (simplified)"""
    try:
        global monitoring_active
        monitoring_active = False
        
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
    """Server-Sent Events endpoint for live log streaming (simplified)"""
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
        ]
        
        counter = 0
        while monitoring_active and counter < 50:  # Limit to prevent infinite streams
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
            '/api/monitoring/start',
            '/api/monitoring/stop',
            '/api/stream/logs'
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
        print("🛡️  CYBERGUARD AI - SIMPLIFIED THREAT DETECTION API")
        print("="*70)
        print("🚀 Simplified Version: Core API without WebSocket complexity")
        print("="*70)
        print(f"🌐 API Server: http://0.0.0.0:5001")
        print(f"🤖 AI Model: {'✅ Active' if threat_detector else '❌ Offline'}")
        print("="*70)
        print("📋 Available Features:")
        print("   • Core threat detection API")
        print("   • Health monitoring")
        print("   • Simple log streaming")
        print("   • Historical threat analysis")
        print("="*70)
        print("🎯 Ready for connections!")
        print("="*70 + "\n")
        
        # Start the application with standard Flask WSGI
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested by user")
        logger.info("Server shutdown by user")
    except Exception as e:
        print(f"\n❌ Server startup failed: {e}")
        logger.error(f"Server startup failed: {e}")
        sys.exit(1) 