#!/usr/bin/env python3
"""
Database module for CyberGuard AI threat detection system
Handles threat storage, retrieval, and database operations
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

# Database configuration
DATABASE_PATH = 'data/threats.db'


def init_db():
    """Initialize the database with required tables"""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    with get_db_connection() as conn:
        # Create threats table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                log_entry TEXT NOT NULL,
                threat_level TEXT NOT NULL,
                threat_score REAL NOT NULL,
                confidence REAL NOT NULL,
                source_ip TEXT,
                target TEXT,
                threat_type TEXT,
                description TEXT,
                blocked BOOLEAN DEFAULT 0,
                investigated BOOLEAN DEFAULT 0,
                response_time_ms REAL,
                features_extracted INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create system_metrics table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_usage REAL,
                memory_usage REAL,
                network_io_in REAL,
                network_io_out REAL,
                active_connections INTEGER,
                threats_per_minute INTEGER,
                model_inference_time REAL,
                queue_size INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create user_sessions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                join_time TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                active_page TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indices for better performance
        conn.execute('CREATE INDEX IF NOT EXISTS idx_threats_timestamp ON threats(timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_threats_level ON threats(threat_level)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_threats_created ON threats(created_at)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON user_sessions(session_id)')
        
        conn.commit()
        print("✅ Database initialized successfully")


@contextmanager
def get_db_connection():
    """Get database connection with context manager"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"❌ Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def log_threat(log_entry: str, threat_level: str, threat_score: float, confidence: float, **kwargs) -> int:
    """Log a threat detection to the database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO threats (
                    timestamp, log_entry, threat_level, threat_score, confidence,
                    source_ip, target, threat_type, description, blocked, 
                    investigated, response_time_ms, features_extracted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                log_entry,
                threat_level,
                threat_score,
                confidence,
                kwargs.get('source_ip'),
                kwargs.get('target'),
                kwargs.get('threat_type'),
                kwargs.get('description'),
                kwargs.get('blocked', False),
                kwargs.get('investigated', False),
                kwargs.get('response_time_ms'),
                kwargs.get('features_extracted')
            ))
            
            threat_id = cursor.lastrowid
            conn.commit()
            
            print(f"✅ Threat logged: ID {threat_id}, Level: {threat_level}, Score: {threat_score:.3f}")
            return threat_id
            
    except Exception as e:
        print(f"❌ Failed to log threat: {e}")
        return -1


def get_recent_threats(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Get recent threats from the database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM threats 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            threats = []
            for row in cursor.fetchall():
                threat = {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'log_entry': row['log_entry'],
                    'threat_level': row['threat_level'],
                    'threat_score': row['threat_score'],
                    'confidence': row['confidence'],
                    'source_ip': row['source_ip'],
                    'target': row['target'],
                    'threat_type': row['threat_type'],
                    'description': row['description'],
                    'blocked': bool(row['blocked']),
                    'investigated': bool(row['investigated']),
                    'response_time_ms': row['response_time_ms'],
                    'features_extracted': row['features_extracted'],
                    'created_at': row['created_at']
                }
                threats.append(threat)
            
            return threats
            
    except Exception as e:
        print(f"❌ Failed to get recent threats: {e}")
        return []


def get_threat_by_id(threat_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific threat by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('SELECT * FROM threats WHERE id = ?', (threat_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'log_entry': row['log_entry'],
                    'threat_level': row['threat_level'],
                    'threat_score': row['threat_score'],
                    'confidence': row['confidence'],
                    'source_ip': row['source_ip'],
                    'target': row['target'],
                    'threat_type': row['threat_type'],
                    'description': row['description'],
                    'blocked': bool(row['blocked']),
                    'investigated': bool(row['investigated']),
                    'response_time_ms': row['response_time_ms'],
                    'features_extracted': row['features_extracted'],
                    'created_at': row['created_at']
                }
            return None
            
    except Exception as e:
        print(f"❌ Failed to get threat by ID: {e}")
        return None


def update_threat_status(threat_id: int, blocked: bool = None, investigated: bool = None) -> bool:
    """Update threat investigation/block status"""
    try:
        with get_db_connection() as conn:
            updates = []
            params = []
            
            if blocked is not None:
                updates.append('blocked = ?')
                params.append(blocked)
            
            if investigated is not None:
                updates.append('investigated = ?')
                params.append(investigated)
            
            if not updates:
                return False
            
            params.append(threat_id)
            query = f"UPDATE threats SET {', '.join(updates)} WHERE id = ?"
            
            cursor = conn.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
            
    except Exception as e:
        print(f"❌ Failed to update threat status: {e}")
        return False


def get_threat_statistics(days: int = 7) -> Dict[str, Any]:
    """Get threat statistics for the specified number of days"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()
        
        with get_db_connection() as conn:
            # Total threats
            cursor = conn.execute(
                'SELECT COUNT(*) as total FROM threats WHERE created_at >= ?',
                (cutoff_str,)
            )
            total_threats = cursor.fetchone()['total']
            
            # Threats by level
            cursor = conn.execute('''
                SELECT threat_level, COUNT(*) as count 
                FROM threats 
                WHERE created_at >= ? 
                GROUP BY threat_level
            ''', (cutoff_str,))
            threats_by_level = {row['threat_level']: row['count'] for row in cursor.fetchall()}
            
            # Blocked threats
            cursor = conn.execute(
                'SELECT COUNT(*) as blocked FROM threats WHERE created_at >= ? AND blocked = 1',
                (cutoff_str,)
            )
            blocked_threats = cursor.fetchone()['blocked']
            
            # Average threat score
            cursor = conn.execute(
                'SELECT AVG(threat_score) as avg_score FROM threats WHERE created_at >= ?',
                (cutoff_str,)
            )
            avg_score = cursor.fetchone()['avg_score'] or 0
            
            # Average response time
            cursor = conn.execute(
                'SELECT AVG(response_time_ms) as avg_time FROM threats WHERE created_at >= ? AND response_time_ms IS NOT NULL',
                (cutoff_str,)
            )
            avg_response_time = cursor.fetchone()['avg_time'] or 0
            
            return {
                'total_threats': total_threats,
                'blocked_threats': blocked_threats,
                'detection_rate': (blocked_threats / max(total_threats, 1)) * 100,
                'threats_by_level': threats_by_level,
                'average_threat_score': round(avg_score, 3),
                'average_response_time': round(avg_response_time, 2),
                'period_days': days
            }
            
    except Exception as e:
        print(f"❌ Failed to get threat statistics: {e}")
        return {}


