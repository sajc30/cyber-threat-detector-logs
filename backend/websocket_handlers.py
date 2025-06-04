#!/usr/bin/env python3
"""
WebSocket Event Handlers for CyberGuard AI Real-Time Features
Handles all SocketIO events for live monitoring and collaboration
"""

from flask import request
from flask_socketio import emit, join_room, leave_room, disconnect
from typing import Dict, Any

from realtime_service import get_realtime_service


def register_websocket_handlers(socketio):
    """Register all WebSocket event handlers"""
    
    @socketio.on('connect', namespace='/monitoring')
    def handle_connect(auth=None):
        """Handle client connection to monitoring namespace"""
        try:
            session_id = request.sid
            client_info = auth or {}
            username = client_info.get('username', f'User_{session_id[:8]}')
            
            print(f"🔌 Client connecting: {session_id} (Username: {username})")
            
            # Get real-time service
            rt_service = get_realtime_service()
            if rt_service:
                rt_service.handle_user_connect(session_id, username)
                
                # Send initial connection success
                emit('connection_status', {
                    'status': 'connected',
                    'session_id': session_id,
                    'timestamp': rt_service.stats.get('uptime_start', '').isoformat() if hasattr(rt_service.stats.get('uptime_start', ''), 'isoformat') else str(rt_service.stats.get('uptime_start', '')),
                    'message': 'Successfully connected to CyberGuard AI real-time monitoring'
                })
                
            else:
                emit('connection_status', {
                    'status': 'error',
                    'message': 'Real-time service unavailable'
                })
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            emit('connection_status', {
                'status': 'error',
                'message': f'Connection failed: {str(e)}'
            })
    
    @socketio.on('disconnect', namespace='/monitoring')
    def handle_disconnect():
        """Handle client disconnection"""
        try:
            session_id = request.sid
            print(f"🔌 Client disconnecting: {session_id}")
            
            rt_service = get_realtime_service()
            if rt_service:
                rt_service.handle_user_disconnect(session_id)
                
        except Exception as e:
            print(f"❌ Disconnect error: {e}")
    
    @socketio.on('join_monitoring', namespace='/monitoring')
    def handle_join_monitoring(data=None):
        """Handle user joining monitoring room"""
        try:
            session_id = request.sid
            username = data.get('username', f'User_{session_id[:8]}') if data else f'User_{session_id[:8]}'
            
            join_room('monitoring_room')
            
            rt_service = get_realtime_service()
            if rt_service:
                rt_service.handle_page_change(session_id, 'monitoring')
                
                # Send current monitoring data
                emit('monitoring_data', {
                    'recent_threats': [rt_service.threat_history[i].__dict__ for i in range(max(0, len(rt_service.threat_history)-10), len(rt_service.threat_history))],
                    'statistics': rt_service.get_threat_statistics(),
                    'active_users': len(rt_service.active_users)
                })
                
            emit('room_joined', {
                'room': 'monitoring_room',
                'username': username,
                'timestamp': 'now'
            })
            
            print(f"📊 {username} joined monitoring room")
            
        except Exception as e:
            print(f"❌ Join monitoring error: {e}")
            emit('error', {'message': f'Failed to join monitoring: {str(e)}'})
    
    @socketio.on('leave_monitoring', namespace='/monitoring')
    def handle_leave_monitoring():
        """Handle user leaving monitoring room"""
        try:
            session_id = request.sid
            leave_room('monitoring_room')
            
            rt_service = get_realtime_service()
            if rt_service and session_id in rt_service.active_users:
                username = rt_service.active_users[session_id].username
                emit('room_left', {
                    'room': 'monitoring_room',
                    'username': username
                })
                print(f"📊 {username} left monitoring room")
                
        except Exception as e:
            print(f"❌ Leave monitoring error: {e}")
    
    @socketio.on('request_live_data', namespace='/monitoring')
    def handle_request_live_data(data=None):
        """Handle request for live data updates"""
        try:
            session_id = request.sid
            data_type = data.get('type', 'all') if data else 'all'
            
            rt_service = get_realtime_service()
            if not rt_service:
                emit('error', {'message': 'Real-time service unavailable'})
                return
            
            response_data = {}
            
            if data_type in ['all', 'threats']:
                response_data['threats'] = [
                    threat.__dict__ for threat in list(rt_service.threat_history)[-20:]
                ]
            
            if data_type in ['all', 'metrics']:
                response_data['metrics'] = [
                    metrics.__dict__ for metrics in list(rt_service.metrics_history)[-10:]
                ]
            
            if data_type in ['all', 'statistics']:
                response_data['statistics'] = rt_service.get_threat_statistics()
            
            if data_type in ['all', 'users']:
                response_data['active_users'] = [
                    {
                        'username': user.username,
                        'active_page': user.active_page,
                        'join_time': user.join_time
                    }
                    for user in rt_service.active_users.values()
                ]
            
            emit('live_data_response', {
                'type': data_type,
                'data': response_data,
                'timestamp': 'now'
            })
            
        except Exception as e:
            print(f"❌ Live data request error: {e}")
            emit('error', {'message': f'Failed to get live data: {str(e)}'})
    
    @socketio.on('manual_threat_analysis', namespace='/monitoring')
    def handle_manual_threat_analysis(data):
        """Handle manual threat analysis request"""
        try:
            session_id = request.sid
            log_entry = data.get('log_entry', '')
            
            if not log_entry.strip():
                emit('analysis_error', {'message': 'Log entry cannot be empty'})
                return
            
            rt_service = get_realtime_service()
            if not rt_service:
                emit('analysis_error', {'message': 'Real-time service unavailable'})
                return
            
            # Simulate threat analysis (in real implementation, this would call the AI model)
            import random
            import time
            
            # Simulate processing time
            processing_time = random.uniform(1.0, 3.0)
            time.sleep(processing_time / 1000)  # Convert to actual seconds
            
            # Generate mock analysis result
            suspicious_keywords = ['SELECT', 'DROP', 'DELETE', 'UPDATE', 'UNION', 'admin', 'password', 'login', 'failed', 'error', 'attack', 'malware', 'virus']
            is_threat = any(keyword.lower() in log_entry.lower() for keyword in suspicious_keywords)
            
            result = {
                'threat_detected': is_threat,
                'threat_level': random.choice(['low', 'medium', 'high']) if is_threat else 'normal',
                'threat_score': random.uniform(0.6, 0.95) if is_threat else random.uniform(0.0, 0.3),
                'confidence': random.uniform(0.8, 0.99),
                'inference_time_ms': processing_time,
                'features_extracted': random.randint(45, 55),
                'log_entry': log_entry,
                'timestamp': 'now'
            }
            
            # Broadcast through real-time service
            rt_service.handle_threat_detection(log_entry, result)
            
            # Send result back to requesting client
            emit('analysis_result', result)
            
            print(f"🔍 Manual analysis: {log_entry[:50]}... -> {'THREAT' if is_threat else 'SAFE'}")
            
        except Exception as e:
            print(f"❌ Manual analysis error: {e}")
            emit('analysis_error', {'message': f'Analysis failed: {str(e)}'})
    
    @socketio.on('acknowledge_threat', namespace='/monitoring')
    def handle_acknowledge_threat(data):
        """Handle threat acknowledgment by user"""
        try:
            session_id = request.sid
            threat_id = data.get('threat_id')
            action = data.get('action', 'acknowledged')  # acknowledged, investigated, blocked
            
            rt_service = get_realtime_service()
            if not rt_service:
                emit('error', {'message': 'Real-time service unavailable'})
                return
            
            username = rt_service.active_users.get(session_id, {}).username if session_id in rt_service.active_users else 'Unknown'
            
            # Broadcast threat acknowledgment to all monitoring users
            emit('threat_acknowledged', {
                'threat_id': threat_id,
                'action': action,
                'user': username,
                'timestamp': 'now'
            }, room='monitoring_room')
            
            print(f"✅ Threat {threat_id} {action} by {username}")
            
        except Exception as e:
            print(f"❌ Threat acknowledgment error: {e}")
            emit('error', {'message': f'Failed to acknowledge threat: {str(e)}'})
    
    @socketio.on('request_system_status', namespace='/monitoring')
    def handle_request_system_status():
        """Handle system status request"""
        try:
            rt_service = get_realtime_service()
            if not rt_service:
                emit('system_status_response', {
                    'status': 'error',
                    'message': 'Real-time service unavailable'
                })
                return
            
            status_data = {
                'status': 'operational',
                'uptime_hours': (rt_service.stats.get('uptime_start', '')),
                'active_connections': len(rt_service.active_users),
                'total_threats': rt_service.stats['total_threats_detected'],
                'threats_blocked': rt_service.stats['threats_blocked'],
                'model_requests': rt_service.stats['model_requests'],
                'average_response_time': rt_service.stats['average_response_time'],
                'services': {
                    'threat_detection': 'online',
                    'real_time_monitoring': 'online',
                    'websocket_server': 'online',
                    'ai_model': 'active'
                }
            }
            
            emit('system_status_response', status_data)
            
        except Exception as e:
            print(f"❌ System status error: {e}")
            emit('system_status_response', {
                'status': 'error',
                'message': f'Failed to get system status: {str(e)}'
            })
    
    @socketio.on('send_message', namespace='/monitoring')
    def handle_send_message(data):
        """Handle chat message between users"""
        try:
            session_id = request.sid
            message = data.get('message', '')
            
            rt_service = get_realtime_service()
            if not rt_service or session_id not in rt_service.active_users:
                emit('error', {'message': 'User session not found'})
                return
            
            username = rt_service.active_users[session_id].username
            
            # Broadcast message to all monitoring users
            emit('user_message', {
                'username': username,
                'message': message,
                'timestamp': 'now',
                'session_id': session_id[:8]  # Short ID for privacy
            }, room='monitoring_room', include_self=False)
            
            # Confirm message sent to sender
            emit('message_sent', {
                'message': message,
                'timestamp': 'now'
            })
            
            print(f"💬 Message from {username}: {message}")
            
        except Exception as e:
            print(f"❌ Message error: {e}")
            emit('error', {'message': f'Failed to send message: {str(e)}'})
    
    @socketio.on('ping', namespace='/monitoring')
    def handle_ping():
        """Handle ping for connection testing"""
        emit('pong', {'timestamp': 'now'})
    
    # Error handler
    @socketio.on_error(namespace='/monitoring')
    def handle_error(e):
        """Handle WebSocket errors"""
        print(f"❌ WebSocket error: {e}")
        emit('error', {'message': f'WebSocket error: {str(e)}'})


def register_general_handlers(socketio):
    """Register general WebSocket handlers (non-namespaced)"""
    
    @socketio.on('connect')
    def handle_general_connect():
        """Handle general connection"""
        session_id = request.sid
        print(f"🔌 General connection: {session_id}")
        emit('connected', {
            'status': 'connected',
            'session_id': session_id,
            'message': 'Connected to CyberGuard AI'
        })
    
    @socketio.on('disconnect')
    def handle_general_disconnect():
        """Handle general disconnection"""
        session_id = request.sid
        print(f"🔌 General disconnection: {session_id}")


# Export registration functions
__all__ = ['register_websocket_handlers', 'register_general_handlers'] 