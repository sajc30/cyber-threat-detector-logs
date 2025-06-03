"""
Flask Application Factory for Cybersecurity Threat Detector

This module implements the Flask app factory pattern and will be fully
implemented during Phase 3: Backend API & Real-Time Inference.
"""

from flask import Flask
from flask_cors import CORS


def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config: Configuration object or dictionary
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Enable CORS for frontend integration
    CORS(app)
    
    # TODO: Phase 3 - Load ML model and threshold at startup
    # from .model_inference import load_model, infer_sequence
    # app.model, app.threshold = load_model("artifacts/model.pth", 0.95)
    
    # TODO: Phase 3 - Register blueprints
    # from .routes import bp
    # app.register_blueprint(bp, url_prefix="/api")
    
    @app.route("/health")
    def health_check():
        """Basic health check endpoint."""
        return {"status": "healthy", "service": "cyber-threat-detector"}
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000) 