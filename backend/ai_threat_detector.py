#!/usr/bin/env python3
"""
AI Threat Detector for CyberGuard AI
Simplified implementation for demonstration purposes
"""

import time
import random
import re
from typing import Dict, Any, List
from datetime import datetime


class AIThreatDetector:
    """AI-powered threat detection system"""
    
    def __init__(self):
        """Initialize the threat detector"""
        self.suspicious_patterns = [
            # SQL Injection patterns
            r'(union|select|insert|update|delete|drop|create|alter|exec|execute)',
            r'(\-\-|\;|\||\/\*|\*\/)',
            r'(\'|\"|\`)',
            
            # XSS patterns
            r'(<script|<\/script>|javascript:|vbscript:)',
            r'(onerror|onload|onclick|onmouseover)',
            r'(alert\(|document\.cookie|window\.location)',
            
            # Path traversal
            r'(\.\.\/|\.\.\\|\.\./|\.\.\\)',
            r'(/etc/passwd|/windows/system32)',
            
            # Command injection
            r'(\||;|&|`|\$\()',
            r'(bash|sh|cmd|powershell)',
            
            # Authentication bypass
            r'(admin|administrator|root)',
            r'(password|passwd|pwd)',
            r'(login|logon)',
            
            # Malware indicators
            r'(malware|virus|trojan|ransomware)',
            r'(backdoor|rootkit|keylogger)',
            
            # Network attacks
            r'(ddos|dos|flood)',
            r'(port.*scan|nmap|masscan)',
            
            # Data exfiltration
            r'(exfiltrat|steal|dump)',
            r'(ftp|scp|rsync).*upload',
        ]
        
        self.threat_keywords = {
            'critical': ['malware', 'ransomware', 'rootkit', 'backdoor', 'exfiltrat'],
            'high': ['injection', 'bypass', 'admin', 'root', 'ddos', 'dump'],
            'medium': ['script', 'alert', 'cookie', 'traversal', 'scan'],
            'low': ['error', 'failed', 'timeout', 'warning']
        }
        
        self.model_loaded = True
        self.features_count = 52
        print("✅ AI Threat Detector initialized (Demo Mode)")
    
    def analyze_log(self, log_entry: str) -> Dict[str, Any]:
        """Analyze a log entry for potential threats"""
        start_time = time.time()
        
        try:
            # Simulate model processing time
            processing_time = random.uniform(0.5, 2.5)
            time.sleep(processing_time / 1000)  # Convert to seconds for demo
            
            # Extract features from log entry
            features = self._extract_features(log_entry)
            
            # Determine threat level and score
            threat_level, threat_score, confidence = self._classify_threat(log_entry, features)
            
            # Calculate processing time
            inference_time_ms = (time.time() - start_time) * 1000
            
            result = {
                'threat_detected': threat_score > 0.5,
                'threat_level': threat_level,
                'threat_score': round(threat_score, 4),
                'confidence': round(confidence, 4),
                'inference_time_ms': round(inference_time_ms, 2),
                'features_extracted': len(features),
                'timestamp': datetime.now().isoformat(),
                'model_version': '1.0.0-demo',
                'log_entry_length': len(log_entry),
                'analysis_details': {
                    'suspicious_patterns_found': features.get('suspicious_patterns', 0),
                    'threat_keywords_found': features.get('threat_keywords', []),
                    'entry_complexity': features.get('complexity_score', 0)
                }
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error in threat analysis: {e}")
            return {
                'threat_detected': False,
                'threat_level': 'unknown',
                'threat_score': 0.0,
                'confidence': 0.0,
                'inference_time_ms': 0.0,
                'features_extracted': 0,
                'error': str(e)
            }
    
    def _extract_features(self, log_entry: str) -> Dict[str, Any]:
        """Extract features from log entry"""
        features = {}
        
        # Basic text features
        features['length'] = len(log_entry)
        features['word_count'] = len(log_entry.split())
        features['uppercase_ratio'] = sum(1 for c in log_entry if c.isupper()) / max(len(log_entry), 1)
        features['digit_ratio'] = sum(1 for c in log_entry if c.isdigit()) / max(len(log_entry), 1)
        features['special_char_ratio'] = sum(1 for c in log_entry if not c.isalnum() and not c.isspace()) / max(len(log_entry), 1)
        
        # Suspicious pattern detection
        suspicious_count = 0
        for pattern in self.suspicious_patterns:
            if re.search(pattern, log_entry, re.IGNORECASE):
                suspicious_count += 1
        features['suspicious_patterns'] = suspicious_count
        
        # Threat keyword detection
        threat_keywords_found = []
        for level, keywords in self.threat_keywords.items():
            for keyword in keywords:
                if keyword.lower() in log_entry.lower():
                    threat_keywords_found.append({'keyword': keyword, 'level': level})
        features['threat_keywords'] = threat_keywords_found
        
        # Calculate complexity score
        complexity_factors = [
            features['length'] > 100,
            features['special_char_ratio'] > 0.2,
            features['suspicious_patterns'] > 0,
            len(threat_keywords_found) > 0,
            'http' in log_entry.lower(),
            any(char in log_entry for char in ['<', '>', '&', '"', "'"]),
        ]
        features['complexity_score'] = sum(complexity_factors) / len(complexity_factors)
        
        return features
    
    def _classify_threat(self, log_entry: str, features: Dict[str, Any]) -> tuple:
        """Classify threat level and calculate scores"""
        base_score = 0.1  # Base score for any log entry
        
        # Scoring based on features
        score_factors = []
        
        # Length-based scoring
        if features['length'] > 500:
            score_factors.append(0.3)
        elif features['length'] > 200:
            score_factors.append(0.15)
        
        # Suspicious patterns
        pattern_score = min(features['suspicious_patterns'] * 0.2, 0.6)
        if pattern_score > 0:
            score_factors.append(pattern_score)
        
        # Threat keywords
        keyword_scores = {'critical': 0.8, 'high': 0.6, 'medium': 0.4, 'low': 0.2}
        max_keyword_score = 0
        for keyword_info in features['threat_keywords']:
            level = keyword_info['level']
            max_keyword_score = max(max_keyword_score, keyword_scores.get(level, 0))
        if max_keyword_score > 0:
            score_factors.append(max_keyword_score)
        
        # Special character ratio
        if features['special_char_ratio'] > 0.3:
            score_factors.append(0.3)
        elif features['special_char_ratio'] > 0.15:
            score_factors.append(0.15)
        
        # Calculate final threat score
        if score_factors:
            threat_score = base_score + sum(score_factors) / len(score_factors)
        else:
            threat_score = base_score
        
        # Add some randomness for demo purposes
        threat_score += random.uniform(-0.1, 0.1)
        threat_score = max(0.0, min(1.0, threat_score))  # Clamp between 0 and 1
        
        # Determine threat level
        if threat_score >= 0.8:
            threat_level = 'critical'
        elif threat_score >= 0.6:
            threat_level = 'high'
        elif threat_score >= 0.4:
            threat_level = 'medium'
        elif threat_score >= 0.2:
            threat_level = 'low'
        else:
            threat_level = 'normal'
        
        # Calculate confidence (higher for more definitive scores)
        if threat_score > 0.7 or threat_score < 0.3:
            confidence = random.uniform(0.85, 0.98)
        else:
            confidence = random.uniform(0.65, 0.85)
        
        return threat_level, threat_score, confidence
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            'model_loaded': self.model_loaded,
            'model_type': 'Demo Threat Detector',
            'version': '1.0.0-demo',
            'features_count': self.features_count,
            'patterns_count': len(self.suspicious_patterns),
            'threat_levels': list(self.threat_keywords.keys()),
            'capabilities': [
                'SQL Injection Detection',
                'XSS Detection',
                'Path Traversal Detection',
                'Command Injection Detection',
                'Authentication Bypass Detection',
                'Malware Detection',
                'Network Attack Detection',
                'Data Exfiltration Detection'
            ]
        }
    
    def batch_analyze(self, log_entries: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple log entries"""
        results = []
        for entry in log_entries:
            result = self.analyze_log(entry)
            results.append(result)
        return results
    
    def update_model(self, model_data: Any = None) -> bool:
        """Update the threat detection model (demo implementation)"""
        print("🔄 Model update requested (Demo Mode - No actual update)")
        time.sleep(1)  # Simulate update time
        print("✅ Model update completed (Demo)")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get model statistics"""
        return {
            'total_analyses': random.randint(1000, 5000),
            'threats_detected': random.randint(100, 500),
            'false_positives': random.randint(5, 25),
            'accuracy': random.uniform(0.92, 0.98),
            'precision': random.uniform(0.88, 0.95),
            'recall': random.uniform(0.85, 0.93),
            'f1_score': random.uniform(0.87, 0.94)
        } 