def log_system_metrics(metrics: Dict[str, Any]) -> bool:
    """Log system performance metrics"""
    try:
        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO system_metrics (
                    timestamp, cpu_usage, memory_usage, network_io_in, network_io_out,
                    active_connections, threats_per_minute, model_inference_time, queue_size
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.get('timestamp', datetime.now().isoformat()),
                metrics.get('cpu_usage'),
                metrics.get('memory_usage'),
                metrics.get('network_io', {}).get('bytes_in'),
                metrics.get('network_io', {}).get('bytes_out'),
                metrics.get('active_connections'),
                metrics.get('threats_per_minute'),
                metrics.get('model_inference_time'),
                metrics.get('queue_size')
            ))
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"❌ Failed to log system metrics: {e}")
        return False


def cleanup_old_data(days_to_keep: int = 30):
    """Clean up old data to prevent database from growing too large"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.isoformat()
        
        with get_db_connection() as conn:
            # Clean up old threats (keep investigated ones longer)
            cursor = conn.execute('''
                DELETE FROM threats 
                WHERE created_at < ? AND investigated = 0 AND threat_level NOT IN ('high', 'critical')
            ''', (cutoff_str,))
            threats_deleted = cursor.rowcount
            
            # Clean up old system metrics
            cursor = conn.execute('''
                DELETE FROM system_metrics 
                WHERE created_at < ?
            ''', (cutoff_str,))
            metrics_deleted = cursor.rowcount
            
            # Clean up old user sessions
            cursor = conn.execute('''
                DELETE FROM user_sessions 
                WHERE created_at < ?
            ''', (cutoff_str,))
            sessions_deleted = cursor.rowcount
            
            conn.commit()
            
            print(f"🧹 Cleanup completed: {threats_deleted} threats, {metrics_deleted} metrics, {sessions_deleted} sessions deleted")
            return True
            
    except Exception as e:
        print(f"❌ Failed to cleanup old data: {e}")
        return False


def get_database_stats() -> Dict[str, Any]:
    """Get database statistics"""
    try:
        with get_db_connection() as conn:
            stats = {}
            
            # Count records in each table
            for table in ['threats', 'system_metrics', 'user_sessions']:
                cursor = conn.execute(f'SELECT COUNT(*) as count FROM {table}')
                stats[f'{table}_count'] = cursor.fetchone()['count']
            
            # Database file size
            if os.path.exists(DATABASE_PATH):
                stats['database_size_mb'] = round(os.path.getsize(DATABASE_PATH) / (1024 * 1024), 2)
            else:
                stats['database_size_mb'] = 0
            
            return stats
            
    except Exception as e:
        print(f"❌ Failed to get database stats: {e}")
        return {}


# Export main functions
__all__ = [
    'init_db',
    'log_threat',
    'get_recent_threats',
    'get_threat_by_id',
    'update_threat_status',
    'get_threat_statistics',
    'log_system_metrics',
    'cleanup_old_data',
    'get_database_stats'
] 