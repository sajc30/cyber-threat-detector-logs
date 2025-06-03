"""
Integrated Dataset Loader for Cybersecurity Threat Detection
This module combines multiple cybersecurity datasets:
1. LogHub (system logs)
2. AIT-LDS (expert-labeled attack scenarios) 
3. KDD Cup 99 (network intrusion detection)

Author: AI Cybersecurity System
"""

import os
import pandas as pd
import numpy as np
import json
import gzip
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedDatasetLoader:
    """
    Loads and integrates multiple cybersecurity datasets
    """
    
    def __init__(self, data_root: str = "../../data"):
        self.data_root = Path(data_root)
        self.raw_path = self.data_root / "raw"
        self.processed_path = self.data_root / "processed"
        self.datasets = {}
        
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load and integrate all available datasets"""
        logger.info("🔄 Loading integrated cybersecurity datasets...")
        
        # 1. Load LogHub data (already processed)
        loghub_data = self._load_loghub_processed()
        
        # 2. Load AIT dataset
        ait_data = self._load_ait_dataset()
        
        # 3. Load KDD Cup 99 network data
        kdd_data = self._load_kdd_dataset()
        
        # 4. Create unified feature space
        unified_data = self._create_unified_features(loghub_data, ait_data, kdd_data)
        
        return unified_data
    
    def _load_loghub_processed(self) -> Optional[pd.DataFrame]:
        """Load already processed LogHub data"""
        try:
            train_file = self.processed_path / "train_features.csv"
            if train_file.exists():
                df = pd.read_csv(train_file)
                logger.info(f"✅ LogHub: {len(df)} records loaded")
                return df
            else:
                logger.warning("⚠️ LogHub processed data not found")
                return None
        except Exception as e:
            logger.error(f"❌ Error loading LogHub: {e}")
            return None
    
    def _load_ait_dataset(self) -> Optional[pd.DataFrame]:
        """Load and process AIT-LDS dataset"""
        try:
            ait_path = self.raw_path / "data"
            if not ait_path.exists():
                logger.warning("⚠️ AIT dataset not found")
                return None
                
            records = []
            attack_count = 0
            
            # Process each mail server
            for server_dir in ait_path.glob("mail.*"):
                server_name = server_dir.name
                
                # Load authentication logs
                auth_log = server_dir / "auth.log"
                if auth_log.exists():
                    with open(auth_log, 'r') as f:
                        for line_no, line in enumerate(f, 1):
                            line = line.strip()
                            if line:
                                is_attack = self._check_ait_attack_label(server_name, "auth.log", line_no)
                                features = self._extract_ait_features(line, "auth")
                                features.update({
                                    'source': 'AIT',
                                    'server': server_name,
                                    'log_type': 'authentication',
                                    'is_attack': is_attack,
                                    'attack_score': 0.9 if is_attack else 0.1
                                })
                                records.append(features)
                                if is_attack:
                                    attack_count += 1
                
                # Load Apache logs
                apache_dir = server_dir / "apache2"
                if apache_dir.exists():
                    for log_file in apache_dir.glob("*.log"):
                        with open(log_file, 'r') as f:
                            for line_no, line in enumerate(f, 1):
                                line = line.strip()
                                if line and len(records) < 50000:  # Limit for memory
                                    is_attack = self._check_ait_attack_label(server_name, f"apache2/{log_file.name}", line_no)
                                    features = self._extract_ait_features(line, "apache")
                                    features.update({
                                        'source': 'AIT',
                                        'server': server_name,
                                        'log_type': 'web_server',
                                        'is_attack': is_attack,
                                        'attack_score': 0.8 if is_attack else 0.2
                                    })
                                    records.append(features)
                                    if is_attack:
                                        attack_count += 1
            
            if records:
                df = pd.DataFrame(records)
                logger.info(f"✅ AIT Dataset: {len(df)} records, {attack_count} attacks ({attack_count/len(df)*100:.1f}%)")
                return df
            else:
                logger.warning("⚠️ No AIT records processed")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error loading AIT dataset: {e}")
            return None
    
    def _check_ait_attack_label(self, server: str, log_file: str, line_no: int) -> bool:
        """Check if a log line is labeled as an attack in AIT dataset"""
        try:
            labels_path = self.raw_path / "labels" / server / log_file
            if labels_path.exists():
                with open(labels_path, 'r') as f:
                    for line in f:
                        try:
                            label_data = json.loads(line.strip())
                            if label_data.get('line') == line_no:
                                return True
                        except:
                            continue
            return False
        except:
            return False
    
    def _extract_ait_features(self, log_line: str, log_type: str) -> Dict:
        """Extract features from AIT log lines"""
        features = {
            'raw_message': log_line[:500],  # Truncate long messages
            'message_length': len(log_line),
            'has_ip': 1 if any(c.isdigit() and '.' in log_line for c in [log_line]) else 0,
            'has_error': 1 if any(word in log_line.lower() for word in ['error', 'fail', 'deny', 'invalid']) else 0,
            'has_auth': 1 if any(word in log_line.lower() for word in ['auth', 'login', 'password', 'user']) else 0,
            'entropy': self._calculate_entropy(log_line),
        }
        
        if log_type == "auth":
            features.update({
                'has_session': 1 if 'session' in log_line.lower() else 0,
                'has_pam': 1 if 'pam' in log_line.lower() else 0,
                'has_cron': 1 if 'cron' in log_line.lower() else 0,
            })
        elif log_type == "apache":
            features.update({
                'has_post': 1 if 'POST' in log_line else 0,
                'has_get': 1 if 'GET' in log_line else 0,
                'has_404': 1 if '404' in log_line else 0,
                'has_php': 1 if 'php' in log_line.lower() else 0,
            })
        
        return features
    
    def _load_kdd_dataset(self) -> Optional[pd.DataFrame]:
        """Load and process KDD Cup 99 dataset"""
        try:
            kdd_file = self.raw_path / "network_intrusion" / "kddcup.data_10_percent"
            if not kdd_file.exists():
                logger.warning("⚠️ KDD dataset not found")
                return None
            
            # KDD feature names
            feature_names = [
                'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
                'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
                'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
                'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
                'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
                'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
                'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
                'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
                'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
                'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'attack_type'
            ]
            
            # Read subset for memory efficiency
            df = pd.read_csv(kdd_file, names=feature_names, nrows=50000)
            
            # Process attack labels
            df['is_attack'] = df['attack_type'] != 'normal.'
            df['attack_score'] = np.where(df['is_attack'], 0.85, 0.15)
            df['source'] = 'KDD'
            df['log_type'] = 'network_traffic'
            
            # Map attack types to severity
            attack_severity = {
                'normal.': 0.0,
                'smurf.': 0.7, 'neptune.': 0.8, 'back.': 0.6,  # DoS attacks
                'satan.': 0.5, 'ipsweep.': 0.4, 'portsweep.': 0.4, 'nmap.': 0.5,  # Probe
                'warezclient.': 0.6, 'imap.': 0.7, 'warezmaster.': 0.8, 'ftp_write.': 0.7,  # R2L
                'buffer_overflow.': 0.9, 'loadmodule.': 0.8, 'perl.': 0.7, 'rootkit.': 0.9  # U2R
            }
            
            df['severity_score'] = df['attack_type'].map(attack_severity).fillna(0.5)
            
            attack_count = df['is_attack'].sum()
            logger.info(f"✅ KDD Dataset: {len(df)} records, {attack_count} attacks ({attack_count/len(df)*100:.1f}%)")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error loading KDD dataset: {e}")
            return None
    
    def _create_unified_features(self, loghub_df: Optional[pd.DataFrame], 
                                ait_df: Optional[pd.DataFrame], 
                                kdd_df: Optional[pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Create unified feature space across all datasets"""
        
        unified_records = []
        
        # Process LogHub data
        if loghub_df is not None:
            for _, row in loghub_df.iterrows():
                unified_records.append({
                    'source': 'LogHub',
                    'log_type': row.get('log_type', 'system'),
                    'is_attack': row.get('is_suspicious', 0) > 0.5,
                    'attack_score': row.get('suspicious_score', 0.0),
                    'message_length': row.get('message_length', 0),
                    'has_ip': row.get('has_ip_address', 0),
                    'has_error': row.get('has_error_keywords', 0),
                    'has_auth': row.get('has_authentication', 0),
                    'entropy': row.get('entropy', 0.0),
                    'severity_score': row.get('suspicious_score', 0.0),
                    'raw_message': str(row.get('raw_log', ''))[:500]
                })
        
        # Process AIT data
        if ait_df is not None:
            for _, row in ait_df.iterrows():
                unified_records.append({
                    'source': 'AIT',
                    'log_type': row.get('log_type', 'system'),
                    'is_attack': row.get('is_attack', False),
                    'attack_score': row.get('attack_score', 0.0),
                    'message_length': row.get('message_length', 0),
                    'has_ip': row.get('has_ip', 0),
                    'has_error': row.get('has_error', 0),
                    'has_auth': row.get('has_auth', 0),
                    'entropy': row.get('entropy', 0.0),
                    'severity_score': row.get('attack_score', 0.0),
                    'raw_message': str(row.get('raw_message', ''))[:500]
                })
        
        # Process KDD data (sample to balance dataset size)
        if kdd_df is not None:
            # Sample KDD data to balance with other datasets
            kdd_sample = kdd_df.sample(n=min(len(kdd_df), 10000), random_state=42)
            for _, row in kdd_sample.iterrows():
                unified_records.append({
                    'source': 'KDD',
                    'log_type': 'network_traffic',
                    'is_attack': row.get('is_attack', False),
                    'attack_score': row.get('attack_score', 0.0),
                    'message_length': len(str(row.get('attack_type', ''))),
                    'has_ip': 1,  # Network data always has IP info
                    'has_error': 1 if row.get('wrong_fragment', 0) > 0 else 0,
                    'has_auth': 1 if row.get('logged_in', 0) > 0 else 0,
                    'entropy': min(row.get('duration', 0) / 1000.0, 1.0),  # Normalize duration as entropy proxy
                    'severity_score': row.get('severity_score', 0.0),
                    'raw_message': f"Network: {row.get('protocol_type', '')} {row.get('service', '')} {row.get('flag', '')}"
                })
        
        # Create final unified dataset
        if unified_records:
            unified_df = pd.DataFrame(unified_records)
            
            # Split into train/validation/test
            train_size = int(0.7 * len(unified_df))
            val_size = int(0.15 * len(unified_df))
            
            # Shuffle data
            unified_df = unified_df.sample(frac=1, random_state=42).reset_index(drop=True)
            
            train_df = unified_df[:train_size]
            val_df = unified_df[train_size:train_size + val_size]
            test_df = unified_df[train_size + val_size:]
            
            # Calculate final statistics
            total_attacks = unified_df['is_attack'].sum()
            attack_rate = total_attacks / len(unified_df) * 100
            
            logger.info(f"""
🎉 UNIFIED CYBERSECURITY DATASET CREATED!
📊 Total Records: {len(unified_df):,}
🚨 Attack Records: {total_attacks:,} ({attack_rate:.1f}%)
📈 Training Set: {len(train_df):,} records
📊 Validation Set: {len(val_df):,} records
🧪 Test Set: {len(test_df):,} records

📋 Data Sources:
- LogHub: System logs (Linux, SSH, Apache, Windows)
- AIT-LDS: Expert-labeled attack scenarios
- KDD Cup 99: Network intrusion patterns

🎯 READY FOR PHASE 2: FEATURE ENGINEERING & MODEL TRAINING!
            """)
            
            return {
                'train': train_df,
                'validation': val_df,
                'test': test_df,
                'full': unified_df
            }
        else:
            logger.error("❌ No data could be loaded from any source")
            return {}
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        length = len(text)
        entropy = 0.0
        for count in char_counts.values():
            p = count / length
            if p > 0:
                entropy -= p * np.log2(p)
        
        return min(entropy, 8.0)  # Cap at 8 bits
    
    def save_unified_dataset(self, datasets: Dict[str, pd.DataFrame], 
                           output_dir: str = "../../data/processed") -> None:
        """Save the unified dataset"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            for split_name, df in datasets.items():
                if df is not None and len(df) > 0:
                    output_file = output_path / f"unified_{split_name}.csv"
                    df.to_csv(output_file, index=False)
                    logger.info(f"💾 Saved {split_name}: {output_file}")
            
            # Save dataset metadata
            metadata = {
                'created_at': datetime.now().isoformat(),
                'total_records': len(datasets.get('full', [])),
                'attack_rate': float(datasets.get('full', pd.DataFrame()).get('is_attack', pd.Series()).mean() or 0),
                'sources': ['LogHub', 'AIT-LDS', 'KDD Cup 99'],
                'splits': {name: len(df) for name, df in datasets.items() if df is not None}
            }
            
            with open(output_path / "unified_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info("✅ Unified dataset saved successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error saving unified dataset: {e}")

def main():
    """Run the integrated data loader"""
    loader = IntegratedDatasetLoader()
    datasets = loader.load_all_datasets()
    
    if datasets:
        loader.save_unified_dataset(datasets)
        print("\n🎉 Phase 1 Complete! Ready for Phase 2: Feature Engineering & Model Training")
    else:
        print("❌ Failed to create unified dataset")

if __name__ == "__main__":
    main() 