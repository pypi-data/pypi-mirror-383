"""
AI Model initialization and management system.
Handles automatic model downloading, caching, and version management.
"""

import os
import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import requests
from tqdm import tqdm
import tempfile

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class ModelInfo:
    """Information about an AI model."""
    
    def __init__(self, 
                 name: str,
                 size_mb: int,
                 description: str,
                 languages: List[str],
                 embedding_dim: int,
                 url: Optional[str] = None,
                 checksum: Optional[str] = None):
        self.name = name
        self.size_mb = size_mb
        self.description = description
        self.languages = languages
        self.embedding_dim = embedding_dim
        self.url = url
        self.checksum = checksum


class ModelManager:
    """Manages AI model downloading, caching, and initialization."""
    
    # Available models with metadata
    AVAILABLE_MODELS = {
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": ModelInfo(
            name="paraphrase-multilingual-MiniLM-L12-v2",
            size_mb=420,
            description="Multilingual model supporting Korean and English",
            languages=["ko", "en", "zh", "ja", "de", "fr", "es"],
            embedding_dim=384
        ),
        "sentence-transformers/all-MiniLM-L6-v2": ModelInfo(
            name="all-MiniLM-L6-v2", 
            size_mb=90,
            description="Lightweight English model",
            languages=["en"],
            embedding_dim=384
        ),
        "sentence-transformers/paraphrase-MiniLM-L6-v2": ModelInfo(
            name="paraphrase-MiniLM-L6-v2",
            size_mb=90,
            description="Compact English paraphrase model",
            languages=["en"],
            embedding_dim=384
        )
    }
    
    DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    FALLBACK_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize model manager.
        
        Args:
            cache_dir: Directory to cache models
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".maekrak" / "models"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.cache_dir / "models_metadata.json"
        self.offline_mode = False
        
        # Load existing metadata
        self.metadata = self._load_metadata()
    
    def initialize_models(self, 
                         preferred_model: Optional[str] = None,
                         force_download: bool = False,
                         offline_mode: bool = False,
                         progress_callback=None) -> Tuple[bool, str, Optional[str]]:
        """Initialize AI models for first-time use.
        
        Args:
            preferred_model: Preferred model name
            force_download: Force re-download even if cached
            offline_mode: Skip downloads and use cached models only
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (success, model_name, error_message)
        """
        self.offline_mode = offline_mode
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return False, "", "sentence-transformers library not available"
        
        if progress_callback:
            progress_callback(10)
        
        # Determine which model to use
        target_model = preferred_model or self.DEFAULT_MODEL
        
        # Check if model is already available
        if not force_download and self._is_model_available(target_model):
            if self._verify_model_integrity(target_model):
                if progress_callback:
                    progress_callback(100)
                return True, target_model, None
            else:
                print(f"Model {target_model} failed integrity check, re-downloading...")
        
        if progress_callback:
            progress_callback(20)
        
        # Try to download/initialize the target model
        success, error = self._ensure_model_available(target_model, progress_callback)
        if success:
            return True, target_model, None
        
        # If target model failed, try fallback model
        if target_model != self.FALLBACK_MODEL:
            print(f"Failed to initialize {target_model}, trying fallback model...")
            if progress_callback:
                progress_callback(50)
            success, error = self._ensure_model_available(self.FALLBACK_MODEL, progress_callback)
            if success:
                return True, self.FALLBACK_MODEL, None
        
        # If all models failed
        if offline_mode:
            return False, "", "No cached models available in offline mode"
        else:
            return False, "", f"Failed to initialize any models: {error}"
    
    def get_model_status(self, model_name: str) -> Dict[str, Any]:
        """Get status information for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with model status information
        """
        model_info = self.AVAILABLE_MODELS.get(model_name)
        if not model_info:
            return {
                'available': False,
                'error': 'Unknown model'
            }
        
        cached = self._is_model_available(model_name)
        valid = self._verify_model_integrity(model_name) if cached else False
        
        status = {
            'name': model_name,
            'available': cached and valid,
            'cached': cached,
            'valid': valid,
            'size_mb': model_info.size_mb,
            'description': model_info.description,
            'languages': model_info.languages,
            'embedding_dim': model_info.embedding_dim
        }
        
        if cached:
            model_path = self._get_model_path(model_name)
            if model_path.exists():
                # Get cache info
                cache_size = sum(f.stat().st_size for f in model_path.rglob('*') if f.is_file())
                status['cache_size_bytes'] = cache_size
                status['cache_path'] = str(model_path)
                
                # Get last modified time
                metadata = self.metadata.get(model_name, {})
                status['downloaded_at'] = metadata.get('downloaded_at')
                status['last_used'] = metadata.get('last_used')
        
        return status
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models with their status.
        
        Returns:
            List of model information dictionaries
        """
        models = []
        for model_name in self.AVAILABLE_MODELS:
            status = self.get_model_status(model_name)
            models.append(status)
        
        return models
    
    def cleanup_old_models(self, keep_days: int = 30) -> Dict[str, Any]:
        """Clean up old or unused models.
        
        Args:
            keep_days: Number of days to keep unused models
            
        Returns:
            Dictionary with cleanup results
        """
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        cleaned_models = []
        total_space_freed = 0
        
        for model_name in list(self.metadata.keys()):
            model_metadata = self.metadata[model_name]
            last_used = datetime.fromisoformat(model_metadata.get('last_used', '1970-01-01'))
            
            if last_used < cutoff_date:
                model_path = self._get_model_path(model_name)
                if model_path.exists():
                    # Calculate size before deletion
                    size = sum(f.stat().st_size for f in model_path.rglob('*') if f.is_file())
                    
                    # Remove model
                    shutil.rmtree(model_path)
                    del self.metadata[model_name]
                    
                    cleaned_models.append(model_name)
                    total_space_freed += size
        
        # Save updated metadata
        self._save_metadata()
        
        return {
            'cleaned_models': cleaned_models,
            'space_freed_bytes': total_space_freed,
            'space_freed_mb': total_space_freed / (1024 * 1024)
        }
    
    def update_model_usage(self, model_name: str) -> None:
        """Update the last used timestamp for a model.
        
        Args:
            model_name: Name of the model
        """
        if model_name in self.metadata:
            self.metadata[model_name]['last_used'] = datetime.now().isoformat()
            self._save_metadata()
    
    def _ensure_model_available(self, model_name: str, progress_callback=None) -> Tuple[bool, Optional[str]]:
        """Ensure a model is available, downloading if necessary.
        
        Args:
            model_name: Name of the model to ensure
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (success, error_message)
        """
        if self.offline_mode:
            if self._is_model_available(model_name):
                return True, None
            else:
                return False, f"Model {model_name} not available in offline mode"
        
        try:
            if progress_callback:
                progress_callback(20)
            
            print(f"Initializing model: {model_name}")
            
            if progress_callback:
                progress_callback(40)
            
            # Try to load the model (this will download if not cached)
            model = SentenceTransformer(model_name, cache_folder=str(self.cache_dir))
            
            if progress_callback:
                progress_callback(80)
            
            # Update metadata
            self.metadata[model_name] = {
                'downloaded_at': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat(),
                'version': getattr(model, '__version__', 'unknown'),
                'embedding_dim': model.get_sentence_embedding_dimension()
            }
            self._save_metadata()
            
            if progress_callback:
                progress_callback(100)
            
            print(f"Model {model_name} initialized successfully")
            return True, None
            
        except Exception as e:
            error_msg = f"Failed to initialize model {model_name}: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def _is_model_available(self, model_name: str) -> bool:
        """Check if a model is available in cache.
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if model is cached
        """
        model_path = self._get_model_path(model_name)
        return model_path.exists() and any(model_path.iterdir())
    
    def _verify_model_integrity(self, model_name: str) -> bool:
        """Verify the integrity of a cached model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if model is valid
        """
        try:
            model_path = self._get_model_path(model_name)
            if not model_path.exists():
                return False
            
            # Check for essential files
            essential_files = ['config.json', 'pytorch_model.bin']
            for file_name in essential_files:
                if not (model_path / file_name).exists():
                    # Try alternative file names
                    if file_name == 'pytorch_model.bin':
                        alternatives = ['model.safetensors', 'pytorch_model.safetensors']
                        if not any((model_path / alt).exists() for alt in alternatives):
                            return False
                    else:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _get_model_path(self, model_name: str) -> Path:
        """Get the local path for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Path to model directory
        """
        # Convert model name to safe directory name
        safe_name = model_name.replace('/', '_').replace('\\', '_')
        return self.cache_dir / safe_name
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load model metadata from disk.
        
        Returns:
            Metadata dictionary
        """
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load model metadata: {e}")
        
        return {}
    
    def _save_metadata(self) -> None:
        """Save model metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Failed to save model metadata: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the model cache.
        
        Returns:
            Dictionary with cache information
        """
        total_size = 0
        model_count = 0
        
        if self.cache_dir.exists():
            for model_dir in self.cache_dir.iterdir():
                if model_dir.is_dir():
                    model_count += 1
                    size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
                    total_size += size
        
        return {
            'cache_dir': str(self.cache_dir),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'model_count': model_count,
            'models': list(self.metadata.keys())
        }


