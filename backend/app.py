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
from flask import Flask, request, jsonify, send_from_directory
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
    r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]},
    r"/socket.io/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}
})

# Initialize SocketIO with CORS support
socketio = SocketIO(
    app,
    cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
            host='localhost',
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