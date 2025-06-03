"""
Flask Application for Cybersecurity Threat Detection System

Main application entry point providing:
- REST API endpoints for threat detection
- Admin dashboard
- Health monitoring and metrics
- Real-time log analysis capabilities

Author: AI Cybersecurity System
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import logging
import os
from datetime import datetime
from pathlib import Path

# Import our API routes
from routes import api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config=None):
    """
    Application factory for creating Flask app
    
    Args:
        config: Configuration object or dictionary
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Default configuration
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
        'DEBUG': os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        'HOST': os.environ.get('FLASK_HOST', '0.0.0.0'),
        'PORT': int(os.environ.get('FLASK_PORT', 5000)),
        'THREADED': True,
        'JSON_SORT_KEYS': False
    })
    
    # Apply custom config if provided
    if config:
        app.config.update(config)
    
    # Enable CORS for API endpoints
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register API blueprint
    app.register_blueprint(api, url_prefix='/api')
    
    # Root endpoint
    @app.route('/')
    def index():
        """
        Landing page with API information
        """
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cybersecurity Threat Detection API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; color: #2c3e50; margin-bottom: 30px; }
                .status { display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; }
                .operational { background-color: #27ae60; }
                .warning { background-color: #f39c12; }
                .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
                .method { display: inline-block; padding: 3px 8px; border-radius: 3px; color: white; font-size: 12px; margin-right: 10px; }
                .get { background-color: #27ae60; }
                .post { background-color: #e74c3c; }
                ul { margin: 10px 0; padding-left: 20px; }
                .footer { text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Cybersecurity Threat Detection API</h1>
                    <p>AI-Enhanced System-Log-Based Threat Detection</p>
                    <span class="status operational">System Operational</span>
                </div>
                
                <h2>📡 Available API Endpoints</h2>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/health</strong>
                    <p>System health check and status information</p>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <strong>/api/detect</strong>
                    <p>Analyze a single log message for cybersecurity threats</p>
                    <ul>
                        <li>Payload: <code>{"log_message": "string", "log_type": "optional"}</code></li>
                        <li>Returns: Threat analysis with anomaly score and threat level</li>
                    </ul>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <strong>/api/detect/batch</strong>
                    <p>Analyze multiple log messages in batch</p>
                    <ul>
                        <li>Payload: <code>{"log_messages": ["string1", "string2", ...]}</code></li>
                        <li>Returns: Batch analysis with summary statistics</li>
                    </ul>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/stats</strong>
                    <p>Get system performance statistics and metrics</p>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/metrics</strong>
                    <p>Detailed performance metrics for monitoring</p>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/admin/dashboard</strong>
                    <p>Admin dashboard for system monitoring</p>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/test</strong>
                    <p>Test endpoint with sample threat detection</p>
                </div>
                
                <h2>🚀 Quick Start</h2>
                <p><strong>Test the API:</strong></p>
                <pre style="background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto;">
curl -X POST {{ request.url_root }}api/detect \\
  -H "Content-Type: application/json" \\
  -d '{"log_message": "CRITICAL: Unauthorized access attempt detected"}'</pre>
                
                <div class="footer">
                    <p>⚡ Powered by PyTorch LSTM Autoencoder | 🔬 AI Cybersecurity Research</p>
                    <p>Server Time: {{ timestamp }}</p>
                </div>
            </div>
        </body>
        </html>
        """, timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'))
    
    # Global error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({
            'error': 'Page not found',
            'message': 'The requested resource does not exist',
            'available_endpoints': {
                'api_root': '/api/',
                'health_check': '/api/health',
                'threat_detection': '/api/detect',
                'batch_detection': '/api/detect/batch',
                'statistics': '/api/stats',
                'admin_dashboard': '/api/admin/dashboard'
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    # Add startup message - Initialize inference engine on first import
    try:
        from model_inference import get_inference_engine
        engine = get_inference_engine()
        if engine.is_loaded:
            logger.info("✅ Threat detection model loaded successfully")
        else:
            logger.warning("⚠️ Threat detection model not loaded - some endpoints may not work")
    except Exception as e:
        logger.error(f"❌ Failed to initialize inference engine: {e}")
    
    logger.info("🛡️ Cybersecurity Threat Detection API ready...")
    logger.info(f"🔧 Debug mode: {app.config['DEBUG']}")
    logger.info(f"🌐 Host: {app.config['HOST']}:{app.config['PORT']}")
    
    return app

# Create the application instance
app = create_app()

# Simple admin dashboard template
ADMIN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Cybersecurity Threat Detection - Admin Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
        .dashboard { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #2c3e50; margin-bottom: 10px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .stat-value { font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }
        .stat-label { color: #7f8c8d; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
        .operational { color: #27ae60; }
        .warning { color: #f39c12; }
        .danger { color: #e74c3c; }
        .info { color: #3498db; }
        .system-info { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 0; }
        .refresh-btn:hover { background: #2980b9; }
        .timestamp { text-align: center; color: #7f8c8d; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🛡️ Cybersecurity Threat Detection Dashboard</h1>
            <p>Real-time system monitoring and threat analysis</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value {{ 'operational' if model_loaded else 'danger' }}">
                    {{ 'ONLINE' if model_loaded else 'OFFLINE' }}
                </div>
                <div class="stat-label">System Status</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value info">{{ total_detections }}</div>
                <div class="stat-label">Total Detections</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value {{ 'danger' if threats_detected > 0 else 'operational' }}">
                    {{ threats_detected }}
                </div>
                <div class="stat-label">Threats Detected</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value {{ 'warning' if threat_rate > 10 else 'info' }}">
                    {{ "%.1f"|format(threat_rate) }}%
                </div>
                <div class="stat-label">Threat Rate</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value info">{{ "%.1f"|format(avg_response_time) }}ms</div>
                <div class="stat-label">Avg Response Time</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value info">{{ device }}</div>
                <div class="stat-label">Processing Device</div>
            </div>
        </div>
        
        <div class="system-info">
            <h3>System Information</h3>
            <p><strong>Detection Threshold:</strong> {{ "%.6f"|format(threshold) if threshold else 'N/A' }}</p>
            <p><strong>Model Status:</strong> {{ 'Loaded and Ready' if model_loaded else 'Not Loaded' }}</p>
            <p><strong>Last Updated:</strong> {{ timestamp }}</p>
            
            <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh Dashboard</button>
            <button class="refresh-btn" onclick="reloadModel()">🧠 Reload Model</button>
        </div>
        
        <div class="timestamp">
            Dashboard generated at {{ timestamp }}
        </div>
    </div>
    
    <script>
        function reloadModel() {
            fetch('/api/admin/reload_model', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message || 'Model reload completed');
                    window.location.reload();
                })
                .catch(error => {
                    alert('Error reloading model: ' + error);
                });
        }
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            window.location.reload();
        }, 30000);
    </script>
</body>
</html>
"""

# Create templates directory and save dashboard template
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)

with open(templates_dir / "admin_dashboard.html", "w") as f:
    f.write(ADMIN_DASHBOARD_TEMPLATE)

if __name__ == '__main__':
    # Development server
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'],
        threaded=app.config['THREADED']
    ) 