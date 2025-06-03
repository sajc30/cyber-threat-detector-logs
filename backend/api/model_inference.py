"""
Model Inference Module for Real-Time Cybersecurity Threat Detection

This module provides real-time inference capabilities using our trained
LSTM autoencoder for anomaly detection in system logs.

Features:
- Real-time log analysis and threat scoring
- Batch processing for multiple logs
- Performance monitoring and caching
- Integration with feature extraction pipeline

Author: AI Cybersecurity System
"""

import os
import sys
import torch
import numpy as np
import pandas as pd
from pathlib import Path
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pickle
import json
import re

# Add model directory to path
sys.path.append(str(Path(__file__).parent.parent / "model"))

from feature_extractor import CybersecurityFeatureExtractor
from lstm_autoencoder import LSTMAutoencoder, CybersecurityLSTMTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatDetectionEngine:
    """
    Real-time threat detection engine using trained LSTM autoencoder
    """
    
    def __init__(self, model_path: str = None, feature_config_path: str = None):
        """
        Initialize the threat detection engine
        
        Args:
            model_path: Path to trained model file
            feature_config_path: Path to feature extractor configuration
        """
        self.model = None
        self.feature_extractor = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.optimal_threshold = None
        self.is_loaded = False
        
        # Performance tracking
        self.inference_times = []
        self.detection_count = 0
        self.threat_count = 0
        
        # Load model if paths provided
        if model_path and feature_config_path:
            self.load_model(model_path, feature_config_path)
    
    def load_model(self, model_path: str, feature_config_path: str):
        """Load trained model and feature extractor"""
        try:
            logger.info(f"🧠 Loading threat detection model...")
            
            # Load model checkpoint
            checkpoint = torch.load(model_path, map_location=self.device)
            model_config = checkpoint['model_config']
            
            # Create model with loaded configuration
            self.model = LSTMAutoencoder(**model_config)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            
            # Load feature extractor configuration
            self.feature_extractor = CybersecurityFeatureExtractor()
            self.feature_extractor.load_feature_config(feature_config_path)
            
            # Load optimal threshold from training results
            results_dir = Path(model_path).parent.parent / "results"
            latest_results = max(results_dir.glob("training_results_*.json"))
            
            with open(latest_results, 'r') as f:
                training_results = json.load(f)
                self.optimal_threshold = training_results['evaluation']['optimal_threshold']
            
            self.is_loaded = True
            logger.info(f"✅ Model loaded successfully:")
            logger.info(f"   🎯 Threshold: {self.optimal_threshold:.6f}")
            logger.info(f"   💻 Device: {self.device}")
            logger.info(f"   🏗️ Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def auto_load_latest_model(self):
        """Automatically load the latest trained model"""
        try:
            models_dir = Path(__file__).parent.parent.parent / "models"
            
            # Find latest model files
            model_files = list(models_dir.glob("cybersecurity_lstm_autoencoder_*.pth"))
            feature_files = list(models_dir.glob("feature_extractor_config_*.pkl"))
            
            if not model_files or not feature_files:
                raise FileNotFoundError("No trained models found")
            
            latest_model = max(model_files, key=os.path.getctime)
            latest_features = max(feature_files, key=os.path.getctime)
            
            self.load_model(str(latest_model), str(latest_features))
            
        except Exception as e:
            logger.error(f"❌ Failed to auto-load model: {e}")
            raise
    
    def preprocess_log(self, log_message: str, log_type: str = "system", 
                      source: str = "api", server: str = "unknown") -> pd.DataFrame:
        """
        Preprocess a single log message for inference
        
        Args:
            log_message: Raw log message
            log_type: Type of log (system, auth, web, etc.)
            source: Data source identifier
            server: Server identifier
            
        Returns:
            Preprocessed DataFrame ready for feature extraction
        """
        # Create a DataFrame with the log entry
        log_data = {
            'raw_message': log_message,
            'message_length': len(log_message),
            'log_type': log_type,
            'source': source,
            'server': server,
            'is_attack': 0  # Unknown, will be predicted
        }
        
        # Add basic feature extraction
        message = log_message.lower()
        
        # Basic cybersecurity indicators
        log_data.update({
            'has_ip': int(bool(re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', log_message))),
            'has_error': int(any(word in message for word in ['error', 'failed', 'exception', 'critical'])),
            'has_auth': int(any(word in message for word in ['login', 'auth', 'password', 'user'])),
            'entropy': self._calculate_entropy(log_message),
            'severity_score': self._calculate_severity_score(message),
            'attack_score': 0.0  # Will be calculated by feature extractor
        })
        
        return pd.DataFrame([log_data])
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        import math
        from collections import Counter
        
        if not text:
            return 0.0
        
        counter = Counter(text)
        length = len(text)
        entropy = -sum((count/length) * math.log2(count/length) for count in counter.values())
        
        return min(entropy, 8.0)  # Cap at 8 bits
    
    def _calculate_severity_score(self, message: str) -> float:
        """Calculate severity score based on keywords"""
        high_severity = ['critical', 'emergency', 'panic', 'fatal', 'alert']
        medium_severity = ['warning', 'error', 'failed', 'denied', 'blocked']
        low_severity = ['info', 'debug', 'notice']
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in high_severity):
            return 0.9
        elif any(word in message_lower for word in medium_severity):
            return 0.6
        elif any(word in message_lower for word in low_severity):
            return 0.3
        else:
            return 0.5
    
    def analyze_single_log(self, log_message: str, **kwargs) -> Dict:
        """
        Analyze a single log message for threats
        
        Args:
            log_message: Raw log message to analyze
            **kwargs: Additional metadata (log_type, source, server)
            
        Returns:
            Dictionary with threat analysis results
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() or auto_load_latest_model() first.")
        
        start_time = time.time()
        
        try:
            # Preprocess log
            log_df = self.preprocess_log(log_message, **kwargs)
            
            # Extract features
            enhanced_df = self.feature_extractor.extract_features(log_df)
            
            # Select numerical features
            numeric_features = self.feature_extractor._select_numeric_features(enhanced_df)
            X = enhanced_df[numeric_features].values
            
            # Handle missing values
            X = np.nan_to_num(X, nan=0.0, posinf=1.0, neginf=-1.0)
            
            # Apply feature selection and scaling
            X_selected = self.feature_extractor.feature_selector.transform(X)
            X_scaled = self.feature_extractor.scaler.transform(X_selected)
            
            # Create sequence (pad if necessary)
            if len(X_scaled) < self.feature_extractor.sequence_length:
                padding = np.zeros((self.feature_extractor.sequence_length - len(X_scaled), X_scaled.shape[1]))
                X_padded = np.vstack([padding, X_scaled])
                X_sequence = X_padded.reshape(1, self.feature_extractor.sequence_length, X_scaled.shape[1])
            else:
                X_sequence = X_scaled[-self.feature_extractor.sequence_length:].reshape(1, self.feature_extractor.sequence_length, X_scaled.shape[1])
            
            # Convert to tensor
            X_tensor = torch.FloatTensor(X_sequence).to(self.device)
            
            # Get model predictions
            with torch.no_grad():
                reconstruction_error = self.model.get_reconstruction_error(X_tensor, reduction='mean')
                anomaly_score = self.model.get_anomaly_scores(X_tensor)[0]
                is_threat = reconstruction_error.item() > self.optimal_threshold
            
            # Calculate inference time
            inference_time = time.time() - start_time
            self.inference_times.append(inference_time)
            self.detection_count += 1
            
            if is_threat:
                self.threat_count += 1
            
            # Threat level classification
            threat_level = self._classify_threat_level(anomaly_score)
            
            result = {
                'log_message': log_message,
                'is_threat': bool(is_threat),
                'threat_level': threat_level,
                'anomaly_score': float(anomaly_score),
                'reconstruction_error': float(reconstruction_error.item()),
                'threshold': float(self.optimal_threshold),
                'confidence': min(float(anomaly_score), 1.0),
                'inference_time_ms': round(inference_time * 1000, 2),
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'log_type': kwargs.get('log_type', 'system'),
                    'source': kwargs.get('source', 'api'),
                    'server': kwargs.get('server', 'unknown')
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing log: {e}")
            return {
                'log_message': log_message,
                'is_threat': False,
                'threat_level': 'error',
                'anomaly_score': 0.0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_batch_logs(self, log_messages: List[str], **kwargs) -> List[Dict]:
        """
        Analyze multiple log messages in batch
        
        Args:
            log_messages: List of log messages to analyze
            **kwargs: Additional metadata for all logs
            
        Returns:
            List of threat analysis results
        """
        logger.info(f"🔍 Analyzing batch of {len(log_messages)} logs...")
        
        results = []
        start_time = time.time()
        
        for i, log_message in enumerate(log_messages):
            try:
                result = self.analyze_single_log(log_message, **kwargs)
                results.append(result)
                
                # Log progress for large batches
                if len(log_messages) > 100 and (i + 1) % 100 == 0:
                    logger.info(f"   📊 Processed {i + 1}/{len(log_messages)} logs...")
                    
            except Exception as e:
                logger.error(f"❌ Error processing log {i}: {e}")
                results.append({
                    'log_message': log_message,
                    'is_threat': False,
                    'threat_level': 'error',
                    'error': str(e)
                })
        
        batch_time = time.time() - start_time
        threat_count = sum(1 for r in results if r.get('is_threat', False))
        
        logger.info(f"✅ Batch analysis complete:")
        logger.info(f"   📊 Processed: {len(results)} logs")
        logger.info(f"   🚨 Threats detected: {threat_count}")
        logger.info(f"   ⏱️ Total time: {batch_time:.2f}s")
        logger.info(f"   📈 Avg time per log: {(batch_time/len(log_messages)*1000):.2f}ms")
        
        return results
    
    def _classify_threat_level(self, anomaly_score: float) -> str:
        """Classify threat level based on anomaly score"""
        if anomaly_score >= 0.9:
            return 'critical'
        elif anomaly_score >= 0.7:
            return 'high'
        elif anomaly_score >= 0.5:
            return 'medium'
        elif anomaly_score >= 0.3:
            return 'low'
        else:
            return 'normal'
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        if not self.inference_times:
            return {'message': 'No inferences performed yet'}
        
        return {
            'total_detections': self.detection_count,
            'threats_detected': self.threat_count,
            'threat_rate': round(self.threat_count / self.detection_count * 100, 2) if self.detection_count > 0 else 0,
            'avg_inference_time_ms': round(np.mean(self.inference_times) * 1000, 2),
            'min_inference_time_ms': round(np.min(self.inference_times) * 1000, 2),
            'max_inference_time_ms': round(np.max(self.inference_times) * 1000, 2),
            'threshold': self.optimal_threshold,
            'model_loaded': self.is_loaded,
            'device': str(self.device)
        }

# Global inference engine instance
_inference_engine = None

def get_inference_engine() -> ThreatDetectionEngine:
    """Get global inference engine instance"""
    global _inference_engine
    
    if _inference_engine is None:
        _inference_engine = ThreatDetectionEngine()
        try:
            _inference_engine.auto_load_latest_model()
        except Exception as e:
            logger.warning(f"⚠️ Could not auto-load model: {e}")
    
    return _inference_engine

def analyze_log(log_message: str, **kwargs) -> Dict:
    """Convenience function for single log analysis"""
    engine = get_inference_engine()
    return engine.analyze_single_log(log_message, **kwargs)

def analyze_logs_batch(log_messages: List[str], **kwargs) -> List[Dict]:
    """Convenience function for batch log analysis"""
    engine = get_inference_engine()
    return engine.analyze_batch_logs(log_messages, **kwargs) 