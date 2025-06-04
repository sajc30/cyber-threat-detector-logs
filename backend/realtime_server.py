#!/usr/bin/env python3

import json
import random
import re
import time
import threading
from datetime import datetime, timedelta
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import queue

print("🚀 Real-Time Server Starting...")

app = Flask(__name__)
# Simplified CORS - allow all origins for development
CORS(app, 
     origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
     allow_headers=["Content-Type", "Authorization", "Cache-Control"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

# Simplified CORS headers
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cache-Control'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

# Global state
log_queue = queue.Queue()
monitoring_active = False
log_generation_thread = None

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
    'System health check passed',
    'New user registration: alice@company.com',
]

def generate_live_logs():
    """Generate and queue live log entries"""
    global monitoring_active
    
    while monitoring_active:
        try:
            # Generate a random log entry
            log_entry = random.choice(SAMPLE_LOGS)
            timestamp = datetime.now().isoformat()
            source_ip = f"192.168.1.{random.randint(10, 200)}"
            
            # Enhanced log entry
            enhanced_log = {
                'id': f"log_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
                'timestamp': timestamp,
                'content': log_entry,
                'source_ip': source_ip,
                'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                'status_code': random.choice([200, 404, 401, 403, 500]),
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
                'analysis': analysis_result,
                'event_type': 'live_log'
            }
            
            # Add to queue
            log_queue.put(live_log_data)
            
            # Also add threat alert if detected
            if analysis_result['threat_detected']:
                threat_alert = {
                    'id': enhanced_log['id'],
                    'timestamp': timestamp,
                    'threat_type': ', '.join(analysis_result['threat_types']),
                    'severity': analysis_result['threat_level'],
                    'source_ip': source_ip,
                    'description': f"Detected {', '.join(analysis_result['threat_types'])} in log entry",
                    'threat_score': analysis_result['threat_score'],
                    'confidence': analysis_result['confidence'],
                    'blocked': analysis_result['threat_score'] > 0.6,
                    'log_content': log_entry,
                    'event_type': 'threat_alert'
                }
                
                log_queue.put(threat_alert)
                print(f"🚨 Threat Alert: {threat_alert['threat_type']} - {threat_alert['severity']}")
            
            # Wait between logs (3-6 seconds for realistic pace)
            time.sleep(random.uniform(3, 6))
            
        except Exception as e:
            print(f"❌ Error in log generation: {e}")
            time.sleep(5)

# Health check endpoint
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'CyberGuard AI Real-Time Server Running',
        'monitoring_active': monitoring_active,
        'queue_size': log_queue.qsize()
    })

# Threat analysis endpoint
@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        start_time = time.time()
        
        data = request.get_json()
        if not data or 'log_entry' not in data:
            return jsonify({'error': 'Missing log_entry in request'}), 400
        
        log_entry = data['log_entry']
        if not log_entry.strip():
            return jsonify({'error': 'Empty log entry'}), 400
        
        # Perform threat analysis
        result = detect_threats(log_entry)
        
        # Calculate inference time
        end_time = time.time()
        inference_time_ms = (end_time - start_time) * 1000
        
        result['timestamp'] = datetime.now().isoformat()
        result['log_entry_length'] = len(log_entry)
        result['inference_time_ms'] = round(inference_time_ms, 2)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

# Start monitoring endpoint
@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    global monitoring_active, log_generation_thread
    
    if not monitoring_active:
        monitoring_active = True
        
        if log_generation_thread is None or not log_generation_thread.is_alive():
            log_generation_thread = threading.Thread(target=generate_live_logs)
            log_generation_thread.daemon = True
            log_generation_thread.start()
        
        return jsonify({
            'status': 'started',
            'timestamp': datetime.now().isoformat(),
            'message': 'Live log monitoring started'
        })
    else:
        return jsonify({
            'status': 'already_active',
            'message': 'Monitoring is already active'
        })

# Stop monitoring endpoint
@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    global monitoring_active
    
    monitoring_active = False
    
    return jsonify({
        'status': 'stopped',
        'timestamp': datetime.now().isoformat(),
        'message': 'Live log monitoring stopped'
    })

# Server-Sent Events stream for real-time logs
@app.route('/api/stream/logs')
def stream_logs():
    def event_stream():
        while True:
            try:
                # Get log from queue (wait up to 1 second)
                log_data = log_queue.get(timeout=1)
                yield f"data: {json.dumps(log_data)}\n\n"
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield f"data: {json.dumps({'event_type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
            except Exception as e:
                print(f"❌ Stream error: {e}")
                break

    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cache-Control'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Content-Type'] = 'text/event-stream'
    return response

