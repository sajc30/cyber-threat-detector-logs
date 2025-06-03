"""
Training Pipeline for Cybersecurity LSTM Autoencoder
Implements end-to-end training with performance evaluation

This module:
1. Loads processed cybersecurity datasets
2. Extracts and engineers features
3. Trains LSTM autoencoder model
4. Evaluates performance against target metrics
5. Saves trained model and results

Target Performance:
- Precision ≥ 85%
- Recall ≥ 90%
- F1-Score ≥ 0.88
- ROC-AUC ≥ 0.92

Author: AI Cybersecurity System
"""

import os
import sys
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    classification_report, confusion_matrix, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import time
from datetime import datetime
import json

# Import our modules
from feature_extractor import CybersecurityFeatureExtractor
from lstm_autoencoder import LSTMAutoencoder, CybersecurityLSTMTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CybersecurityTrainingPipeline:
    """
    Complete training pipeline for cybersecurity threat detection
    """
    
    def __init__(self, 
                 data_path: str = "../../data/processed",
                 model_save_path: str = "../../models",
                 results_path: str = "../../results"):
        
        self.data_path = Path(data_path)
        self.model_save_path = Path(model_save_path)
        self.results_path = Path(results_path)
        
        # Create directories
        self.model_save_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.feature_extractor = None
        self.model = None
        self.trainer = None
        
        # Data storage
        self.train_data = None
        self.val_data = None
        self.test_data = None
        
        # Results storage
        self.results = {}
        
    def load_data(self):
        """Load processed cybersecurity datasets"""
        logger.info("📁 Loading cybersecurity datasets...")
        
        try:
            self.train_data = pd.read_csv(self.data_path / "unified_train.csv")
            self.val_data = pd.read_csv(self.data_path / "unified_validation.csv")
            self.test_data = pd.read_csv(self.data_path / "unified_test.csv")
            
            logger.info(f"✅ Data loaded successfully:")
            logger.info(f"   📈 Training: {len(self.train_data)} samples")
            logger.info(f"   📊 Validation: {len(self.val_data)} samples")
            logger.info(f"   🧪 Test: {len(self.test_data)} samples")
            
            # Show attack distribution
            train_attacks = self.train_data['is_attack'].sum()
            val_attacks = self.val_data['is_attack'].sum()
            test_attacks = self.test_data['is_attack'].sum()
            
            logger.info(f"🚨 Attack distribution:")
            logger.info(f"   📈 Training: {train_attacks}/{len(self.train_data)} ({train_attacks/len(self.train_data)*100:.1f}%)")
            logger.info(f"   📊 Validation: {val_attacks}/{len(self.val_data)} ({val_attacks/len(self.val_data)*100:.1f}%)")
            logger.info(f"   🧪 Test: {test_attacks}/{len(self.test_data)} ({test_attacks/len(self.test_data)*100:.1f}%)")
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            raise
    
    def extract_features(self):
        """Extract and engineer features for model training"""
        logger.info("🔧 Extracting features for model training...")
        
        # Initialize feature extractor
        self.feature_extractor = CybersecurityFeatureExtractor(
            sequence_length=50,
            selected_features=30
        )
        
        # Prepare features for training
        X_train, X_val, X_test = self.feature_extractor.prepare_for_training(
            self.train_data, self.val_data, self.test_data
        )
        
        # Create sequences for LSTM
        logger.info("🔄 Creating sequences for LSTM...")
        train_sequences = self.feature_extractor.create_sequences(X_train)
        val_sequences = self.feature_extractor.create_sequences(X_val)
        test_sequences = self.feature_extractor.create_sequences(X_test)
        
        # Get labels (we'll use reconstruction error for anomaly detection)
        # But we need labels for evaluation
        y_train = self.train_data['is_attack'].values
        y_val = self.val_data['is_attack'].values
        y_test = self.test_data['is_attack'].values
        
        # Adjust labels to match sequence length
        y_train_seq = y_train[49:]  # Skip first 49 samples due to sequence creation
        y_val_seq = y_val[49:]
        y_test_seq = y_test[49:]
        
        logger.info(f"✅ Feature extraction complete:")
        logger.info(f"   📊 Feature dimension: {X_train.shape[1]}")
        logger.info(f"   🔢 Sequence length: {train_sequences.shape[1]}")
        logger.info(f"   📈 Training sequences: {train_sequences.shape}")
        logger.info(f"   📊 Validation sequences: {val_sequences.shape}")
        logger.info(f"   🧪 Test sequences: {test_sequences.shape}")
        
        return train_sequences, val_sequences, test_sequences, y_train_seq, y_val_seq, y_test_seq
    
    def create_data_loaders(self, train_sequences, val_sequences, test_sequences,
                           y_train, y_val, y_test, batch_size=32):
        """Create PyTorch data loaders"""
        logger.info(f"📦 Creating data loaders with batch size {batch_size}...")
        
        # Convert to tensors
        train_tensor = torch.FloatTensor(train_sequences)
        val_tensor = torch.FloatTensor(val_sequences)
        test_tensor = torch.FloatTensor(test_sequences)
        
        # Create datasets
        train_dataset = TensorDataset(train_tensor)
        val_dataset = TensorDataset(val_tensor)
        test_dataset = TensorDataset(test_tensor)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, drop_last=False)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, drop_last=False)
        
        logger.info(f"✅ Data loaders created:")
        logger.info(f"   📈 Training batches: {len(train_loader)}")
        logger.info(f"   📊 Validation batches: {len(val_loader)}")
        logger.info(f"   🧪 Test batches: {len(test_loader)}")
        
        # Store labels for evaluation
        self.y_train = y_train
        self.y_val = y_val
        self.y_test = y_test
        
        return train_loader, val_loader, test_loader
    
    def initialize_model(self, input_dim=30, sequence_length=50):
        """Initialize LSTM autoencoder model"""
        logger.info("🧠 Initializing LSTM Autoencoder...")
        
        self.model = LSTMAutoencoder(
            input_dim=input_dim,
            sequence_length=sequence_length,
            hidden_dim=128,
            num_layers=3,
            dropout=0.2,
            bidirectional=False
        )
        
        # Initialize trainer
        self.trainer = CybersecurityLSTMTrainer(
            model=self.model,
            learning_rate=0.001,
            weight_decay=1e-5
        )
        
        num_params = sum(p.numel() for p in self.model.parameters())
        logger.info(f"✅ Model initialized:")
        logger.info(f"   🏗️ Parameters: {num_params:,}")
        logger.info(f"   💻 Device: {self.trainer.device}")
        
    def train_model(self, train_loader, val_loader, epochs=50):
        """Train the LSTM autoencoder"""
        logger.info(f"🚀 Starting model training for {epochs} epochs...")
        
        start_time = time.time()
        
        # Train the model
        self.trainer.train(
            train_loader=train_loader,
            val_loader=val_loader,
            epochs=epochs,
            early_stopping_patience=15
        )
        
        training_time = time.time() - start_time
        logger.info(f"✅ Training completed in {training_time:.2f} seconds")
        
        # Save training results
        self.results['training'] = {
            'training_time': training_time,
            'best_val_loss': self.trainer.best_val_loss,
            'train_losses': self.trainer.train_losses,
            'val_losses': self.trainer.val_losses,
            'epochs_trained': len(self.trainer.train_losses)
        }
    
    def find_optimal_threshold(self, val_sequences, y_val):
        """Find optimal threshold for anomaly detection"""
        logger.info("🎯 Finding optimal anomaly detection threshold...")
        
        # Get reconstruction errors for validation set
        val_tensor = torch.FloatTensor(val_sequences)
        reconstruction_errors = []
        
        self.model.eval()
        with torch.no_grad():
            for i in range(0, len(val_tensor), 32):
                batch = val_tensor[i:i+32].to(self.trainer.device)
                errors = self.model.get_reconstruction_error(batch, reduction='mean')
                reconstruction_errors.extend(errors.cpu().numpy())
        
        reconstruction_errors = np.array(reconstruction_errors)
        
        # Try different thresholds
        thresholds = np.percentile(reconstruction_errors, np.arange(50, 99, 1))
        best_threshold = None
        best_f1 = 0
        
        for threshold in thresholds:
            predictions = (reconstruction_errors > threshold).astype(int)
            f1 = f1_score(y_val, predictions)
            
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold
        
        logger.info(f"✅ Optimal threshold found: {best_threshold:.6f} (F1: {best_f1:.4f})")
        
        self.optimal_threshold = best_threshold
        return best_threshold
    
    def evaluate_model(self, test_sequences, y_test):
        """Evaluate model performance on test set"""
        logger.info("📊 Evaluating model performance...")
        
        # Get reconstruction errors for test set
        test_tensor = torch.FloatTensor(test_sequences)
        reconstruction_errors = []
        anomaly_scores = []
        
        self.model.eval()
        with torch.no_grad():
            for i in range(0, len(test_tensor), 32):
                batch = test_tensor[i:i+32].to(self.trainer.device)
                errors = self.model.get_reconstruction_error(batch, reduction='mean')
                scores = self.model.get_anomaly_scores(batch)
                
                reconstruction_errors.extend(errors.cpu().numpy())
                anomaly_scores.extend(scores)
        
        reconstruction_errors = np.array(reconstruction_errors)
        anomaly_scores = np.array(anomaly_scores)
        
        # Make predictions using optimal threshold
        predictions = (reconstruction_errors > self.optimal_threshold).astype(int)
        
        # Calculate metrics
        precision = precision_score(y_test, predictions)
        recall = recall_score(y_test, predictions)
        f1 = f1_score(y_test, predictions)
        roc_auc = roc_auc_score(y_test, anomaly_scores)
        
        # Detailed classification report
        class_report = classification_report(y_test, predictions, target_names=['Normal', 'Attack'])
        conf_matrix = confusion_matrix(y_test, predictions)
        
        # Store results
        self.results['evaluation'] = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': roc_auc,
            'optimal_threshold': self.optimal_threshold,
            'classification_report': class_report,
            'confusion_matrix': conf_matrix.tolist(),
            'reconstruction_errors': reconstruction_errors.tolist(),
            'anomaly_scores': anomaly_scores.tolist(),
            'true_labels': y_test.tolist(),
            'predictions': predictions.tolist()
        }
        
        # Log results
        logger.info(f"🎯 Model Performance:")
        logger.info(f"   🎯 Precision: {precision:.4f} (Target: ≥0.85)")
        logger.info(f"   🔄 Recall: {recall:.4f} (Target: ≥0.90)")
        logger.info(f"   ⚖️ F1-Score: {f1:.4f} (Target: ≥0.88)")
        logger.info(f"   📈 ROC-AUC: {roc_auc:.4f} (Target: ≥0.92)")
        
        # Check if targets are met
        targets_met = {
            'precision': precision >= 0.85,
            'recall': recall >= 0.90,
            'f1_score': f1 >= 0.88,
            'roc_auc': roc_auc >= 0.92
        }
        
        all_targets_met = all(targets_met.values())
        
        if all_targets_met:
            logger.info("🎉 ALL PERFORMANCE TARGETS MET! ✅")
        else:
            logger.info("⚠️ Some performance targets not met:")
            for metric, met in targets_met.items():
                if not met:
                    logger.info(f"   ❌ {metric}")
        
        self.results['targets_met'] = targets_met
        self.results['all_targets_met'] = all_targets_met
        
        return precision, recall, f1, roc_auc
    
    def save_results(self):
        """Save all results and models"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save model
        model_path = self.model_save_path / f"cybersecurity_lstm_autoencoder_{timestamp}.pth"
        self.trainer.save_model(str(model_path))
        
        # Save feature extractor
        feature_config_path = self.model_save_path / f"feature_extractor_config_{timestamp}.pkl"
        self.feature_extractor.save_feature_config(str(feature_config_path))
        
        # Save results
        results_path = self.results_path / f"training_results_{timestamp}.json"
        
        # Prepare results for JSON serialization
        json_results = self.results.copy()
        if 'confusion_matrix' in json_results.get('evaluation', {}):
            json_results['evaluation']['confusion_matrix'] = json_results['evaluation']['confusion_matrix']
        
        with open(results_path, 'w') as f:
            json.dump(json_results, f, indent=2, default=str)
        
        logger.info(f"💾 Results saved:")
        logger.info(f"   🧠 Model: {model_path}")
        logger.info(f"   🔧 Features: {feature_config_path}")
        logger.info(f"   📊 Results: {results_path}")
        
        return model_path, feature_config_path, results_path
    
    def create_visualizations(self):
        """Create performance visualization plots"""
        logger.info("📈 Creating performance visualizations...")
        
        try:
            # Training curves
            plt.figure(figsize=(15, 5))
            
            # Loss curves
            plt.subplot(1, 3, 1)
            plt.plot(self.results['training']['train_losses'], label='Training Loss')
            plt.plot(self.results['training']['val_losses'], label='Validation Loss')
            plt.title('Training Progress')
            plt.xlabel('Epoch')
            plt.ylabel('MSE Loss')
            plt.legend()
            plt.grid(True)
            
            # ROC Curve
            plt.subplot(1, 3, 2)
            y_test = np.array(self.results['evaluation']['true_labels'])
            scores = np.array(self.results['evaluation']['anomaly_scores'])
            fpr, tpr, _ = roc_curve(y_test, scores)
            roc_auc = self.results['evaluation']['roc_auc']
            
            plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc:.3f})')
            plt.plot([0, 1], [0, 1], 'k--', label='Random')
            plt.title('ROC Curve')
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.legend()
            plt.grid(True)
            
            # Confusion Matrix
            plt.subplot(1, 3, 3)
            conf_matrix = np.array(self.results['evaluation']['confusion_matrix'])
            sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
                       xticklabels=['Normal', 'Attack'],
                       yticklabels=['Normal', 'Attack'])
            plt.title('Confusion Matrix')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_path = self.results_path / f"performance_plots_{timestamp}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"📈 Visualizations saved: {plot_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create visualizations: {e}")
    
    def run_complete_pipeline(self, epochs=50, batch_size=32):
        """Run the complete training pipeline"""
        logger.info("🚀 Starting complete cybersecurity training pipeline...")
        
        start_time = time.time()
        
        try:
            # Step 1: Load data
            self.load_data()
            
            # Step 2: Extract features
            train_seq, val_seq, test_seq, y_train, y_val, y_test = self.extract_features()
            
            # Step 3: Create data loaders
            train_loader, val_loader, test_loader = self.create_data_loaders(
                train_seq, val_seq, test_seq, y_train, y_val, y_test, batch_size
            )
            
            # Step 4: Initialize model
            self.initialize_model(input_dim=train_seq.shape[2], sequence_length=train_seq.shape[1])
            
            # Step 5: Train model
            self.train_model(train_loader, val_loader, epochs)
            
            # Step 6: Find optimal threshold
            self.find_optimal_threshold(val_seq, y_val)
            
            # Step 7: Evaluate model
            precision, recall, f1, roc_auc = self.evaluate_model(test_seq, y_test)
            
            # Step 8: Save results
            model_path, feature_path, results_path = self.save_results()
            
            # Step 9: Create visualizations
            self.create_visualizations()
            
            total_time = time.time() - start_time
            
            logger.info(f"🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info(f"⏱️ Total time: {total_time:.2f} seconds")
            logger.info(f"🎯 Final Performance:")
            logger.info(f"   • Precision: {precision:.4f}")
            logger.info(f"   • Recall: {recall:.4f}")
            logger.info(f"   • F1-Score: {f1:.4f}")
            logger.info(f"   • ROC-AUC: {roc_auc:.4f}")
            
            if self.results['all_targets_met']:
                logger.info("🏆 ALL PERFORMANCE TARGETS ACHIEVED! 🎯✅")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            raise

def main():
    """Run the complete training pipeline"""
    print("🛡️ Cybersecurity LSTM Autoencoder Training Pipeline")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = CybersecurityTrainingPipeline()
    
    # Run complete pipeline
    success = pipeline.run_complete_pipeline(epochs=30, batch_size=32)
    
    if success:
        print("\n🎉 PHASE 2 COMPLETE! ✅")
        print("🎯 Ready for Phase 3: Backend API Development")
    
    return pipeline

if __name__ == "__main__":
    pipeline = main() 