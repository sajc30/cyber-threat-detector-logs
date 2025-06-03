"""
Flask API Routes for Cybersecurity Threat Detection System

Provides REST API endpoints for:
- Real-time threat detection
- Batch log analysis  
- System monitoring and health checks
- Admin dashboard functionality
- Performance metrics and statistics

Author: AI Cybersecurity System
"""

from flask import Blueprint, request, jsonify, render_template
from flask_cors import cross_origin
import logging
from datetime import datetime, timedelta
import json
from typing import Dict, List
import time

from model_inference import (
    get_inference_engine, 
    analyze_log, 
    analyze_logs_batch
)

logger = logging.getLogger(__name__)

# Create blueprint for API routes
api = Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """
    Health check endpoint to verify API status
    
    Returns:
        JSON response with system health information
    """
    try:
        engine = get_inference_engine()
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'model_loaded': engine.is_loaded,
            'device': str(engine.device) if engine.is_loaded else 'none',
            'api_endpoints': [
                '/health', '/detect', '/detect/batch', 
                '/stats', '/metrics', '/admin/dashboard'
            ]
        }
        
        if engine.is_loaded:
            health_status.update({
                'threshold': engine.optimal_threshold,
                'model_parameters': sum(p.numel() for p in engine.model.parameters()),
                'inference_ready': True
            })
        else:
            health_status.update({
                'inference_ready': False,
                'warning': 'Model not loaded - inference endpoints may not work'
            })
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api.route('/detect', methods=['POST'])
@cross_origin()
def detect_threat():
    """
    Analyze a single log message for cybersecurity threats
    
    Expected JSON payload:
    {
        "log_message": "string",
        "log_type": "string (optional)",
        "source": "string (optional)", 
        "server": "string (optional)"
    }
    
    Returns:
        JSON response with threat analysis results
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'log_message' not in data:
            return jsonify({
                'error': 'Missing required field: log_message'
            }), 400
        
        log_message = data['log_message']
        
        if not log_message or not isinstance(log_message, str):
            return jsonify({
                'error': 'log_message must be a non-empty string'
            }), 400
        
        # Extract optional metadata
        metadata = {
            'log_type': data.get('log_type', 'system'),
            'source': data.get('source', 'api'),
            'server': data.get('server', 'unknown')
        }
        
        # Perform threat detection
        start_time = time.time()
        result = analyze_log(log_message, **metadata)
        
        # Add request metadata
        result['request_id'] = f"req_{int(time.time() * 1000)}"
        result['api_response_time_ms'] = round((time.time() - start_time) * 1000, 2)
        
        # Determine HTTP status code based on threat level
        if result.get('threat_level') in ['critical', 'high']:
            status_code = 200  # Still successful, but flag for attention
        else:
            status_code = 200
        
        logger.info(f"🔍 Threat detection request: {result['threat_level']} threat detected")
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in threat detection: {e}")
        return jsonify({
            'error': 'Internal server error during threat detection',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api.route('/detect/batch', methods=['POST'])
@cross_origin()
def detect_threats_batch():
    """
    Analyze multiple log messages in batch for cybersecurity threats
    
    Expected JSON payload:
    {
        "log_messages": ["string1", "string2", ...],
        "log_type": "string (optional)",
        "source": "string (optional)",
        "server": "string (optional)"
    }
    
    Returns:
        JSON response with batch analysis results
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'log_messages' not in data:
            return jsonify({
                'error': 'Missing required field: log_messages'
            }), 400
        
        log_messages = data['log_messages']
        
        if not isinstance(log_messages, list) or len(log_messages) == 0:
            return jsonify({
                'error': 'log_messages must be a non-empty list'
            }), 400
        
        # Validate message count
        if len(log_messages) > 1000:
            return jsonify({
                'error': 'Maximum 1000 log messages per batch request'
            }), 400
        
        # Validate each message
        for i, msg in enumerate(log_messages):
            if not isinstance(msg, str) or not msg.strip():
                return jsonify({
                    'error': f'log_messages[{i}] must be a non-empty string'
                }), 400
        
        # Extract optional metadata
        metadata = {
            'log_type': data.get('log_type', 'system'),
            'source': data.get('source', 'api'),
            'server': data.get('server', 'unknown')
        }
        
        # Perform batch threat detection
        start_time = time.time()
        results = analyze_logs_batch(log_messages, **metadata)
        total_time = time.time() - start_time
        
        # Calculate batch statistics
        threat_count = sum(1 for r in results if r.get('is_threat', False))
        threat_levels = {}
        for result in results:
            level = result.get('threat_level', 'unknown')
            threat_levels[level] = threat_levels.get(level, 0) + 1
        
        # Build response
        response = {
            'request_id': f"batch_req_{int(time.time() * 1000)}",
            'batch_summary': {
                'total_logs': len(log_messages),
                'threats_detected': threat_count,
                'threat_rate': round(threat_count / len(log_messages) * 100, 2),
                'threat_levels': threat_levels,
                'processing_time_ms': round(total_time * 1000, 2),
                'avg_time_per_log_ms': round(total_time / len(log_messages) * 1000, 2)
            },
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"🔍 Batch detection: {len(log_messages)} logs, {threat_count} threats detected")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in batch threat detection: {e}")
        return jsonify({
            'error': 'Internal server error during batch threat detection',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api.route('/stats', methods=['GET'])
@cross_origin()
def get_statistics():
    """
    Get system performance statistics and metrics
    
    Returns:
        JSON response with comprehensive system statistics
    """
    try:
        engine = get_inference_engine()
        
        # Get performance stats from inference engine
        performance_stats = engine.get_performance_stats()
        
        # Add system statistics
        stats = {
            'system_info': {
                'api_version': '1.0.0',
                'model_loaded': engine.is_loaded,
                'uptime_info': 'API running since startup',
                'current_time': datetime.now().isoformat()
            },
            'performance_metrics': performance_stats,
            'detection_summary': {
                'total_requests': performance_stats.get('total_detections', 0),
                'threats_detected': performance_stats.get('threats_detected', 0),
                'threat_percentage': performance_stats.get('threat_rate', 0),
                'average_response_time': f"{performance_stats.get('avg_inference_time_ms', 0)}ms"
            }
        }
        
        if engine.is_loaded:
            stats['model_info'] = {
                'model_parameters': sum(p.numel() for p in engine.model.parameters()),
                'detection_threshold': engine.optimal_threshold,
                'device': str(engine.device),
                'sequence_length': engine.feature_extractor.sequence_length,
                'feature_count': len(engine.feature_extractor.feature_names)
            }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({
            'error': 'Failed to retrieve statistics',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api.route('/metrics', methods=['GET'])
@cross_origin() 
def get_metrics():
    """
    Get detailed performance metrics for monitoring
    
    Returns:
        JSON response with detailed metrics
    """
    try:
        engine = get_inference_engine()
        
        # Get basic performance stats
        performance_stats = engine.get_performance_stats()
        
        # Create detailed metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'inference_metrics': {
                'total_inferences': performance_stats.get('total_detections', 0),
                'successful_inferences': performance_stats.get('total_detections', 0),
                'failed_inferences': 0,  # Would track separately in production
                'average_latency_ms': performance_stats.get('avg_inference_time_ms', 0),
                'min_latency_ms': performance_stats.get('min_inference_time_ms', 0),
                'max_latency_ms': performance_stats.get('max_inference_time_ms', 0)
            },
            'detection_metrics': {
                'threats_detected': performance_stats.get('threats_detected', 0),
                'normal_logs': performance_stats.get('total_detections', 0) - performance_stats.get('threats_detected', 0),
                'threat_rate_percent': performance_stats.get('threat_rate', 0),
                'detection_threshold': performance_stats.get('threshold', 0)
            },
            'system_metrics': {
                'model_loaded': performance_stats.get('model_loaded', False),
                'device': performance_stats.get('device', 'unknown'),
                'memory_usage': 'Not implemented',  # Would add memory tracking
                'cpu_usage': 'Not implemented'      # Would add CPU tracking
            }
        }
        
        return jsonify(metrics), 200
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({
            'error': 'Failed to retrieve metrics',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """
    Render admin dashboard for system monitoring
    
    Returns:
        HTML dashboard page
    """
    try:
        engine = get_inference_engine()
        
        # Get stats for dashboard
        stats = engine.get_performance_stats()
        
        dashboard_data = {
            'system_status': 'Operational' if engine.is_loaded else 'Model Not Loaded',
            'model_loaded': engine.is_loaded,
            'total_detections': stats.get('total_detections', 0),
            'threats_detected': stats.get('threats_detected', 0),
            'threat_rate': stats.get('threat_rate', 0),
            'avg_response_time': stats.get('avg_inference_time_ms', 0),
            'threshold': stats.get('threshold', 0),
            'device': stats.get('device', 'unknown'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render_template('admin_dashboard.html', **dashboard_data)
        
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return f"Dashboard Error: {str(e)}", 500

@api.route('/admin/reload_model', methods=['POST'])
@cross_origin()
def reload_model():
    """
    Reload the threat detection model
    
    Returns:
        JSON response with reload status
    """
    try:
        engine = get_inference_engine()
        
        # Attempt to reload the latest model
        engine.auto_load_latest_model()
        
        return jsonify({
            'status': 'success',
            'message': 'Model reloaded successfully',
            'model_loaded': engine.is_loaded,
            'threshold': engine.optimal_threshold,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error reloading model: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to reload model',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api.route('/test', methods=['GET'])
@cross_origin()
def test_endpoint():
    """
    Test endpoint with sample threat detection
    
    Returns:
        JSON response with test results
    """
    try:
        # Test log messages with different threat levels
        test_logs = [
            "User authentication successful for admin",
            "CRITICAL: Unauthorized access attempt detected from 192.168.1.100",
            "ERROR: Failed login attempt for user admin from suspicious IP",
            "INFO: System backup completed successfully",
            "ALERT: Potential SQL injection detected in web request"
        ]
        
        results = []
        for log in test_logs:
            result = analyze_log(log, source='test', log_type='test')
            results.append({
                'log': log,
                'is_threat': result['is_threat'],
                'threat_level': result['threat_level'],
                'anomaly_score': result['anomaly_score']
            })
        
        return jsonify({
            'test_status': 'success',
            'test_results': results,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        return jsonify({
            'test_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Error handlers
@api.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested API endpoint does not exist',
        'available_endpoints': [
            '/health', '/detect', '/detect/batch', 
            '/stats', '/metrics', '/admin/dashboard', '/test'
        ]
    }), 404

@api.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint'
    }), 405

@api.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'timestamp': datetime.now().isoformat()
    }), 500 