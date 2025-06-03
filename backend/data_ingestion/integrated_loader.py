"""
Optimized Integrated Dataset Loader for Cybersecurity Threat Detection
This module combines multiple cybersecurity datasets efficiently:
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
from tqdm import tqdm
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedIntegratedLoader:
    """
    Optimized loader for multiple cybersecurity datasets
    """
    
    def __init__(self, data_root: str = "../../data"):
        self.data_root = Path(data_root)
        self.raw_path = self.data_root / "raw"
        self.processed_path = self.data_root / "processed"
        self.datasets = {}
        
        # Optimization settings
        self.max_ait_records = 20000  # Limit AIT records for speed
        self.max_kdd_records = 25000  # Limit KDD records
        self.max_loghub_records = 10000  # Use existing LogHub data
        
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load and integrate all available datasets with optimizations"""
        logger.info("🚀 Loading integrated cybersecurity datasets (OPTIMIZED)...")
        
        # 1. Load LogHub data (already processed)
        logger.info("📁 Loading LogHub data...")
        loghub_data = self._load_loghub_processed()
        
        # 2. Load AIT dataset (optimized)
        logger.info("📁 Loading AIT dataset (optimized)...")
        ait_data = self._load_ait_dataset_optimized()
        
        # 3. Load KDD Cup 99 network data (optimized)
        logger.info("📁 Loading KDD dataset (optimized)...")
        kdd_data = self._load_kdd_dataset_optimized()
        
        # 4. Create unified feature space
        logger.info("🔧 Creating unified feature space...")
        unified_data = self._create_unified_features_optimized(loghub_data, ait_data, kdd_data)
        
        return unified_data
    
    def _load_loghub_processed(self) -> Optional[pd.DataFrame]:
        """Load already processed LogHub data"""
        try:
            train_file = self.processed_path / "train_features.csv"
            if train_file.exists():
                df = pd.read_csv(train_file, nrows=self.max_loghub_records)
                logger.info(f"✅ LogHub: {len(df)} records loaded")
                return df
            else:
                logger.warning("⚠️ LogHub processed data not found")
                return None
        except Exception as e:
            logger.error(f"❌ Error loading LogHub: {e}")
            return None
    
    def _load_ait_dataset_optimized(self) -> Optional[pd.DataFrame]:
        """Load and process AIT-LDS dataset with optimizations"""
        try:
            ait_path = self.raw_path / "data"
            if not ait_path.exists():
                logger.warning("⚠️ AIT dataset not found")
                return None
                
            records = []
            attack_count = 0
            
            # Cache all label files in memory first (OPTIMIZATION)
            logger.info("🗂️ Caching AIT label files...")
            label_cache = self._cache_ait_labels()
            
            # Process only first 2 mail servers for speed (OPTIMIZATION)
            server_dirs = list(ait_path.glob("mail.*"))[:2]  
            logger.info(f"📊 Processing {len(server_dirs)} servers...")
            
            for server_dir in tqdm(server_dirs, desc="Processing servers"):
                server_name = server_dir.name
                
                # Process authentication logs (SAMPLED)
                auth_log = server_dir / "auth.log"
                if auth_log.exists():
                    auth_records = self._process_log_file_sampled(
                        auth_log, server_name, "auth.log", "authentication", 
                        label_cache, max_records=5000
                    )
                    records.extend(auth_records)
                    attack_count += sum(1 for r in auth_records if r.get('is_attack', False))
                
                # Process Apache logs (SAMPLED)
                apache_dir = server_dir / "apache2"
                if apache_dir.exists():
                    for log_file in list(apache_dir.glob("*.log"))[:2]:  # Only first 2 files
                        apache_records = self._process_log_file_sampled(
                            log_file, server_name, f"apache2/{log_file.name}", 
                            "web_server", label_cache, max_records=3000
                        )
                        records.extend(apache_records)
                        attack_count += sum(1 for r in apache_records if r.get('is_attack', False))
                
                # Stop if we have enough records
                if len(records) >= self.max_ait_records:
                    break
            
            if records:
                df = pd.DataFrame(records[:self.max_ait_records])  # Ensure we don't exceed limit
                logger.info(f"✅ AIT Dataset: {len(df)} records, {attack_count} attacks ({attack_count/len(df)*100:.1f}%)")
                return df
            else:
                logger.warning("⚠️ No AIT records processed")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error loading AIT dataset: {e}")
            return None
    
    def _cache_ait_labels(self) -> Dict:
        """Cache all AIT label files in memory for fast lookup"""
        label_cache = {}
        labels_path = self.raw_path / "labels"
        
        if not labels_path.exists():
            return label_cache
        
        try:
            for server_dir in labels_path.glob("mail.*"):
                server_name = server_dir.name
                label_cache[server_name] = {}
                
                # Cache auth.log labels
                auth_labels = server_dir / "auth.log"
                if auth_labels.exists():
                    label_cache[server_name]["auth.log"] = self._load_label_file(auth_labels)
                
                # Cache apache labels
                apache2_dir = server_dir / "apache2"
                if apache2_dir.exists():
                    for label_file in apache2_dir.glob("*.log"):
                        key = f"apache2/{label_file.name}"
                        label_cache[server_name][key] = self._load_label_file(label_file)
        
        except Exception as e:
            logger.warning(f"⚠️ Error caching labels: {e}")
        
        return label_cache
    
    def _load_label_file(self, label_file: Path) -> set:
        """Load a label file and return set of attack line numbers"""
        attack_lines = set()
        try:
            with open(label_file, 'r') as f:
                for line in f:
                    try:
                        label_data = json.loads(line.strip())
                        attack_lines.add(label_data.get('line'))
                    except:
                        continue
        except:
            pass
        return attack_lines
    
    def _process_log_file_sampled(self, log_file: Path, server_name: str, 
                                 log_key: str, log_type: str, label_cache: Dict, 
                                 max_records: int = 5000) -> List[Dict]:
        """Process a log file with sampling for speed"""
        records = []
        attack_lines = label_cache.get(server_name, {}).get(log_key, set())
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Sample lines for processing (OPTIMIZATION)
            if len(lines) > max_records:
                # Ensure we get some attack samples
                attack_indices = [i for i, _ in enumerate(lines, 1) if i in attack_lines]
                normal_indices = [i for i in range(len(lines)) if (i + 1) not in attack_lines]
                
                # Sample both attack and normal lines
                sample_attack = random.sample(attack_indices, min(len(attack_indices), max_records // 4))
                sample_normal = random.sample(normal_indices, max_records - len(sample_attack))
                
                selected_indices = sorted(sample_attack + sample_normal)
            else:
                selected_indices = list(range(len(lines)))
            
            for idx in selected_indices:
                line_no = idx + 1
                line = lines[idx].strip()
                
                if line:
                    is_attack = line_no in attack_lines
                    features = self._extract_ait_features_fast(line, log_type)
                    features.update({
                        'source': 'AIT',
                        'server': server_name,
                        'log_type': log_type,
                        'is_attack': is_attack,
                        'attack_score': 0.9 if is_attack else 0.1
                    })
                    records.append(features)
                    
        except Exception as e:
            logger.warning(f"⚠️ Error processing {log_file}: {e}")
        
        return records
    
    def _extract_ait_features_fast(self, log_line: str, log_type: str) -> Dict:
        """Fast feature extraction from AIT log lines"""
        # Pre-compute common checks
        line_lower = log_line.lower()
        
        features = {
            'raw_message': log_line[:200],  # Shorter for speed
            'message_length': len(log_line),
            'has_ip': 1 if '.' in log_line and any(c.isdigit() for c in log_line) else 0,
            'has_error': 1 if any(word in line_lower for word in ['error', 'fail', 'deny', 'invalid']) else 0,
            'has_auth': 1 if any(word in line_lower for word in ['auth', 'login', 'password', 'user']) else 0,
            'entropy': min(len(set(log_line)) / len(log_line) * 8, 8.0) if log_line else 0.0,  # Fast entropy approximation
        }
        
        if log_type == "authentication":
            features.update({
                'has_session': 1 if 'session' in line_lower else 0,
                'has_pam': 1 if 'pam' in line_lower else 0,
                'has_cron': 1 if 'cron' in line_lower else 0,
            })
        elif log_type == "web_server":
            features.update({
                'has_post': 1 if 'POST' in log_line else 0,
                'has_get': 1 if 'GET' in log_line else 0,
                'has_404': 1 if '404' in log_line else 0,
                'has_php': 1 if 'php' in line_lower else 0,
            })
        
        return features
    
    def _load_kdd_dataset_optimized(self) -> Optional[pd.DataFrame]:
        """Load and process KDD Cup 99 dataset with optimizations"""
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
            
            # Read limited subset for speed (OPTIMIZATION)
            df = pd.read_csv(kdd_file, names=feature_names, nrows=self.max_kdd_records)
            
            # Process attack labels
            df['is_attack'] = df['attack_type'] != 'normal.'
            df['attack_score'] = np.where(df['is_attack'], 0.85, 0.15)
            df['source'] = 'KDD'
            df['log_type'] = 'network_traffic'
            
            # Map attack types to severity (vectorized for speed)
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
    
    def _create_unified_features_optimized(self, loghub_df: Optional[pd.DataFrame], 
                                         ait_df: Optional[pd.DataFrame], 
                                         kdd_df: Optional[pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Create unified feature space with optimizations"""
        
        unified_records = []
        
        # Process LogHub data
        if loghub_df is not None:
            logger.info(f"🔧 Processing {len(loghub_df)} LogHub records...")
            for _, row in tqdm(loghub_df.iterrows(), total=len(loghub_df), desc="LogHub"):
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
                    'raw_message': str(row.get('raw_log', ''))[:200]
                })
        
        # Process AIT data
        if ait_df is not None:
            logger.info(f"🔧 Processing {len(ait_df)} AIT records...")
            for _, row in tqdm(ait_df.iterrows(), total=len(ait_df), desc="AIT"):
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
                    'raw_message': str(row.get('raw_message', ''))[:200]
                })
        
        # Process KDD data (vectorized for speed)
        if kdd_df is not None:
            logger.info(f"🔧 Processing {len(kdd_df)} KDD records...")
            
            # Vectorized processing for speed
            kdd_unified = pd.DataFrame({
                'source': 'KDD',
                'log_type': 'network_traffic',
                'is_attack': kdd_df['is_attack'],
                'attack_score': kdd_df['attack_score'],
                'message_length': kdd_df['attack_type'].str.len(),
                'has_ip': 1,
                'has_error': (kdd_df['wrong_fragment'] > 0).astype(int),
                'has_auth': (kdd_df['logged_in'] > 0).astype(int),
                'entropy': np.clip(kdd_df['duration'] / 1000.0, 0, 1),
                'severity_score': kdd_df['severity_score'],
                'raw_message': kdd_df['protocol_type'].astype(str) + " " + kdd_df['service'].astype(str)
            })
            
            unified_records.extend(kdd_unified.to_dict('records'))
        
        # Create final unified dataset
        if unified_records:
            logger.info("🔧 Creating final unified dataset...")
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
🎉 OPTIMIZED UNIFIED CYBERSECURITY DATASET CREATED!
📊 Total Records: {len(unified_df):,}
🚨 Attack Records: {total_attacks:,} ({attack_rate:.1f}%)
📈 Training Set: {len(train_df):,} records
📊 Validation Set: {len(val_df):,} records
🧪 Test Set: {len(test_df):,} records

📋 Data Sources:
- LogHub: System logs (Linux, SSH, Apache, Windows)
- AIT-LDS: Expert-labeled attack scenarios (SAMPLED)
- KDD Cup 99: Network intrusion patterns (SAMPLED)

⚡ OPTIMIZED: Fast processing with representative sampling
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
    
    def save_unified_dataset(self, datasets: Dict[str, pd.DataFrame], 
                           output_dir: str = "../../data/processed") -> None:
        """Save the unified dataset"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("💾 Saving unified datasets...")
            for split_name, df in datasets.items():
                if df is not None and len(df) > 0:
                    output_file = output_path / f"unified_{split_name}.csv"
                    df.to_csv(output_file, index=False)
                    logger.info(f"✅ Saved {split_name}: {output_file} ({len(df)} records)")
            
            # Save dataset metadata
            metadata = {
                'created_at': datetime.now().isoformat(),
                'total_records': len(datasets.get('full', [])),
                'attack_rate': float(datasets.get('full', pd.DataFrame()).get('is_attack', pd.Series()).mean() or 0),
                'sources': ['LogHub', 'AIT-LDS (sampled)', 'KDD Cup 99 (sampled)'],
                'splits': {name: len(df) for name, df in datasets.items() if df is not None},
                'optimization': 'Enabled - Representative sampling for speed'
            }
            
            with open(output_path / "unified_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info("✅ Optimized unified dataset saved successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error saving unified dataset: {e}")

def main():
    """Run the optimized integrated data loader"""
    print("🚀 Starting Optimized Cybersecurity Data Integration...")
    print("⚡ Optimizations: Sampling, caching, progress indicators")
    print("⏱️ Expected time: 3-5 minutes\n")
    
    loader = OptimizedIntegratedLoader()
    datasets = loader.load_all_datasets()
    
    if datasets:
        loader.save_unified_dataset(datasets)
        print("\n🎉 PHASE 1 COMPLETE! ✅")
        print("🎯 Ready for Phase 2: Feature Engineering & Model Training")
        print("📁 Datasets saved in: data/processed/")
        return True
    else:
        print("❌ Failed to create unified dataset")
        return False

if __name__ == "__main__":
    success = main() 