"""
Feature Extraction Module for Log Sequence Processing

This module handles tokenization, vocabulary building, and sequence
generation for the LSTM autoencoder. Will be implemented during
Phase 2: Feature Engineering & Model Prototype.
"""

import re
import json
import pickle
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional
import numpy as np


class LogTokenizer:
    """Tokenizer for log messages."""
    
    def __init__(self, vocab_size: int = 10000, min_freq: int = 2):
        """
        Initialize the tokenizer.
        
        Args:
            vocab_size: Maximum vocabulary size
            min_freq: Minimum frequency for a token to be included
        """
        self.vocab_size = vocab_size
        self.min_freq = min_freq
        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: Dict[int, str] = {}
        self.token_freq: Counter = Counter()
        
        # Special tokens
        self.PAD_TOKEN = "<PAD>"
        self.UNK_TOKEN = "<UNK>"
        self.START_TOKEN = "<START>"
        self.END_TOKEN = "<END>"
        
    def tokenize(self, message: str) -> List[str]:
        """
        Tokenize a log message.
        
        Args:
            message: Raw log message string
            
        Returns:
            List of tokens
            
        TODO: Phase 2 implementation
        - Clean and normalize message
        - Split on whitespace and punctuation
        - Handle special characters and numbers
        - Extract meaningful log components
        """
        print(f"TODO: Tokenize message: {message[:50]}...")
        
        # Placeholder tokenization
        tokens = re.split(r'\W+', message.lower())
        tokens = [token for token in tokens if token and len(token) > 1]
        return tokens
        
    def build_vocabulary(self, messages: List[str]):
        """
        Build vocabulary from a corpus of log messages.
        
        Args:
            messages: List of log message strings
            
        TODO: Phase 2 implementation
        - Tokenize all messages
        - Count token frequencies
        - Select top tokens by frequency
        - Create token-to-ID mappings
        """
        print(f"TODO: Build vocabulary from {len(messages)} messages")
        
        # Placeholder vocabulary
        special_tokens = [self.PAD_TOKEN, self.UNK_TOKEN, self.START_TOKEN, self.END_TOKEN]
        
        for i, token in enumerate(special_tokens):
            self.token_to_id[token] = i
            self.id_to_token[i] = token
            
        # TODO: Add real tokens from corpus
        
    def encode(self, tokens: List[str]) -> List[int]:
        """
        Convert tokens to token IDs.
        
        Args:
            tokens: List of token strings
            
        Returns:
            List of token IDs
        """
        ids = []
        for token in tokens:
            token_id = self.token_to_id.get(token, self.token_to_id[self.UNK_TOKEN])
            ids.append(token_id)
        return ids
        
    def decode(self, token_ids: List[int]) -> List[str]:
        """
        Convert token IDs back to tokens.
        
        Args:
            token_ids: List of token IDs
            
        Returns:
            List of token strings
        """
        tokens = []
        for token_id in token_ids:
            token = self.id_to_token.get(token_id, self.UNK_TOKEN)
            tokens.append(token)
        return tokens
        
    def save_vocabulary(self, path: str):
        """Save vocabulary to file."""
        vocab_data = {
            'token_to_id': self.token_to_id,
            'id_to_token': self.id_to_token,
            'token_freq': dict(self.token_freq),
            'vocab_size': self.vocab_size,
            'min_freq': self.min_freq
        }
        with open(path, 'w') as f:
            json.dump(vocab_data, f, indent=2)
            
    def load_vocabulary(self, path: str):
        """Load vocabulary from file."""
        with open(path, 'r') as f:
            vocab_data = json.load(f)
            
        self.token_to_id = vocab_data['token_to_id']
        self.id_to_token = {int(k): v for k, v in vocab_data['id_to_token'].items()}
        self.token_freq = Counter(vocab_data['token_freq'])
        self.vocab_size = vocab_data['vocab_size']
        self.min_freq = vocab_data['min_freq']


