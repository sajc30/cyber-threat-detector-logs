"""
LogHub Dataset Loader for Cybersecurity Threat Detection

This module handles loading and preprocessing of LogHub datasets which include:
- Linux system logs (authentication failures, ssh attacks)
- OpenSSH logs (break-in attempts, authentication events)
- Apache logs (web server attacks)
- Hadoop logs (distributed system events)
- Windows logs (system events)

Author: AI Cybersecurity System
"""

import os
import pandas as pd
import numpy as np
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogHubLoader:
    """
    Loads and preprocesses LogHub datasets for cybersecurity analysis
    """
    
    def __init__(self, data_root: str = "../../data/raw/loghub"):
        """
        Initialize the LogHub loader
        
        Args:
            data_root: Path to the loghub directory
        """
        self.data_root = Path(data_root)
        self.datasets = {}
        self.cybersecurity_relevant = [
            'Linux', 'OpenSSH', 'Apache', 'Windows', 'Hadoop'
        ]
        
    def list_available_datasets(self) -> List[str]:
        """List all available LogHub datasets"""
        datasets = []
        if self.data_root.exists():
            for item in self.data_root.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    datasets.append(item.name)
        return sorted(datasets)
    
    def load_dataset(self, dataset_name: str) -> Dict:
        """
        Load a specific LogHub dataset
        
        Args:
            dataset_name: Name of the dataset (e.g., 'Linux', 'OpenSSH')
            
        Returns:
            Dictionary containing raw logs, structured logs, and templates
        """
        dataset_path = self.data_root / dataset_name
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset {dataset_name} not found at {dataset_path}")
        
        result = {
            'name': dataset_name,
            'raw_logs': None,
            'structured_logs': None,
            'templates': None,
            'metadata': {}
        }
        
        # Load raw logs
        raw_log_files = list(dataset_path.glob("*.log"))
        if raw_log_files:
            raw_log_file = raw_log_files[0]  # Take first .log file
            logger.info(f"Loading raw logs from {raw_log_file}")
            result['raw_logs'] = self._load_raw_logs(raw_log_file)
            result['metadata']['raw_log_count'] = len(result['raw_logs'])
        
        # Load structured logs
        structured_files = list(dataset_path.glob("*_structured.csv"))
        if structured_files:
            structured_file = structured_files[0]
            logger.info(f"Loading structured logs from {structured_file}")
            result['structured_logs'] = pd.read_csv(structured_file)
            result['metadata']['structured_log_count'] = len(result['structured_logs'])
        
        # Load templates
        template_files = list(dataset_path.glob("*_templates.csv"))
        if template_files:
            template_file = template_files[0]
            logger.info(f"Loading templates from {template_file}")
            result['templates'] = pd.read_csv(template_file)
            result['metadata']['template_count'] = len(result['templates'])
        
        return result
    
    def _load_raw_logs(self, log_file: Path) -> List[str]:
        """Load raw log lines from file"""
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                logs = [line.strip() for line in f if line.strip()]
            return logs
        except Exception as e:
            logger.error(f"Error loading {log_file}: {e}")
            return []
    
    def extract_cybersecurity_features(self, dataset: Dict) -> pd.DataFrame:
        """
        Extract cybersecurity-relevant features from a dataset
        
        Args:
            dataset: Dataset dictionary from load_dataset()
            
        Returns:
            DataFrame with extracted features
        """
        if not dataset['raw_logs']:
            return pd.DataFrame()
        
        features = []
        
        for i, log_line in enumerate(dataset['raw_logs']):
            feature_dict = {
                'log_id': i,
                'raw_log': log_line,
                'dataset': dataset['name'],
                'length': len(log_line),
                'word_count': len(log_line.split()),
            }
            
            # Extract cybersecurity indicators
            feature_dict.update(self._extract_security_indicators(log_line))
            
            # Extract timestamp if possible
            timestamp = self._extract_timestamp(log_line)
            if timestamp:
                feature_dict['timestamp'] = timestamp
            
            features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    def _extract_security_indicators(self, log_line: str) -> Dict:
        """Extract cybersecurity-relevant indicators from a log line"""
        indicators = {
            'contains_authentication': 0,
            'contains_failure': 0,
            'contains_attack': 0,
            'contains_ssh': 0,
            'contains_login': 0,
            'contains_error': 0,
            'contains_unauthorized': 0,
            'contains_ip_address': 0,
            'suspicious_score': 0.0
        }
        
        log_lower = log_line.lower()
        
        # Authentication events
        auth_keywords = ['authentication', 'auth', 'login', 'logon', 'password']
        if any(keyword in log_lower for keyword in auth_keywords):
            indicators['contains_authentication'] = 1
            indicators['suspicious_score'] += 0.1
        
        # Failure indicators  
        failure_keywords = ['failure', 'failed', 'error', 'denied', 'reject']
        if any(keyword in log_lower for keyword in failure_keywords):
            indicators['contains_failure'] = 1
            indicators['suspicious_score'] += 0.3
        
        # Attack indicators
        attack_keywords = ['attack', 'intrusion', 'breach', 'compromise', 'malicious']
        if any(keyword in log_lower for keyword in attack_keywords):
            indicators['contains_attack'] = 1
            indicators['suspicious_score'] += 0.8
        
        # SSH-related
        if 'ssh' in log_lower:
            indicators['contains_ssh'] = 1
            indicators['suspicious_score'] += 0.1
        
        # Login events
        if 'login' in log_lower or 'logon' in log_lower:
            indicators['contains_login'] = 1
            indicators['suspicious_score'] += 0.1
        
        # Error events
        if 'error' in log_lower:
            indicators['contains_error'] = 1
            indicators['suspicious_score'] += 0.2
        
        # Unauthorized access
        unauthorized_keywords = ['unauthorized', 'invalid', 'unknown', 'illegal']
        if any(keyword in log_lower for keyword in unauthorized_keywords):
            indicators['contains_unauthorized'] = 1
            indicators['suspicious_score'] += 0.5
        
        # IP addresses (potential external access)
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        if re.search(ip_pattern, log_line):
            indicators['contains_ip_address'] = 1
            indicators['suspicious_score'] += 0.2
        
        # Special high-risk indicators
        high_risk_phrases = [
            'break-in attempt', 'possible attack', 'security violation',
            'brute force', 'repeated failed', 'multiple failures'
        ]
        for phrase in high_risk_phrases:
            if phrase in log_lower:
                indicators['suspicious_score'] += 1.0
                break
        
        # Cap the suspicious score
        indicators['suspicious_score'] = min(indicators['suspicious_score'], 1.0)
        
        return indicators
    
    def _extract_timestamp(self, log_line: str) -> Optional[str]:
        """Extract timestamp from log line if present"""
        # Common timestamp patterns
        patterns = [
            r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})',  # Dec 10 06:55:46
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',  # 2023-12-10 06:55:46
            r'(\[\w{3}\s+\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2}\s+\d{4}\])',  # [Sun Dec 04 04:47:44 2005]
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log_line)
            if match:
                return match.group(1)
        
        return None
    
    def load_cybersecurity_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all cybersecurity-relevant datasets and extract features
        
        Returns:
            Dictionary mapping dataset names to feature DataFrames
        """
        results = {}
        
        for dataset_name in self.cybersecurity_relevant:
            try:
                logger.info(f"Processing {dataset_name} dataset...")
                dataset = self.load_dataset(dataset_name)
                features_df = self.extract_cybersecurity_features(dataset)
                
                if not features_df.empty:
                    results[dataset_name] = features_df
                    logger.info(f"✅ {dataset_name}: {len(features_df)} log entries processed")
                    
                    # Log some statistics
                    suspicious_logs = features_df[features_df['suspicious_score'] > 0.5]
                    logger.info(f"   High suspicion logs: {len(suspicious_logs)}")
                    
                else:
                    logger.warning(f"⚠️ {dataset_name}: No features extracted")
                    
            except Exception as e:
                logger.error(f"❌ Error processing {dataset_name}: {e}")
        
        return results
    
    def create_training_dataset(self, datasets: Dict[str, pd.DataFrame], 
                              test_split: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Combine datasets and create train/test split for model training
        
        Args:
            datasets: Dictionary of processed datasets
            test_split: Fraction for test set
            
        Returns:
            Tuple of (train_df, test_df)
        """
        # Combine all datasets
        all_data = []
        for dataset_name, df in datasets.items():
            df_copy = df.copy()
            df_copy['source_dataset'] = dataset_name
            all_data.append(df_copy)
        
        if not all_data:
            return pd.DataFrame(), pd.DataFrame()
        
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Shuffle the data
        combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Split into train/test
        split_idx = int(len(combined_df) * (1 - test_split))
        train_df = combined_df[:split_idx]
        test_df = combined_df[split_idx:]
        
        logger.info(f"Created training dataset: {len(train_df)} training, {len(test_df)} test samples")
        
        return train_df, test_df
    
    def save_processed_data(self, datasets: Dict[str, pd.DataFrame], 
                           output_dir: str = "../../data/processed") -> None:
        """
        Save processed datasets to files
        
        Args:
            datasets: Processed datasets
            output_dir: Output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for dataset_name, df in datasets.items():
            output_file = output_path / f"{dataset_name.lower()}_features.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"Saved {dataset_name} features to {output_file}")
        
        # Save combined dataset
        if datasets:
            train_df, test_df = self.create_training_dataset(datasets)
            
            train_file = output_path / "train_features.csv"
            test_file = output_path / "test_features.csv"
            
            train_df.to_csv(train_file, index=False)
            test_df.to_csv(test_file, index=False)
            
            logger.info(f"Saved training data to {train_file}")
            logger.info(f"Saved test data to {test_file}")


def main():
    """Main function to demonstrate the LogHub loader"""
    print("🚀 LogHub Cybersecurity Data Loader")
    print("=" * 50)
    
    # Initialize loader
    loader = LogHubLoader()
    
    # List available datasets
    datasets = loader.list_available_datasets()
    print(f"Available datasets: {datasets}")
    
    # Load cybersecurity datasets
    processed_datasets = loader.load_cybersecurity_datasets()
    
    # Save processed data
    if processed_datasets:
        loader.save_processed_data(processed_datasets)
        print("\n✅ Data processing complete!")
        
        # Print summary statistics
        print("\n📊 Dataset Summary:")
        print("-" * 30)
        total_logs = 0
        total_suspicious = 0
        
        for name, df in processed_datasets.items():
            suspicious_count = len(df[df['suspicious_score'] > 0.5])
            total_logs += len(df)
            total_suspicious += suspicious_count
            
            print(f"{name:15}: {len(df):>6} logs, {suspicious_count:>4} suspicious")
        
        print("-" * 30)
        print(f"{'TOTAL':15}: {total_logs:>6} logs, {total_suspicious:>4} suspicious")
        print(f"Suspicious rate: {(total_suspicious/total_logs)*100:.1f}%")
    
    else:
        print("❌ No datasets could be processed")


if __name__ == "__main__":
    main() 