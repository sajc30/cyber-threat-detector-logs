#!/usr/bin/env python3

import json
import random
import re
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

print("🚀 Ultra Simple Server Starting...")

app = Flask(__name__)
CORS(app)

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

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'CyberGuard AI Server Running'
    })

@app.route('/api/dashboard')
def dashboard():
    return jsonify({
        'recent_threats': [{
            'id': f'threat_{i}',
            'threat_type': random.choice(['SQL Injection', 'XSS', 'Brute Force']),
            'severity': random.choice(['low', 'medium', 'high']),
            'timestamp': datetime.now().isoformat()
        } for i in range(5)],
        'statistics': {
            'total_threats': 127,
            'threats_blocked': 98,
            'detection_rate': 85.5
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        import time
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

if __name__ == '__main__':
    print("🌐 Starting on http://localhost:5001")
    app.run(host='localhost', port=5001, debug=False) 