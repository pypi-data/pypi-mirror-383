"""RNA-MSM Adapter for Multiple Sequence Alignment Transformer"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Union, Optional, List

import numpy as np
import torch
from tqdm import tqdm

from .config import RnaMSMConfig
from .model import MSATransformer
from .dataset import RNADataset, RandomCropDataset
from .msm import Alphabet
from .utils.tokenization import Vocab
from ...core.base import BaseModel
from ...core.exceptions import ModelLoadError, PredictionError, InvalidSequenceError


class RnaMSMAdapter(BaseModel):
    """RNA-MSM adapter for MSA-based RNA sequence analysis"""

    def __init__(self, config: Union[RnaMSMConfig, Dict[str, Any]], device: str = "cpu"):
        super().__init__(config, device)
        
        if isinstance(config, RnaMSMConfig):
            self.model_type = config.model_type
        else:
            self.model_type = config.get('model_type', 'rna_msm')
            
        self.alphabet = None
        self.vocab = None
        self._is_loaded = False
        self._model_instance = None
        
        # Extract config parameters
        self._extract_config_params()

    def _extract_config_params(self):
        """Extract configuration parameters"""
        if isinstance(self.config, RnaMSMConfig):
            self.embed_dim = self.config.embed_dim
            self.num_attention_heads = self.config.num_attention_heads
            self.num_layers = self.config.num_layers
            self.embed_positions_msa = self.config.embed_positions_msa
            self.dropout = self.config.dropout
            self.attention_dropout = self.config.attention_dropout
            self.activation_dropout = self.config.activation_dropout
            self.architecture = self.config.architecture
            self.max_seqlen = self.config.max_seqlen
            self.max_tokens = self.config.max_tokens
            self.max_seqs_per_msa = self.config.max_seqs_per_msa
            self.sample_method = self.config.sample_method
            self.extract_layer = self.config.extract_layer
            self.extract_attention = self.config.extract_attention
            self.extract_embeddings = self.config.extract_embeddings
        else:
            # Handle dict config
            self.embed_dim = self.config.get('embed_dim', 768)
            self.num_attention_heads = self.config.get('num_attention_heads', 12)
            self.num_layers = self.config.get('num_layers', 10)
            self.embed_positions_msa = self.config.get('embed_positions_msa', True)
            self.dropout = self.config.get('dropout', 0.1)
            self.attention_dropout = self.config.get('attention_dropout', 0.1)
            self.activation_dropout = self.config.get('activation_dropout', 0.1)
            self.architecture = self.config.get('architecture', 'rna language')
            self.max_seqlen = self.config.get('max_seqlen', 1024)
            self.max_tokens = self.config.get('max_tokens', 16384)
            self.max_seqs_per_msa = self.config.get('max_seqs_per_msa', 512)
            self.sample_method = self.config.get('sample_method', 'hhfilter')
            self.extract_layer = self.config.get('extract_layer', -1)
            self.extract_attention = self.config.get('extract_attention', True)
            self.extract_embeddings = self.config.get('extract_embeddings', True)

    def load_model(self, checkpoint_path: str) -> None:
        """Load RNA-MSM model
        
        Args:
            checkpoint_path: Path to model checkpoint
        """
        try:
            checkpoint_path = Path(checkpoint_path)
            if not checkpoint_path.exists():
                raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
                
            self.logger.info(f"Loading RNA-MSM model from {checkpoint_path}")
            
            # Setup alphabet and vocab
            self.alphabet = Alphabet.from_architecture(self.architecture)
            self.vocab = Vocab.from_esm_alphabet(self.alphabet)
            
            # Create model
            # Using dummy optimizer config
            from dataclasses import dataclass, field
            from typing import Tuple
            
            @dataclass
            class OptimizerConfig:
                name: str = "adam"
                learning_rate: float = 3e-4
                weight_decay: float = 3e-4
                lr_scheduler: str = "warmup_cosine"
                warmup_steps: int = 16000
                adam_betas: Tuple[float, float] = (0.9, 0.999)
                max_steps: int = 500000
            
            optimizer_config = OptimizerConfig()
            
            self.model = MSATransformer(
                vocab=self.vocab,
                optimizer_config=optimizer_config,
                contact_train_data=None,
                embed_dim=self.embed_dim,
                num_attention_heads=self.num_attention_heads,
                num_layers=self.num_layers,
                embed_positions_msa=self.embed_positions_msa,
                dropout=self.dropout,
                attention_dropout=self.attention_dropout,
                activation_dropout=self.activation_dropout,
                max_tokens_per_msa=self.max_tokens,
                max_seqlen=self.max_seqlen,
            )
            
            # Load checkpoint
            state = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
            if 'state_dict' in state:
                state = state['state_dict']
            
            self.model.load_state_dict(state, strict=True)
            self.model = self.model.eval().to(self.device)
            
            self._is_loaded = True
            self.logger.info(f"Successfully loaded RNA-MSM model")
            
        except Exception as e:
            raise ModelLoadError(f"Failed to load RNA-MSM model: {str(e)}")

    def preprocess(self, raw_input: Union[str, List[str], Dict[str, Any]]) -> torch.Tensor:
        """Preprocess input for RNA-MSM model
        
        Args:
            raw_input: RNA sequence(s) or MSA data
            
        Returns:
            Preprocessed tensor
        """
        if not self._is_loaded:
            raise ModelLoadError("Model not loaded. Call load_model() first.")
            
        # Handle different input types
        if isinstance(raw_input, str):
            # Single sequence - create dummy MSA
            return self._process_single_sequence(raw_input)
        elif isinstance(raw_input, list):
            # Multiple sequences - treat as MSA
            return self._process_msa_sequences(raw_input)
        elif isinstance(raw_input, dict):
            # MSA data with metadata
            sequences = raw_input.get('sequences', [])
            return self._process_msa_sequences(sequences)
        else:
            raise InvalidSequenceError("Input must be string, list, or dict")

    def _process_single_sequence(self, sequence: str) -> torch.Tensor:
        """Process single RNA sequence into MSA format"""
        if not self._validate_rna_sequence(sequence):
            raise InvalidSequenceError(f"Invalid RNA sequence: {sequence}")
        
        # Create simple MSA with just the input sequence
        msa_sequences = [sequence]
        return self._encode_msa(msa_sequences)

    def _process_msa_sequences(self, sequences: List[str]) -> torch.Tensor:
        """Process MSA sequences"""
        # Validate sequences
        for i, seq in enumerate(sequences):
            if not self._validate_rna_sequence(seq):
                raise InvalidSequenceError(f"Invalid RNA sequence at position {i}: {seq}")
        
        # Limit MSA size
        if len(sequences) > self.max_seqs_per_msa:
            sequences = sequences[:self.max_seqs_per_msa]
            
        return self._encode_msa(sequences)

    def _encode_msa(self, sequences: List[str]) -> torch.Tensor:
        """Encode MSA sequences to tensor"""
        # Convert sequences to tokens
        tokens_list = []
        for seq in sequences:
            # Truncate if too long
            if len(seq) > self.max_seqlen:
                seq = seq[:self.max_seqlen]
            tokens = self.vocab.encode(seq)
            tokens_list.append(tokens)
        
        # Pad to same length
        max_len = max(len(tokens) for tokens in tokens_list)
        padded_tokens = []
        
        for tokens in tokens_list:
            if len(tokens) < max_len:
                # Pad with padding token
                pad_token = self.vocab.padding_idx
                tokens = tokens + [pad_token] * (max_len - len(tokens))
            padded_tokens.append(tokens)
        
        # Convert to tensor
        msa_tensor = torch.tensor(padded_tokens, dtype=torch.long)
        return msa_tensor

    def _validate_rna_sequence(self, sequence: str) -> bool:
        """Validate RNA sequence"""
        if not sequence:
            return False
        
        valid_chars = set('AUGC')
        return all(c.upper() in valid_chars for c in sequence if c.isalpha())

    def predict(self, input_data: torch.Tensor) -> Dict[str, Any]:
        """Run inference on preprocessed input
        
        Args:
            input_data: Preprocessed tensor
            
        Returns:
            Model outputs including attention and embeddings
        """
        if not self._is_loaded:
            raise ModelLoadError("Model not loaded. Call load_model() first.")
            
        try:
            with torch.no_grad():
                input_data = input_data.to(self.device)
                
                # Add batch dimension if needed
                if input_data.dim() == 2:
                    input_data = input_data.unsqueeze(0)
                
                # Run model
                extract_layer = self.num_layers if self.extract_layer == -1 else self.extract_layer
                
                results = self.model(
                    input_data, 
                    repr_layers=[extract_layer], 
                    need_head_weights=self.extract_attention
                )
                
                return results
                
        except Exception as e:
            raise PredictionError(f"Prediction failed: {str(e)}")

    def postprocess(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess model outputs
        
        Args:
            raw_output: Raw model outputs
            
        Returns:
            Processed results with attention maps and embeddings
        """
        results = {}
        
        try:
            # Extract attention maps if available
            if self.extract_attention and "row_attentions" in raw_output:
                attentions = raw_output["row_attentions"]
                
                # Remove BOS/EOS tokens
                start_idx = int(self.vocab.prepend_bos)
                end_idx = attentions.size(-1) - int(self.vocab.append_eos)
                attentions = attentions[..., start_idx:end_idx, start_idx:end_idx]
                
                seqlen = attentions.size(-1)
                attentions = attentions.view(-1, seqlen, seqlen).cpu().numpy()
                results["attention_maps"] = attentions
            
            # Extract embeddings if available
            if self.extract_embeddings and "representations" in raw_output:
                layer_idx = self.num_layers if self.extract_layer == -1 else self.extract_layer
                
                if layer_idx in raw_output["representations"]:
                    embedding = raw_output["representations"][layer_idx]
                    
                    # Remove BOS/EOS tokens
                    start_idx = int(self.vocab.prepend_bos)
                    end_idx = embedding.size(-2) - int(self.vocab.append_eos)
                    embedding = embedding[:, 0, start_idx:end_idx, :].squeeze(0).cpu().numpy()
                    
                    results["embeddings"] = embedding
            
            # Add metadata
            results["model_info"] = {
                "model_type": self.model_type,
                "num_layers": self.num_layers,
                "embed_dim": self.embed_dim,
                "extraction_layer": self.extract_layer if self.extract_layer != -1 else self.num_layers
            }
            
            return results
            
        except Exception as e:
            raise PredictionError(f"Postprocessing failed: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_type": self.model_type,
            "loaded": self._is_loaded,
            "device": self.device,
            "architecture": self.architecture if hasattr(self, 'architecture') else None,
            "embed_dim": self.embed_dim if hasattr(self, 'embed_dim') else None,
            "num_layers": self.num_layers if hasattr(self, 'num_layers') else None,
            "max_seqlen": self.max_seqlen if hasattr(self, 'max_seqlen') else None,
        } 