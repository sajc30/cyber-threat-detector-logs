"""
LSTM Autoencoder for Cybersecurity Threat Detection
Implements an encoder-decoder architecture for anomaly detection in system logs

Architecture:
- Encoder: Multi-layer LSTM with dropout
- Decoder: Multi-layer LSTM with attention mechanism
- Output: Reconstruction loss for anomaly scoring

Author: AI Cybersecurity System
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LSTMAutoencoder(nn.Module):
    """
    LSTM Autoencoder for cybersecurity anomaly detection
    """
    
    def __init__(self, 
                 input_dim: int = 30,
                 sequence_length: int = 50,
                 hidden_dim: int = 128,
                 num_layers: int = 3,
                 dropout: float = 0.2,
                 bidirectional: bool = False):
        super(LSTMAutoencoder, self).__init__()
        
        self.input_dim = input_dim
        self.sequence_length = sequence_length
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        self.bidirectional = bidirectional
        
        # Calculate effective hidden dimension
        self.effective_hidden_dim = hidden_dim * (2 if bidirectional else 1)
        
        # Encoder
        self.encoder_lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
            bidirectional=bidirectional
        )
        
        # Encoder output processing
        self.encoder_fc = nn.Sequential(
            nn.Linear(self.effective_hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2)
        )
        
        # Latent space representation
        self.latent_dim = hidden_dim // 2
        
        # Decoder initialization
        self.decoder_init = nn.Sequential(
            nn.Linear(self.latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, self.effective_hidden_dim)
        )
        
        # Decoder LSTM
        self.decoder_lstm = nn.LSTM(
            input_size=self.latent_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
            bidirectional=bidirectional
        )
        
        # Output layer
        self.output_layer = nn.Sequential(
            nn.Linear(self.effective_hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, input_dim)
        )
        
        # Attention mechanism for decoder
        self.attention = nn.MultiheadAttention(
            embed_dim=self.effective_hidden_dim,
            num_heads=8,
            dropout=dropout,
            batch_first=True
        )
        
        # Initialize weights
        self._init_weights()
        
    def _init_weights(self):
        """Initialize model weights"""
        for name, param in self.named_parameters():
            if 'weight_ih' in name:
                torch.nn.init.xavier_uniform_(param.data)
            elif 'weight_hh' in name:
                torch.nn.init.orthogonal_(param.data)
            elif 'bias' in name:
                param.data.fill_(0)
                
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Encode input sequence to latent representation
        
        Args:
            x: Input tensor (batch_size, sequence_length, input_dim)
            
        Returns:
            latent: Latent representation (batch_size, latent_dim)
            encoder_outputs: Full encoder outputs for attention
        """
        batch_size, seq_len, _ = x.shape
        
        # Encoder LSTM
        encoder_outputs, (h_n, c_n) = self.encoder_lstm(x)
        
        # Use last hidden state (or concatenated if bidirectional)
        if self.bidirectional:
            # Concatenate forward and backward final hidden states
            final_hidden = torch.cat((h_n[-2], h_n[-1]), dim=1)
        else:
            final_hidden = h_n[-1]
        
        # Project to latent space
        latent = self.encoder_fc(final_hidden)
        
        return latent, encoder_outputs
    
    def decode(self, latent: torch.Tensor, encoder_outputs: torch.Tensor) -> torch.Tensor:
        """
        Decode latent representation back to sequence
        
        Args:
            latent: Latent representation (batch_size, latent_dim)
            encoder_outputs: Encoder outputs for attention (batch_size, seq_len, hidden_dim)
            
        Returns:
            reconstruction: Reconstructed sequence (batch_size, sequence_length, input_dim)
        """
        batch_size = latent.shape[0]
        
        # Initialize decoder hidden state
        init_hidden = self.decoder_init(latent)
        init_hidden = init_hidden.unsqueeze(0).repeat(self.num_layers, 1, 1)
        
        if self.bidirectional:
            # Split for bidirectional
            init_hidden = init_hidden.view(self.num_layers * 2, batch_size, self.hidden_dim)
        
        # Initialize decoder cell state
        init_cell = torch.zeros_like(init_hidden)
        
        # Prepare decoder input (repeat latent for each time step)
        decoder_input = latent.unsqueeze(1).repeat(1, self.sequence_length, 1)
        
        # Decoder LSTM
        decoder_outputs, _ = self.decoder_lstm(decoder_input, (init_hidden, init_cell))
        
        # Apply attention mechanism
        attended_outputs, attention_weights = self.attention(
            decoder_outputs, encoder_outputs, encoder_outputs
        )
        
        # Generate final reconstruction
        reconstruction = self.output_layer(attended_outputs)
        
        return reconstruction
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through autoencoder
        
        Args:
            x: Input tensor (batch_size, sequence_length, input_dim)
            
        Returns:
            reconstruction: Reconstructed sequence
            latent: Latent representation
        """
        latent, encoder_outputs = self.encode(x)
        reconstruction = self.decode(latent, encoder_outputs)
        
        return reconstruction, latent
    
    def get_reconstruction_error(self, x: torch.Tensor, reduction: str = 'mean') -> torch.Tensor:
        """
        Calculate reconstruction error for anomaly detection
        
        Args:
            x: Input tensor
            reduction: How to reduce the error ('mean', 'sum', 'none')
            
        Returns:
            reconstruction_error: Error tensor
        """
        with torch.no_grad():
            reconstruction, _ = self.forward(x)
            
            # Calculate MSE loss
            mse_loss = F.mse_loss(reconstruction, x, reduction='none')
            
            if reduction == 'mean':
                return mse_loss.mean(dim=(1, 2))  # Mean over sequence and features
            elif reduction == 'sum':
                return mse_loss.sum(dim=(1, 2))   # Sum over sequence and features
            else:
                return mse_loss
    
    def predict_anomaly(self, x: torch.Tensor, threshold: float) -> torch.Tensor:
        """
        Predict anomalies based on reconstruction error
        
        Args:
            x: Input tensor
            threshold: Anomaly threshold
            
        Returns:
            anomaly_predictions: Binary predictions (1 = anomaly, 0 = normal)
        """
        reconstruction_error = self.get_reconstruction_error(x, reduction='mean')
        return (reconstruction_error > threshold).long()
    
    def get_anomaly_scores(self, x: torch.Tensor) -> np.ndarray:
        """
        Get continuous anomaly scores (0-1 normalized)
        
        Args:
            x: Input tensor
            
        Returns:
            scores: Normalized anomaly scores
        """
        reconstruction_error = self.get_reconstruction_error(x, reduction='mean')
        
        # Normalize to 0-1 range using sigmoid
        scores = torch.sigmoid(reconstruction_error / reconstruction_error.mean())
        
        return scores.cpu().numpy()

class CybersecurityLSTMTrainer:
    """
    Trainer class for LSTM Autoencoder
    """
    
    def __init__(self, 
                 model: LSTMAutoencoder,
                 learning_rate: float = 0.001,
                 weight_decay: float = 1e-5,
                 device: str = None):
        
        self.model = model
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # Optimizer
        self.optimizer = torch.optim.Adam(
            model.parameters(), 
            lr=learning_rate, 
            weight_decay=weight_decay
        )
        
        # Learning rate scheduler
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, 
            mode='min', 
            factor=0.5, 
            patience=10
        )
        
        # Loss function
        self.criterion = nn.MSELoss()
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.best_val_loss = float('inf')
        self.best_model_state = None
        
    def train_epoch(self, train_loader) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch_idx, batch_data in enumerate(train_loader):
            # Handle different batch formats
            if isinstance(batch_data, (list, tuple)):
                x = batch_data[0].to(self.device)
            else:
                x = batch_data.to(self.device)
            
            # Forward pass
            reconstruction, latent = self.model(x)
            
            # Calculate loss
            loss = self.criterion(reconstruction, x)
            
            # Add regularization
            l2_reg = sum(param.pow(2.0).sum() for param in self.model.parameters())
            loss += 1e-6 * l2_reg
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
            
            if batch_idx % 100 == 0:
                logger.info(f"Batch {batch_idx}/{len(train_loader)}, Loss: {loss.item():.6f}")
        
        return total_loss / num_batches
    
    def validate(self, val_loader) -> float:
        """Validate the model"""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch_data in val_loader:
                # Handle different batch formats
                if isinstance(batch_data, (list, tuple)):
                    x = batch_data[0].to(self.device)
                else:
                    x = batch_data.to(self.device)
                
                # Forward pass
                reconstruction, latent = self.model(x)
                
                # Calculate loss
                loss = self.criterion(reconstruction, x)
                
                total_loss += loss.item()
                num_batches += 1
        
        return total_loss / num_batches
    
    def train(self, train_loader, val_loader, epochs: int = 100, early_stopping_patience: int = 15):
        """
        Train the autoencoder
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of training epochs
            early_stopping_patience: Early stopping patience
        """
        logger.info(f"🚀 Starting training on {self.device}")
        logger.info(f"📊 Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        
        patience_counter = 0
        
        for epoch in range(epochs):
            # Train
            train_loss = self.train_epoch(train_loader)
            self.train_losses.append(train_loss)
            
            # Validate
            val_loss = self.validate(val_loader)
            self.val_losses.append(val_loss)
            
            # Learning rate scheduling
            self.scheduler.step(val_loss)
            
            # Early stopping and model saving
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.best_model_state = self.model.state_dict().copy()
                patience_counter = 0
                logger.info(f"✅ Epoch {epoch+1}: New best model! Val Loss: {val_loss:.6f}")
            else:
                patience_counter += 1
            
            # Log progress
            if (epoch + 1) % 5 == 0:
                current_lr = self.optimizer.param_groups[0]['lr']
                logger.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.6f}, "
                          f"Val Loss: {val_loss:.6f}, LR: {current_lr:.2e}")
            
            # Early stopping
            if patience_counter >= early_stopping_patience:
                logger.info(f"🛑 Early stopping at epoch {epoch+1}")
                break
        
        # Load best model
        if self.best_model_state is not None:
            self.model.load_state_dict(self.best_model_state)
            logger.info(f"🏆 Loaded best model with validation loss: {self.best_val_loss:.6f}")
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_val_loss': self.best_val_loss,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'model_config': {
                'input_dim': self.model.input_dim,
                'sequence_length': self.model.sequence_length,
                'hidden_dim': self.model.hidden_dim,
                'num_layers': self.model.num_layers,
                'dropout': self.model.dropout,
                'bidirectional': self.model.bidirectional
            }
        }, filepath)
        logger.info(f"💾 Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.best_val_loss = checkpoint['best_val_loss']
        self.train_losses = checkpoint['train_losses']
        self.val_losses = checkpoint['val_losses']
        logger.info(f"📂 Model loaded from {filepath}")

def main():
    """Test the LSTM autoencoder"""
    # Model configuration
    input_dim = 30
    sequence_length = 50
    batch_size = 32
    
    # Create model
    model = LSTMAutoencoder(
        input_dim=input_dim,
        sequence_length=sequence_length,
        hidden_dim=128,
        num_layers=3,
        dropout=0.2,
        bidirectional=False
    )
    
    print(f"🧠 LSTM Autoencoder created:")
    print(f"   📊 Input dimension: {input_dim}")
    print(f"   🔢 Sequence length: {sequence_length}")
    print(f"   🏗️ Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Test forward pass
    test_input = torch.randn(batch_size, sequence_length, input_dim)
    
    with torch.no_grad():
        reconstruction, latent = model(test_input)
        reconstruction_error = model.get_reconstruction_error(test_input)
        anomaly_scores = model.get_anomaly_scores(test_input)
    
    print(f"\n✅ Forward pass successful:")
    print(f"   📥 Input shape: {test_input.shape}")
    print(f"   📤 Reconstruction shape: {reconstruction.shape}")
    print(f"   🎯 Latent shape: {latent.shape}")
    print(f"   ⚠️ Reconstruction error shape: {reconstruction_error.shape}")
    print(f"   📊 Anomaly scores shape: {anomaly_scores.shape}")
    
    return model

if __name__ == "__main__":
    model = main() 