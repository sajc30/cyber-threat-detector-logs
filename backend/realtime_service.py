#!/usr/bin/env python3
"""
Real-Time WebSocket Service for CyberGuard AI
Provides live threat detection, performance monitoring, and multi-user collaboration
"""

import json
import time
import threading
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import eventlet


@dataclass
class ThreatAlert:
    """Real-time threat alert data structure"""
    id: str
    timestamp: str
    threat_type: str
    severity: str
    source_ip: str
    target: str
    description: str
    threat_score: float
    confidence: float
    response_time_ms: float
    blocked: bool = False
    investigated: bool = False


@dataclass
class UserSession:
    """User session tracking for multi-user features"""
    session_id: str
    username: str
    join_time: str
    last_activity: str
    active_page: str
    location: Optional[str] = None


@dataclass
class SystemMetrics:
    """Real-time system performance metrics"""
    timestamp: str
    cpu_usage: float
    memory_usage: float
    network_io: Dict[str, float]
    active_connections: int
    threats_per_minute: int
    model_inference_time: float
    queue_size: int


class RealTimeService:
    """Real-time WebSocket service for live cybersecurity monitoring"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.active_users: Dict[str, UserSession] = {}
        self.threat_history: deque = deque(maxlen=1000)  # Keep last 1000 threats
        self.metrics_history: deque = deque(maxlen=100)   # Keep last 100 metric points
        self.rooms_users: Dict[str, set] = defaultdict(set)
        self.monitoring_active = True  # Enable monitoring by default
        
        # Performance tracking
        self.stats = {
            'total_threats_detected': 0,
            'threats_blocked': 0,
            'active_sessions': 0,
            'uptime_start': datetime.now(),
            'model_requests': 0,
            'average_response_time': 0.0
        }
        
        # Start background tasks
        self._start_background_tasks()
        
    def _start_background_tasks(self):
        """Start background threads for real-time updates"""
        # System metrics monitoring
        self.socketio.start_background_task(self._system_metrics_monitor)
        
        # User activity tracker
        self.socketio.start_background_task(self._user_activity_tracker)
        
        # Simulated live threat feed (for demo)
        self.socketio.start_background_task(self._simulated_threat_feed)
        
    def _system_metrics_monitor(self):
        """Monitor and broadcast system metrics every 5 seconds"""
        while True:
            try:
                metrics = self._generate_system_metrics()
                self.metrics_history.append(metrics)
                
                # Broadcast to all connected clients
                self.socketio.emit('system_metrics_update', asdict(metrics), namespace='/monitoring')
                
                eventlet.sleep(5)  # Update every 5 seconds
            except Exception as e:
                print(f"Error in system metrics monitor: {e}")
                eventlet.sleep(5)
                
    def _user_activity_tracker(self):
        """Track user activity and clean up inactive sessions"""
        while True:
            try:
                current_time = datetime.now()
                inactive_users = []
                
                for session_id, user in self.active_users.items():
                    last_activity = datetime.fromisoformat(user.last_activity)
                    if (current_time - last_activity).seconds > 300:  # 5 minutes timeout
                        inactive_users.append(session_id)
                
                # Remove inactive users
                for session_id in inactive_users:
                    self._remove_user_session(session_id)
                
                # Broadcast updated user list
                self._broadcast_active_users()
                
                eventlet.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"Error in user activity tracker: {e}")
                eventlet.sleep(30)
                
    def _simulated_threat_feed(self):
        """Generate simulated live threat alerts for demonstration"""
        threat_types = [
            ('SQL Injection', 'high', 'Database attack attempt'),
            ('Brute Force', 'medium', 'Multiple failed login attempts'),
            ('Malware Upload', 'critical', 'Malicious file detected'),
            ('DDoS Attack', 'high', 'Distributed denial of service'),
            ('Phishing', 'medium', 'Suspicious email detected'),
            ('Port Scan', 'low', 'Network reconnaissance activity'),
            ('XSS Attack', 'medium', 'Cross-site scripting attempt'),
            ('Data Exfiltration', 'critical', 'Unauthorized data access')
        ]
        
        while True:
            try:
                # Generate random threat (30% chance every 10-30 seconds)
                if random.random() < 0.3:
                    threat_type, severity, description = random.choice(threat_types)
                    
                    alert = ThreatAlert(
                        id=f"threat_{int(time.time())}_{random.randint(1000, 9999)}",
                        timestamp=datetime.now().isoformat(),
                        threat_type=threat_type,
                        severity=severity,
                        source_ip=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                        target=f"server-{random.randint(1, 10)}.internal",
                        description=description,
                        threat_score=random.uniform(0.6, 0.95),
                        confidence=random.uniform(0.8, 0.99),
                        response_time_ms=random.uniform(1.2, 4.8),
                        blocked=random.choice([True, False])
                    )
                    
                    self.broadcast_threat_alert(alert)
                
                # Wait 10-30 seconds before next potential threat
                wait_time = random.uniform(10, 30)
                eventlet.sleep(wait_time)
                
            except Exception as e:
                print(f"Error in simulated threat feed: {e}")
                eventlet.sleep(10)
    
    def _generate_system_metrics(self) -> SystemMetrics:
        """Generate current system performance metrics"""
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_usage=random.uniform(20, 80),
            memory_usage=random.uniform(40, 85),
            network_io={
                'bytes_in': random.uniform(1000, 50000),
                'bytes_out': random.uniform(500, 25000)
            },
            active_connections=len(self.active_users),
            threats_per_minute=random.randint(0, 15),
            model_inference_time=random.uniform(1.5, 5.0),
            queue_size=random.randint(0, 25)
        )
    
    def handle_user_connect(self, session_id: str, username: str = None):
        """Handle new user connection"""
        username = username or f"User_{session_id[:8]}"
        
        user_session = UserSession(
            session_id=session_id,
            username=username,
            join_time=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            active_page="dashboard"
        )
        
        self.active_users[session_id] = user_session
        self.stats['active_sessions'] = len(self.active_users)
        
        # Send welcome data to new user
        self.socketio.emit('welcome', {
            'user_info': asdict(user_session),
            'recent_threats': [asdict(threat) for threat in list(self.threat_history)[-10:]],
            'system_stats': self.stats,
            'active_users_count': len(self.active_users)
        }, room=session_id, namespace='/monitoring')
        
        # Broadcast updated user list
        self._broadcast_active_users()
        
        print(f"👤 User {username} connected (Session: {session_id})")
    
    def handle_user_disconnect(self, session_id: str):
        """Handle user disconnection"""
        if session_id in self.active_users:
            username = self.active_users[session_id].username
            self._remove_user_session(session_id)
            print(f"👤 User {username} disconnected (Session: {session_id})")
    
    def _remove_user_session(self, session_id: str):
        """Remove user session and update stats"""
        if session_id in self.active_users:
            del self.active_users[session_id]
            self.stats['active_sessions'] = len(self.active_users)
            self._broadcast_active_users()
    
    def handle_page_change(self, session_id: str, page: str):
        """Handle user page navigation"""
        if session_id in self.active_users:
            self.active_users[session_id].active_page = page
            self.active_users[session_id].last_activity = datetime.now().isoformat()
            
            # Join appropriate room for page-specific updates
            if page == 'monitoring':
                join_room('monitoring_room', session_id, namespace='/monitoring')
            elif page == 'analytics':
                join_room('analytics_room', session_id, namespace='/monitoring')
    
    def broadcast_threat_alert(self, alert: ThreatAlert):
        """Broadcast new threat alert to all connected users"""
        self.threat_history.append(alert)
        self.stats['total_threats_detected'] += 1
        
        if alert.blocked:
            self.stats['threats_blocked'] += 1
        
        # Broadcast to all monitoring room users
        self.socketio.emit('threat_alert', {
            'alert': asdict(alert),
            'total_threats': self.stats['total_threats_detected'],
            'threats_blocked': self.stats['threats_blocked']
        }, room='monitoring_room', namespace='/monitoring')
        
        # Send high-priority alerts to all users regardless of page
        if alert.severity in ['high', 'critical']:
            self.socketio.emit('priority_alert', asdict(alert), namespace='/monitoring')
        
        print(f"🚨 Threat Alert: {alert.threat_type} ({alert.severity}) from {alert.source_ip}")
    
    def handle_threat_detection(self, log_entry: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle real-time threat detection and broadcast results"""
        self.stats['model_requests'] += 1
        
        # Update average response time
        response_time = result.get('inference_time_ms', 0)
        total_requests = self.stats['model_requests']
        current_avg = self.stats['average_response_time']
        self.stats['average_response_time'] = (current_avg * (total_requests - 1) + response_time) / total_requests
        
        # If threat detected, create and broadcast alert
        if result.get('threat_detected', False):
            alert = ThreatAlert(
                id=f"detection_{int(time.time())}_{random.randint(1000, 9999)}",
                timestamp=datetime.now().isoformat(),
                threat_type=result.get('threat_level', 'unknown').title(),
                severity=result.get('threat_level', 'low'),
                source_ip='user_input',
                target='manual_analysis',
                description=f"Manual analysis: {log_entry[:100]}...",
                threat_score=result.get('threat_score', 0),
                confidence=result.get('confidence', 0),
                response_time_ms=response_time,
                blocked=False
            )
            
            self.broadcast_threat_alert(alert)
        
        return result
    
    def _broadcast_active_users(self):
        """Broadcast current active users to all clients"""
        user_data = [
            {
                'username': user.username,
                'active_page': user.active_page,
                'join_time': user.join_time
            }
            for user in self.active_users.values()
        ]
        
        self.socketio.emit('active_users_update', {
            'users': user_data,
            'count': len(user_data)
        }, namespace='/monitoring')
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get current threat detection statistics"""
        recent_threats = list(self.threat_history)[-50:]  # Last 50 threats
        
        # Calculate threat distribution
        threat_distribution = defaultdict(int)
        severity_distribution = defaultdict(int)
        
        for threat in recent_threats:
            threat_distribution[threat.threat_type] += 1
            severity_distribution[threat.severity] += 1
        
        # Calculate uptime
        uptime = datetime.now() - self.stats['uptime_start']
        uptime_hours = uptime.total_seconds() / 3600
        
        return {
            'total_threats': self.stats['total_threats_detected'],
            'threats_blocked': self.stats['threats_blocked'],
            'detection_rate': (self.stats['threats_blocked'] / max(self.stats['total_threats_detected'], 1)) * 100,
            'active_sessions': self.stats['active_sessions'],
            'uptime_hours': round(uptime_hours, 2),
            'model_requests': self.stats['model_requests'],
            'average_response_time': round(self.stats['average_response_time'], 2),
            'threat_distribution': dict(threat_distribution),
            'severity_distribution': dict(severity_distribution),
            'recent_activity': len([t for t in recent_threats if 
                                  (datetime.now() - datetime.fromisoformat(t.timestamp)).seconds < 300])
        }


# Global instance (will be initialized by the Flask app)
realtime_service: Optional[RealTimeService] = None


def init_realtime_service(socketio: SocketIO) -> RealTimeService:
    """Initialize the real-time service with SocketIO instance"""
    global realtime_service
    realtime_service = RealTimeService(socketio)
    return realtime_service


def get_realtime_service() -> Optional[RealTimeService]:
    """Get the current real-time service instance"""
    return realtime_service 