class ModelInitializer:
    """High-level interface for model initialization."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize model initializer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.model_manager = ModelManager(
            cache_dir=self.config.get('model_cache_dir')
        )
    
    def ensure_models_ready(self, 
                           offline_mode: bool = False,
                           force_download: bool = False,
                           progress_callback=None) -> Dict[str, Any]:
        """Ensure AI models are ready for use.
        
        Args:
            offline_mode: Skip downloads and use cached models only
            force_download: Force re-download even if cached
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with initialization results
        """
        preferred_model = self.config.get('embedding_model')
        
        success, model_name, error = self.model_manager.initialize_models(
            preferred_model=preferred_model,
            force_download=force_download,
            offline_mode=offline_mode,
            progress_callback=progress_callback
        )
        
        result = {
            'success': success,
            'model_name': model_name,
            'offline_mode': offline_mode
        }
        
        if error:
            result['error'] = error
        
        if success:
            # Update usage tracking
            self.model_manager.update_model_usage(model_name)
            
            # Get model status
            status = self.model_manager.get_model_status(model_name)
            result['model_info'] = status
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status.
        
        Returns:
            Dictionary with system status
        """
        return {
            'sentence_transformers_available': SENTENCE_TRANSFORMERS_AVAILABLE,
            'cache_info': self.model_manager.get_cache_info(),
            'available_models': self.model_manager.list_available_models()
        }