class SequenceBuilder:
    """Builder for log sequences using sliding window approach."""
    
    def __init__(self, window_size: int = 20, stride: int = 1):
        """
        Initialize the sequence builder.
        
        Args:
            window_size: Number of log lines per sequence
            stride: Step size for sliding window
        """
        self.window_size = window_size
        self.stride = stride
        
    def build_sequences(self, 
                       parsed_logs: List[Dict], 
                       tokenizer: LogTokenizer) -> List[List[int]]:
        """
        Build sequences from parsed log data.
        
        Args:
            parsed_logs: List of parsed log dictionaries
            tokenizer: Tokenizer for converting messages to tokens
            
        Returns:
            List of tokenized sequences
            
        TODO: Phase 2 implementation
        - Extract messages from parsed logs
        - Create sliding windows of log messages
        - Tokenize and encode each sequence
        - Pad/truncate to fixed length
        """
        print(f"TODO: Build sequences from {len(parsed_logs)} logs")
        print(f"TODO: Window size: {self.window_size}, Stride: {self.stride}")
        
        # Placeholder sequences
        sequences = []
        for i in range(0, len(parsed_logs) - self.window_size + 1, self.stride):
            # Mock sequence of token IDs
            sequence = [1, 2, 3, 4, 5] * (self.window_size // 5)
            sequence = sequence[:self.window_size]  # Truncate
            sequences.append(sequence)
            
        return sequences
        
    def pad_sequence(self, sequence: List[int], pad_token_id: int = 0) -> List[int]:
        """
        Pad or truncate sequence to fixed length.
        
        Args:
            sequence: Input sequence of token IDs
            pad_token_id: Token ID for padding
            
        Returns:
            Padded/truncated sequence
        """
        if len(sequence) >= self.window_size:
            return sequence[:self.window_size]
        else:
            padding = [pad_token_id] * (self.window_size - len(sequence))
            return sequence + padding


def extract_features(log_data: List[Dict], 
                    tokenizer: Optional[LogTokenizer] = None,
                    sequence_builder: Optional[SequenceBuilder] = None) -> Tuple[List[List[int]], LogTokenizer]:
    """
    Complete feature extraction pipeline.
    
    Args:
        log_data: List of parsed log dictionaries
        tokenizer: Pre-trained tokenizer (optional)
        sequence_builder: Sequence builder (optional)
        
    Returns:
        Tuple of (sequences, tokenizer)
        
    TODO: Phase 2 implementation
    - Extract messages from log data
    - Build/load tokenizer vocabulary
    - Create sequences using sliding window
    - Return processed sequences and tokenizer
    """
    print(f"TODO: Extract features from {len(log_data)} log entries")
    
    # Initialize components if not provided
    if tokenizer is None:
        tokenizer = LogTokenizer()
        
    if sequence_builder is None:
        sequence_builder = SequenceBuilder()
        
    # Extract messages for vocabulary building
    messages = [log['message'] for log in log_data if 'message' in log]
    
    # Build vocabulary if tokenizer is new
    if not tokenizer.token_to_id:
        tokenizer.build_vocabulary(messages)
        
    # Build sequences
    sequences = sequence_builder.build_sequences(log_data, tokenizer)
    
    return sequences, tokenizer


# Utility functions for data processing
def create_train_test_split(sequences: List[List[int]], 
                          labels: List[int], 
                          test_size: float = 0.2) -> Tuple[List, List, List, List]:
    """
    Split sequences into train/test sets.
    
    TODO: Phase 2 implementation with stratified split
    """
    print(f"TODO: Split {len(sequences)} sequences with test_size={test_size}")
    
    # Mock split for now
    split_idx = int(len(sequences) * (1 - test_size))
    
    X_train = sequences[:split_idx]
    X_test = sequences[split_idx:]
    y_train = labels[:split_idx] if labels else []
    y_test = labels[split_idx:] if labels else []
    
    return X_train, X_test, y_train, y_test 