# Phase 5B: Advanced Analytics & Intelligence API Endpoints

@app.route('/api/threat-intelligence', methods=['GET'])
def get_threat_intelligence():
    """Get threat intelligence indicators"""
    try:
        # Mock threat intelligence data
        threat_intel = [
            {
                'id': 'TI-001',
                'indicator': '192.168.1.100',
                'type': 'IP Address',
                'threatLevel': 'High',
                'firstSeen': '2024-01-15',
                'lastSeen': '2 hours ago',
                'occurrences': 47,
                'associatedCampaigns': ['APT-29', 'Lazarus Group'],
                'reputation': 'Malicious',
                'confidence': 95,
                'tags': ['botnet', 'c2-server', 'apt'],
                'description': 'Known C&C server associated with APT-29 operations'
            },
            {
                'id': 'TI-002',
                'indicator': 'malware.example.com',
                'type': 'Domain',
                'threatLevel': 'Critical',
                'firstSeen': '2024-01-10',
                'lastSeen': '30 min ago',
                'occurrences': 23,
                'associatedCampaigns': ['Operation Aurora'],
                'reputation': 'Malicious',
                'confidence': 99,
                'tags': ['malware-distribution', 'phishing'],
                'description': 'Active malware distribution domain'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': threat_intel,
            'count': len(threat_intel),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch threat intelligence: {str(e)}'}), 500

@app.route('/api/forensic-cases', methods=['GET'])
def get_forensic_cases():
    """Get active forensic investigation cases"""
    try:
        cases = [
            {
                'id': 'CASE-001',
                'title': 'Advanced Persistent Threat Investigation',
                'status': 'Active',
                'priority': 'Critical',
                'assignee': 'Security Team Alpha',
                'createdDate': '2024-01-15',
                'lastUpdate': '2 hours ago',
                'findings': 'Multiple compromised endpoints detected',
                'indicators': 12,
                'timeline': 'Day 5 of investigation'
            },
            {
                'id': 'CASE-002',
                'title': 'SQL Injection Campaign Analysis',
                'status': 'Under Review',
                'priority': 'High',
                'assignee': 'Analyst John Doe',
                'createdDate': '2024-01-18',
                'lastUpdate': '1 day ago',
                'findings': 'Automated attack pattern identified',
                'indicators': 8,
                'timeline': 'Day 2 of investigation'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': cases,
            'active_cases': len([c for c in cases if c['status'] == 'Active']),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch forensic cases: {str(e)}'}), 500

@app.route('/api/predictive-analytics', methods=['GET'])
def get_predictive_analytics():
    """Get AI-powered predictive analytics"""
    try:
        predictions = {
            'nextWeekPrediction': {
                'sqlInjection': {'predicted': 145, 'confidence': 87, 'trend': 'increasing'},
                'xss': {'predicted': 98, 'confidence': 82, 'trend': 'stable'},
                'bruteForce': {'predicted': 67, 'confidence': 91, 'trend': 'decreasing'},
                'total': {'predicted': 310, 'confidence': 85, 'trend': 'increasing'}
            },
            'riskFactors': [
                {'factor': 'Increased scanning activity', 'impact': 'High', 'probability': 89},
                {'factor': 'New vulnerability disclosure', 'impact': 'Critical', 'probability': 65},
                {'factor': 'Holiday period approaching', 'impact': 'Medium', 'probability': 95},
                {'factor': 'Geopolitical tensions', 'impact': 'High', 'probability': 71}
            ],
            'modelAccuracy': {
                'last30Days': 89.3,
                'last7Days': 92.1,
                'yesterday': 94.7
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': predictions,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch predictive analytics: {str(e)}'}), 500

@app.route('/api/ml-insights', methods=['GET'])
def get_ml_insights():
    """Get machine learning insights and anomaly detection results"""
    try:
        insights = [
            {
                'type': 'Anomaly Detection',
                'title': 'Unusual Traffic Pattern Detected',
                'confidence': 94,
                'impact': 'High',
                'description': 'Machine learning model detected a 340% increase in traffic from Eastern Europe',
                'recommendation': 'Implement geo-blocking for suspicious regions',
                'timestamp': '2 hours ago'
            },
            {
                'type': 'Behavioral Analysis',
                'title': 'Admin Account Privilege Escalation',
                'confidence': 87,
                'impact': 'Critical',
                'description': 'AI detected unusual privilege escalation pattern for admin account "sa_admin"',
                'recommendation': 'Immediately review admin account activities and reset credentials',
                'timestamp': '4 hours ago'
            },
            {
                'type': 'Pattern Recognition',
                'title': 'Coordinated Attack Campaign',
                'confidence': 91,
                'impact': 'High',
                'description': 'Multiple IP addresses showing coordinated attack behavior',
                'recommendation': 'Implement IP range blocking and enhance monitoring',
                'timestamp': '6 hours ago'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': insights,
            'high_confidence_count': len([i for i in insights if i['confidence'] > 90]),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch ML insights: {str(e)}'}), 500

@app.route('/api/threat-hunting', methods=['POST'])
def execute_threat_hunting():
    """Execute advanced threat hunting queries"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query.strip():
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Simulate threat hunting results based on query
        mock_results = [
            {
                'id': 'hunt-001',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': '192.168.1.45',
                'event': 'Suspicious PowerShell execution',
                'severity': 'High',
                'confidence': 89,
                'raw_log': f'PowerShell execution detected matching query: {query[:50]}...'
            },
            {
                'id': 'hunt-002',
                'timestamp': (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'),
                'source': '10.0.0.23',
                'event': 'Unusual network connection pattern',
                'severity': 'Medium',
                'confidence': 76,
                'raw_log': f'Network anomaly detected for query: {query[:50]}...'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'query': query,
            'results': mock_results,
            'count': len(mock_results),
            'execution_time_ms': random.uniform(50, 200),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Threat hunting failed: {str(e)}'}), 500

@app.route('/api/advanced-analytics', methods=['GET'])
def get_advanced_analytics():
    """Get comprehensive advanced analytics data"""
    try:
        # Get query parameters
        time_range = request.args.get('timeRange', '30d')
        analytics_type = request.args.get('type', 'all')
        
        analytics_data = {
            'threatTrends': {
                'last30Days': [
                    {
                        'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                        'sqlInjection': random.randint(10, 50),
                        'xss': random.randint(5, 40),
                        'bruteForce': random.randint(8, 30),
                        'directoryTraversal': random.randint(3, 20)
                    } for i in range(30, 0, -1)
                ]
            },
            'threatDistribution': [
                {'name': 'SQL Injection', 'value': 342, 'color': '#f44336', 'severity': 'High'},
                {'name': 'Cross-Site Scripting', 'value': 287, 'color': '#ff9800', 'severity': 'Medium'},
                {'name': 'Brute Force Attack', 'value': 156, 'color': '#2196f3', 'severity': 'Medium'},
                {'name': 'Directory Traversal', 'value': 89, 'color': '#9c27b0', 'severity': 'Low'}
            ],
            'geographicData': [
                {'country': 'China', 'attacks': 145, 'lat': 35.8617, 'lng': 104.1954},
                {'country': 'Russia', 'attacks': 123, 'lat': 61.5240, 'lng': 105.3188},
                {'country': 'United States', 'attacks': 98, 'lat': 37.0902, 'lng': -95.7129}
            ],
            'topAttackers': [
                {'ip': '192.168.1.100', 'attacks': 45, 'country': 'CN', 'lastSeen': '2 hours ago'},
                {'ip': '10.0.0.45', 'attacks': 38, 'country': 'RU', 'lastSeen': '4 hours ago'},
                {'ip': '172.16.0.23', 'attacks': 32, 'country': 'US', 'lastSeen': '1 hour ago'}
            ],
            'systemPerformance': {
                'avgResponseTime': random.uniform(50, 150),
                'successRate': random.uniform(85, 98),
                'cpuUsage': random.uniform(40, 80),
                'memoryUsage': random.uniform(30, 70)
            }
        }
        
        return jsonify({
            'status': 'success',
            'timeRange': time_range,
            'data': analytics_data,
            'generatedAt': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch advanced analytics: {str(e)}'}), 500

# Phase 5C: System Configuration & Production Readiness API Endpoints

@app.route('/api/system/config', methods=['GET'])
def get_system_config():
    """Get current system configuration"""
    try:
        config = {
            'security': {
                'enableRateLimit': True,
                'rateLimitRequests': 100,
                'rateLimitWindow': 3600,
                'enableCORS': True,
                'allowedOrigins': ['http://localhost:3000', 'https://yourdomain.com'],
                'enableSSL': False,
                'sslRedirect': False,
                'enableCSRF': True,
                'sessionTimeout': 1800,
                'passwordPolicy': {
                    'minLength': 8,
                    'requireNumbers': True,
                    'requireSymbols': True,
                    'requireUppercase': True,
                },
                'ipWhitelist': [],
                'enableIPBlocking': True,
                'maxFailedAttempts': 5,
            },
            'monitoring': {
                'enableMetrics': True,
                'metricsInterval': 30,
                'enableLogging': True,
                'logLevel': 'INFO',
                'logRetention': 30,
                'enableAlerts': True,
                'alertThresholds': {
                    'cpuUsage': 80,
                    'memoryUsage': 85,
                    'diskUsage': 90,
                    'errorRate': 5,
                },
                'enableHealthChecks': True,
                'healthCheckInterval': 60,
            },
            'notifications': {
                'enableEmail': False,
                'emailSettings': {
                    'smtpServer': '',
                    'smtpPort': 587,
                    'username': '',
                    'fromEmail': '',
                },
                'enableSlack': False,
                'slackWebhook': '',
                'enableSMS': False,
                'threatLevelNotifications': {
                    'low': False,
                    'medium': True,
                    'high': True,
                    'critical': True,
                },
            },
            'performance': {
                'maxConcurrentConnections': 100,
                'requestTimeout': 30,
                'enableCaching': True,
                'cacheExpiration': 300,
                'enableCompression': True,
                'compressionLevel': 6,
                'enableLoadBalancing': False,
                'workerProcesses': 4,
                'maxRequestSize': 16,
            },
            'authentication': {
                'enableMFA': False,
                'mfaProvider': 'google',
                'sessionDuration': 3600,
                'enableSSO': False,
                'ssoProvider': 'azure',
                'enableLDAP': False,
                'passwordReset': True,
                'enableOAuth': False,
                'oauthProviders': [],
            },
            'backup': {
                'enableAutoBackup': True,
                'backupInterval': 'daily',
                'backupRetention': 7,
                'backupLocation': '/backups',
                'enableEncryption': True,
                'compressionEnabled': True,
                'includeConfigs': True,
                'includeLogs': True,
                'includeDatabase': True,
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': config,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch system configuration: {str(e)}'}), 500

@app.route('/api/system/config', methods=['PUT'])
def update_system_config():
    """Update system configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No configuration data provided'}), 400
        
        # In a real implementation, this would validate and save to database/config files
        # For now, we'll simulate successful update
        
        # Validate required sections
        required_sections = ['security', 'monitoring', 'notifications', 'performance', 'authentication', 'backup']
        for section in required_sections:
            if section not in data:
                return jsonify({'error': f'Missing configuration section: {section}'}), 400
        
        # Simulate configuration update
        updated_config = data
        
        return jsonify({
            'status': 'success',
            'message': 'System configuration updated successfully',
            'data': updated_config,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update system configuration: {str(e)}'}), 500

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Get real-time system status and health metrics"""
    try:
        import psutil
        import os
        
        # Get actual system metrics if psutil is available
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            # Convert uptime to human readable format
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            uptime_str = f"{days}d {hours}h {minutes}m"
            
        except ImportError:
            # Fallback to mock data if psutil not available
            cpu_usage = random.uniform(20, 80)
            memory_usage = random.uniform(40, 85)
            disk_usage = random.uniform(20, 60)
            uptime_str = "2d 14h 32m"
        except:
            # Fallback to mock data on any error
            cpu_usage = random.uniform(20, 80)
            memory_usage = random.uniform(40, 85)
            disk_usage = random.uniform(20, 60)
            uptime_str = "2d 14h 32m"
        
        status = {
            'uptime': uptime_str,
            'cpuUsage': round(cpu_usage, 1),
            'memoryUsage': round(memory.percent if 'memory' in locals() else random.uniform(40, 85), 1),
            'diskUsage': round((disk.used / disk.total * 100) if 'disk' in locals() else random.uniform(20, 60), 1),
            'activeConnections': random.randint(15, 45),
            'lastBackup': '2024-01-20 02:00:00',
            'threatDetectionEnabled': True,
            'databaseStatus': 'healthy',
            'apiStatus': 'healthy',
            'services': {
                'webServer': 'running',
                'database': 'running',
                'threatDetection': 'running',
                'monitoring': 'running',
                'backup': 'running'
            },
            'networkStats': {
                'bytesIn': random.randint(1000000, 5000000),
                'bytesOut': random.randint(800000, 3000000),
                'packetsIn': random.randint(10000, 50000),
                'packetsOut': random.randint(8000, 40000)
            },
            'performance': {
                'avgResponseTime': round(random.uniform(50, 200), 2),
                'requestsPerSecond': round(random.uniform(10, 100), 2),
                'errorRate': round(random.uniform(0.1, 2.5), 2),
                'successRate': round(random.uniform(97, 99.9), 2)
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': status,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch system status: {str(e)}'}), 500

@app.route('/api/system/restart', methods=['POST'])
def restart_system():
    """Restart system services (simulation)"""
    try:
        data = request.get_json()
        service = data.get('service', 'all') if data else 'all'
        
        # Simulate service restart
        restart_time = datetime.now().isoformat()
        
        return jsonify({
            'status': 'success',
            'message': f'Service "{service}" restart initiated',
            'restartTime': restart_time,
            'estimatedDowntime': '30 seconds',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to restart system: {str(e)}'}), 500

@app.route('/api/system/backup', methods=['POST'])
def create_system_backup():
    """Create system backup (simulation)"""
    try:
        data = request.get_json()
        backup_type = data.get('type', 'full') if data else 'full'
        include_configs = data.get('includeConfigs', True) if data else True
        include_logs = data.get('includeLogs', True) if data else True
        include_database = data.get('includeDatabase', True) if data else True
        
        backup_id = f"backup_{int(time.time())}"
        backup_size = random.randint(100, 1000)  # MB
        
        return jsonify({
            'status': 'success',
            'message': 'System backup created successfully',
            'backupId': backup_id,
            'backupType': backup_type,
            'size': f"{backup_size} MB",
            'location': f"/backups/{backup_id}.tar.gz",
            'includes': {
                'configurations': include_configs,
                'logs': include_logs,
                'database': include_database
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to create backup: {str(e)}'}), 500

@app.route('/api/system/logs', methods=['GET'])
def get_system_logs():
    """Get system logs with filtering options"""
    try:
        # Get query parameters
        level = request.args.get('level', 'INFO')
        limit = int(request.args.get('limit', 100))
        service = request.args.get('service', 'all')
        
        # Mock log entries
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        services = ['api', 'database', 'threat-detection', 'monitoring', 'backup']
        
        logs = []
        for i in range(limit):
            log_time = datetime.now() - timedelta(minutes=i*5)
            log_entry = {
                'timestamp': log_time.isoformat(),
                'level': random.choice(log_levels),
                'service': random.choice(services),
                'message': f"Sample log message {i+1}",
                'details': f"Additional context for log entry {i+1}"
            }
            
            # Filter by level if specified
            if level != 'all' and log_entry['level'] != level:
                continue
                
            # Filter by service if specified
            if service != 'all' and log_entry['service'] != service:
                continue
                
            logs.append(log_entry)
        
        return jsonify({
            'status': 'success',
            'data': logs,
            'count': len(logs),
            'filters': {
                'level': level,
                'service': service,
                'limit': limit
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch system logs: {str(e)}'}), 500

@app.route('/api/system/security/audit', methods=['GET'])
def get_security_audit():
    """Get security audit information"""
    try:
        audit_data = {
            'lastAudit': '2024-01-20 10:30:00',
            'securityScore': random.randint(85, 98),
            'vulnerabilities': {
                'critical': random.randint(0, 2),
                'high': random.randint(0, 5),
                'medium': random.randint(1, 8),
                'low': random.randint(2, 12)
            },
            'compliance': {
                'gdpr': True,
                'hipaa': False,
                'sox': True,
                'pci': False
            },
            'recommendations': [
                'Enable SSL/TLS encryption for all endpoints',
                'Implement multi-factor authentication',
                'Update password policy requirements',
                'Configure automated security scanning',
                'Review and update firewall rules'
            ],
            'recentEvents': [
                {
                    'timestamp': '2024-01-20 14:25:00',
                    'event': 'Failed login attempt',
                    'severity': 'medium',
                    'source': '192.168.1.100'
                },
                {
                    'timestamp': '2024-01-20 13:45:00',
                    'event': 'Configuration change',
                    'severity': 'low',
                    'user': 'admin@company.com'
                },
                {
                    'timestamp': '2024-01-20 12:30:00',
                    'event': 'Security scan completed',
                    'severity': 'info',
                    'details': 'No new vulnerabilities found'
                }
            ]
        }
        
        return jsonify({
            'status': 'success',
            'data': audit_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch security audit: {str(e)}'}), 500

if __name__ == '__main__':
    print("🌐 Starting Real-Time server on http://localhost:5001")
    print("✅ Server ready in ~2 seconds!")
    app.run(host='localhost', port=5001, debug=False, threaded=True) 