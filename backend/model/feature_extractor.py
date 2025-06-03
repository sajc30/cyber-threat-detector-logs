"""
Enhanced Feature Extractor for Cybersecurity Threat Detection
Processes unified dataset from LogHub, AIT-LDS, and KDD Cup 99

Features extracted:
- Statistical features from log content
- Temporal patterns
- Behavioral anomaly indicators
- Network traffic characteristics
- Text-based cybersecurity features

Author: AI Cybersecurity System
"""

import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif
from typing import Dict, List, Tuple, Optional
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CybersecurityFeatureExtractor:
    """
    Advanced feature extractor for cybersecurity threat detection
    """
    
    def __init__(self, sequence_length: int = 50, selected_features: int = 30):
        self.sequence_length = sequence_length
        self.selected_features = selected_features
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_selector = SelectKBest(f_classif, k=selected_features)
        self.feature_names = []
        self.is_fitted = False
        
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract comprehensive cybersecurity features from unified dataset
        """
        logger.info(f"🔧 Extracting features from {len(df)} records...")
        
        # Start with existing features
        features_df = df.copy()
        
        # 1. Text-based features
        features_df = self._add_text_features(features_df)
        
        # 2. Statistical features
        features_df = self._add_statistical_features(features_df)
        
        # 3. Behavioral features
        features_df = self._add_behavioral_features(features_df)
        
        # 4. Source-specific features
        features_df = self._add_source_specific_features(features_df)
        
        # 5. Engineered interaction features
        features_df = self._add_interaction_features(features_df)
        
        logger.info(f"✅ Feature extraction complete: {features_df.shape[1]} features")
        return features_df
    
    def _add_text_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add advanced text-based cybersecurity features"""
        logger.info("📝 Adding text-based features...")
        
        # Convert raw_message to string and handle NaN
        df['raw_message'] = df['raw_message'].fillna('').astype(str)
        
        # Character-level features
        df['char_diversity'] = df['raw_message'].apply(lambda x: len(set(x)) / max(len(x), 1))
        df['uppercase_ratio'] = df['raw_message'].apply(lambda x: sum(1 for c in x if c.isupper()) / max(len(x), 1))
        df['digit_ratio'] = df['raw_message'].apply(lambda x: sum(1 for c in x if c.isdigit()) / max(len(x), 1))
        df['special_char_ratio'] = df['raw_message'].apply(lambda x: sum(1 for c in x if not c.isalnum()) / max(len(x), 1))
        
        # Cybersecurity-specific patterns
        df['has_suspicious_keywords'] = df['raw_message'].str.lower().str.contains(
            r'exploit|malware|backdoor|trojan|virus|worm|rootkit|keylogger|botnet|phishing', 
            regex=True, na=False
        ).astype(int)
        
        df['has_network_indicators'] = df['raw_message'].str.contains(
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b|port|tcp|udp|http|ftp|ssh|ssl', 
            regex=True, na=False
        ).astype(int)
        
        df['has_file_operations'] = df['raw_message'].str.lower().str.contains(
            r'file|directory|folder|download|upload|execute|run|start|stop', 
            regex=True, na=False
        ).astype(int)
        
        df['has_security_events'] = df['raw_message'].str.lower().str.contains(
            r'alert|warning|critical|emergency|panic|attack|intrusion|breach', 
            regex=True, na=False
        ).astype(int)
        
        # Command injection patterns
        df['has_command_injection'] = df['raw_message'].str.contains(
            r';|\||&|`|\$\(|\${|<|>|\.\./|/etc/|/bin/|cmd\.exe|powershell', 
            regex=True, na=False
        ).astype(int)
        
        return df
    
    def _add_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add statistical features based on existing data"""
        logger.info("📊 Adding statistical features...")
        
        # Message length statistics
        df['msg_length_log'] = np.log1p(df['message_length'])
        df['msg_length_zscore'] = (df['message_length'] - df['message_length'].mean()) / df['message_length'].std()
        
        # Entropy-based features
        df['entropy_normalized'] = df['entropy'] / 8.0  # Normalize to [0,1]
        df['entropy_categorical'] = pd.cut(df['entropy'], bins=5, labels=False)
        
        # Attack score transformations
        df['attack_score_squared'] = df['attack_score'] ** 2
        df['attack_score_log'] = np.log1p(df['attack_score'])
        
        # Risk scoring
        df['risk_score'] = (df['attack_score'] * 0.4 + 
                           df['severity_score'] * 0.3 + 
                           df['entropy_normalized'] * 0.3)
        
        return df
    
    def _add_behavioral_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add behavioral anomaly detection features"""
        logger.info("🎭 Adding behavioral features...")
        
        # Frequency-based features by source
        source_counts = df['source'].value_counts()
        df['source_frequency'] = df['source'].map(source_counts)
        df['source_rarity'] = 1.0 / df['source_frequency']
        
        # Log type patterns
        logtype_counts = df['log_type'].value_counts()
        df['logtype_frequency'] = df['log_type'].map(logtype_counts)
        df['logtype_rarity'] = 1.0 / df['logtype_frequency']
        
        # Composite anomaly indicators
        df['anomaly_indicator'] = (
            df['has_error'] * 2 + 
            df['has_suspicious_keywords'] * 3 + 
            df['has_command_injection'] * 4 + 
            df['has_security_events'] * 2
        )
        
        # Binary feature combinations
        df['error_and_auth'] = df['has_error'] & df['has_auth']
        df['ip_and_error'] = df['has_ip'] & df['has_error']
        df['network_and_suspicious'] = df['has_network_indicators'] & df['has_suspicious_keywords']
        
        return df
    
    def _add_source_specific_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features specific to each data source"""
        logger.info("🎯 Adding source-specific features...")
        
        # One-hot encode sources
        for source in df['source'].unique():
            df[f'is_{source.lower()}'] = (df['source'] == source).astype(int)
        
        # One-hot encode log types
        for log_type in df['log_type'].unique():
            clean_name = log_type.replace(' ', '_').replace('-', '_')
            df[f'is_{clean_name}'] = (df['log_type'] == log_type).astype(int)
        
        # Source-specific risk factors
        df['kdd_network_risk'] = df['is_kdd'] * df['risk_score']
        df['ait_system_risk'] = df['is_ait'] * df['anomaly_indicator']
        df['loghub_auth_risk'] = df['is_loghub'] * df['has_auth'] * df['has_error']
        
        return df
    
    def _add_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add engineered interaction features"""
        logger.info("🔗 Adding interaction features...")
        
        # Risk multipliers
        df['risk_entropy_product'] = df['risk_score'] * df['entropy_normalized']
        df['attack_length_ratio'] = df['attack_score'] * np.log1p(df['message_length'])
        
        # Complex indicators
        df['high_risk_long_message'] = ((df['risk_score'] > 0.7) & 
                                       (df['message_length'] > df['message_length'].quantile(0.8))).astype(int)
        
        df['suspicious_network_activity'] = ((df['has_network_indicators'] == 1) & 
                                           (df['has_suspicious_keywords'] == 1) & 
                                           (df['attack_score'] > 0.5)).astype(int)
        
        # Threat level classification
        conditions = [
            df['attack_score'] < 0.2,
            (df['attack_score'] >= 0.2) & (df['attack_score'] < 0.5),
            (df['attack_score'] >= 0.5) & (df['attack_score'] < 0.8),
            df['attack_score'] >= 0.8
        ]
        threat_levels = [0, 1, 2, 3]  # Low, Medium, High, Critical
        df['threat_level'] = np.select(conditions, threat_levels)
        
        return df
    
    def prepare_for_training(self, train_df: pd.DataFrame, val_df: pd.DataFrame, 
                           test_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare features for LSTM training with proper scaling and selection
        """
        logger.info("🎛️ Preparing features for LSTM training...")
        
        # Extract features for all splits
        train_features = self.extract_features(train_df)
        val_features = self.extract_features(val_df)
        test_features = self.extract_features(test_df)
        
        # Select numerical features for model training
        numeric_features = self._select_numeric_features(train_features)
        
        # Get feature matrices
        X_train = train_features[numeric_features].values
        X_val = val_features[numeric_features].values
        X_test = test_features[numeric_features].values
        
        # Handle missing values
        X_train = np.nan_to_num(X_train, nan=0.0, posinf=1.0, neginf=-1.0)
        X_val = np.nan_to_num(X_val, nan=0.0, posinf=1.0, neginf=-1.0)
        X_test = np.nan_to_num(X_test, nan=0.0, posinf=1.0, neginf=-1.0)
        
        # Feature selection based on training data
        y_train = train_features['is_attack'].values
        if not self.is_fitted:
            self.feature_selector.fit(X_train, y_train)
            selected_indices = self.feature_selector.get_support(indices=True)
            self.feature_names = [numeric_features[i] for i in selected_indices]
            self.is_fitted = True
        
        # Apply feature selection
        X_train_selected = self.feature_selector.transform(X_train)
        X_val_selected = self.feature_selector.transform(X_val)
        X_test_selected = self.feature_selector.transform(X_test)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train_selected)
        X_val_scaled = self.scaler.transform(X_val_selected)
        X_test_scaled = self.scaler.transform(X_test_selected)
        
        logger.info(f"✅ Feature preparation complete:")
        logger.info(f"   📊 Selected features: {len(self.feature_names)}")
        logger.info(f"   📈 Training shape: {X_train_scaled.shape}")
        logger.info(f"   📊 Validation shape: {X_val_scaled.shape}")
        logger.info(f"   🧪 Test shape: {X_test_scaled.shape}")
        
        return X_train_scaled, X_val_scaled, X_test_scaled
    
    def _select_numeric_features(self, df: pd.DataFrame) -> List[str]:
        """Select numerical features suitable for LSTM training"""
        # Exclude non-numeric and identifier columns
        exclude_cols = ['raw_message', 'source', 'log_type', 'server']
        numeric_cols = []
        
        for col in df.columns:
            if col not in exclude_cols:
                if df[col].dtype in ['int64', 'float64', 'bool']:
                    numeric_cols.append(col)
                elif df[col].dtype == 'object':
                    # Try to convert to numeric
                    try:
                        pd.to_numeric(df[col])
                        numeric_cols.append(col)
                    except:
                        pass
        
        return numeric_cols
    
    def create_sequences(self, X: np.ndarray, window_size: int = None) -> np.ndarray:
        """
        Create sequences for LSTM input from feature matrix
        """
        if window_size is None:
            window_size = self.sequence_length
            
        if len(X) < window_size:
            # If we have fewer samples than window_size, pad with zeros
            padding = np.zeros((window_size - len(X), X.shape[1]))
            X_padded = np.vstack([padding, X])
            return X_padded.reshape(1, window_size, X.shape[1])
        
        sequences = []
        for i in range(len(X) - window_size + 1):
            sequences.append(X[i:i + window_size])
        
        return np.array(sequences)
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance scores"""
        if not self.is_fitted:
            raise ValueError("Feature extractor must be fitted first")
        
        scores = self.feature_selector.scores_[self.feature_selector.get_support()]
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': scores
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def save_feature_config(self, filepath: str):
        """Save feature extraction configuration"""
        import pickle
        config = {
            'scaler': self.scaler,
            'feature_selector': self.feature_selector,
            'feature_names': self.feature_names,
            'sequence_length': self.sequence_length,
            'selected_features': self.selected_features,
            'is_fitted': self.is_fitted
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(config, f)
        
        logger.info(f"💾 Feature configuration saved to {filepath}")
    
    def load_feature_config(self, filepath: str):
        """Load feature extraction configuration"""
        import pickle
        
        with open(filepath, 'rb') as f:
            config = pickle.load(f)
        
        self.scaler = config['scaler']
        self.feature_selector = config['feature_selector']
        self.feature_names = config['feature_names']
        self.sequence_length = config['sequence_length']
        self.selected_features = config['selected_features']
        self.is_fitted = config['is_fitted']
        
        logger.info(f"📂 Feature configuration loaded from {filepath}")

def main():
    """Test the feature extractor"""
    # Load test data
    data_path = Path("../../data/processed")
    train_df = pd.read_csv(data_path / "unified_train.csv")
    val_df = pd.read_csv(data_path / "unified_validation.csv")
    test_df = pd.read_csv(data_path / "unified_test.csv")
    
    print(f"📊 Loaded data: {len(train_df)} train, {len(val_df)} val, {len(test_df)} test")
    
    # Initialize feature extractor
    extractor = CybersecurityFeatureExtractor(sequence_length=50, selected_features=30)
    
    # Prepare features
    X_train, X_val, X_test = extractor.prepare_for_training(train_df, val_df, test_df)
    
    # Show feature importance
    importance_df = extractor.get_feature_importance()
    print("\n🏆 Top 10 Most Important Features:")
    print(importance_df.head(10))
    
    # Create sequences for LSTM
    print(f"\n🔄 Creating sequences for LSTM...")
    sequences_train = extractor.create_sequences(X_train)
    sequences_val = extractor.create_sequences(X_val)
    sequences_test = extractor.create_sequences(X_test)
    
    print(f"✅ Sequence shapes:")
    print(f"   Train: {sequences_train.shape}")
    print(f"   Validation: {sequences_val.shape}")
    print(f"   Test: {sequences_test.shape}")
    
    return extractor, (sequences_train, sequences_val, sequences_test)

if __name__ == "__main__":
    extractor, sequences = main() 