"""
HuggingFace Hub Storage Implementation

Provides storage capabilities using HuggingFace Hub as the backend.
Supports uploading trained models, managing versions, and metadata.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

try:
    from huggingface_hub import HfApi, create_repo, upload_folder, snapshot_download
    from huggingface_hub.errors import HfHubHTTPError
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False

from ..models.model_storage import ModelStorage

logger = logging.getLogger(__name__)


class HuggingFaceStorage(ModelStorage):
    """
    HuggingFace Hub storage implementation for model management.
    
    This storage backend uploads models to HuggingFace Hub and manages
    them using the repository system. Perfect for sharing trained models
    and maintaining versions.
    
    Example:
        ```python
        from isa_model.core.storage import HuggingFaceStorage
        
        storage = HuggingFaceStorage(
            username="xenobordom",
            token=os.getenv("HF_TOKEN")  # Set in environment
        )
        
        # Save a trained model to HuggingFace Hub
        await storage.save_model(
            model_id="gemma-4b-alpaca-v1",
            model_path="./trained_models/gemma-4b",
            metadata={
                "base_model": "google/gemma-2-4b-it",
                "dataset": "tatsu-lab/alpaca",
                "training_method": "LoRA + Unsloth"
            }
        )
        ```
    """
    
    def __init__(self, 
                 username: str = "xenobordom",
                 token: Optional[str] = None,
                 private: bool = False,
                 local_cache_dir: str = "./models/hf_cache"):
        """
        Initialize HuggingFace storage.
        
        Args:
            username: HuggingFace username (default: xenobordom)
            token: HuggingFace API token (from env if not provided)
            private: Whether to create private repositories
            local_cache_dir: Local cache directory for downloaded models
        """
        if not HF_HUB_AVAILABLE:
            raise ImportError("huggingface_hub is required. Install with: pip install huggingface_hub")
        
        self.username = username
        self.token = token or os.getenv("HF_TOKEN")
        self.private = private
        self.local_cache_dir = Path(local_cache_dir)
        self.local_cache_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.token:
            raise ValueError("HuggingFace token is required. Set HF_TOKEN environment variable or pass token parameter.")
        
        # Initialize HF API
        self.api = HfApi(token=self.token)
        
        # Local metadata storage
        self.metadata_file = self.local_cache_dir / "hf_models_metadata.json"
        self._load_metadata()
        
        logger.info(f"HuggingFace storage initialized for user: {self.username}")
        logger.info(f"Local cache directory: {self.local_cache_dir}")
    
    def _load_metadata(self):
        """Load local metadata cache"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
            self._save_metadata()
    
    def _save_metadata(self):
        """Save local metadata cache"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _get_repo_id(self, model_id: str) -> str:
        """Get full repository ID for a model"""
        return f"{self.username}/{model_id}"
    
    async def save_model(self, model_id: str, model_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Save model to HuggingFace Hub.
        
        Args:
            model_id: Unique identifier for the model (will be repo name)
            model_path: Local path to model files
            metadata: Model metadata to include
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repo_id = self._get_repo_id(model_id)
            source_path = Path(model_path)
            
            logger.info(f"Uploading model {model_id} to HuggingFace Hub: {repo_id}")
            
            # Create repository if it doesn't exist
            try:
                create_repo(
                    repo_id=repo_id,
                    token=self.token,
                    private=self.private,
                    exist_ok=True
                )
                logger.info(f"Repository created/verified: {repo_id}")
            except Exception as e:
                logger.warning(f"Repository creation warning: {e}")
            
            # Prepare metadata for README
            readme_content = self._generate_model_card(model_id, metadata)
            
            # Create temporary directory for upload preparation
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Copy model files
                if source_path.is_file():
                    shutil.copy2(source_path, temp_path / source_path.name)
                else:
                    # Copy entire directory
                    for item in source_path.rglob("*"):
                        if item.is_file():
                            relative_path = item.relative_to(source_path)
                            dest_path = temp_path / relative_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, dest_path)
                
                # Add README.md
                with open(temp_path / "README.md", 'w') as f:
                    f.write(readme_content)
                
                # Add metadata.json
                enhanced_metadata = {
                    **metadata,
                    "model_id": model_id,
                    "repo_id": repo_id,
                    "uploaded_at": datetime.now().isoformat(),
                    "uploaded_by": self.username,
                    "storage_backend": "huggingface_hub"
                }
                
                with open(temp_path / "metadata.json", 'w') as f:
                    json.dump(enhanced_metadata, f, indent=2)
                
                # Upload to HuggingFace Hub
                upload_folder(
                    folder_path=str(temp_path),
                    repo_id=repo_id,
                    token=self.token,
                    commit_message=f"Upload {model_id} - {metadata.get('description', 'Model upload')}"
                )
            
            # Update local metadata
            self.metadata[model_id] = {
                **enhanced_metadata,
                "local_cache_path": str(self.local_cache_dir / model_id),
                "repo_url": f"https://huggingface.co/{repo_id}"
            }
            self._save_metadata()
            
            logger.info(f"Model {model_id} uploaded successfully to {repo_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save model {model_id} to HuggingFace Hub: {e}")
            return False
    
    async def load_model(self, model_id: str) -> Optional[Path]:
        """
        Load model from HuggingFace Hub.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Path to local model files
        """
        try:
            repo_id = self._get_repo_id(model_id)
            local_path = self.local_cache_dir / model_id
            
            # Check if already cached
            if local_path.exists() and model_id in self.metadata:
                logger.info(f"Using cached model {model_id}")
                return local_path
            
            logger.info(f"Downloading model {model_id} from HuggingFace Hub: {repo_id}")
            
            # Download from HuggingFace Hub
            snapshot_download(
                repo_id=repo_id,
                local_dir=str(local_path),
                token=self.token,
                local_dir_use_symlinks=False
            )
            
            # Load metadata if available
            metadata_file = local_path / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                self.metadata[model_id] = {
                    **metadata,
                    "local_cache_path": str(local_path),
                    "last_downloaded": datetime.now().isoformat()
                }
                self._save_metadata()
            
            logger.info(f"Model {model_id} downloaded successfully")
            return local_path
            
        except HfHubHTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"Model {model_id} not found on HuggingFace Hub")
            else:
                logger.error(f"Failed to load model {model_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return None
    
    async def delete_model(self, model_id: str) -> bool:
        """
        Delete model from HuggingFace Hub and local cache.
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repo_id = self._get_repo_id(model_id)
            
            # Delete from HuggingFace Hub
            try:
                self.api.delete_repo(repo_id=repo_id, token=self.token)
                logger.info(f"Deleted repository {repo_id} from HuggingFace Hub")
            except Exception as e:
                logger.warning(f"Failed to delete repository {repo_id}: {e}")
            
            # Delete local cache
            local_path = self.local_cache_dir / model_id
            if local_path.exists():
                shutil.rmtree(local_path)
                logger.info(f"Deleted local cache for {model_id}")
            
            # Remove from metadata
            if model_id in self.metadata:
                del self.metadata[model_id]
                self._save_metadata()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete model {model_id}: {e}")
            return False
    
    async def get_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model metadata"""
        return self.metadata.get(model_id)
    
    async def list_models(self) -> Dict[str, Dict[str, Any]]:
        """List all models managed by this storage"""
        return self.metadata.copy()
    
    def _generate_model_card(self, model_id: str, metadata: Dict[str, Any]) -> str:
        """Generate a model card for HuggingFace Hub"""
        base_model = metadata.get("base_model", "Unknown")
        dataset = metadata.get("dataset", "Unknown")
        training_method = metadata.get("training_method", "Unknown")
        description = metadata.get("description", f"Fine-tuned {base_model}")
        
        model_card = f"""---
license: apache-2.0
base_model: {base_model}
tags:
- generated_from_trainer
- isa-model
- {training_method.lower().replace(' ', '-')}
datasets:
- {dataset}
language:
- en
pipeline_tag: text-generation
---

# {model_id}

{description}

## Model Details

- **Base Model**: {base_model}
- **Training Dataset**: {dataset}
- **Training Method**: {training_method}
- **Uploaded by**: {self.username}
- **Framework**: ISA Model SDK

## Training Details

"""
        
        # Add training configuration if available
        if "config" in metadata:
            config = metadata["config"]
            model_card += f"""
### Training Configuration

- **Epochs**: {config.get('num_epochs', 'Unknown')}
- **Batch Size**: {config.get('batch_size', 'Unknown')}
- **Learning Rate**: {config.get('learning_rate', 'Unknown')}
- **LoRA**: {'Yes' if config.get('use_lora', False) else 'No'}
"""
            
            if config.get('use_lora', False):
                lora_config = config.get('lora_config', {})
                model_card += f"""
### LoRA Configuration

- **LoRA Rank**: {lora_config.get('lora_rank', 'Unknown')}
- **LoRA Alpha**: {lora_config.get('lora_alpha', 'Unknown')}
- **LoRA Dropout**: {lora_config.get('lora_dropout', 'Unknown')}
"""
        
        model_card += f"""

## Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("{self._get_repo_id(model_id)}")
model = AutoModelForCausalLM.from_pretrained("{self._get_repo_id(model_id)}")

# For inference
inputs = tokenizer("Your prompt here", return_tensors="pt")
outputs = model.generate(**inputs, max_length=100)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

## ISA Model SDK

This model was trained using the [ISA Model SDK](https://github.com/your-repo/isA_Model), 
a comprehensive framework for training and deploying AI models.

"""
        
        return model_card
    
    def get_public_url(self, model_id: str) -> str:
        """Get public URL for a model on HuggingFace Hub"""
        return f"https://huggingface.co/{self._get_repo_id(model_id)}"
    
    async def update_model_metadata(self, model_id: str, new_metadata: Dict[str, Any]) -> bool:
        """Update model metadata on HuggingFace Hub"""
        try:
            if model_id not in self.metadata:
                logger.error(f"Model {model_id} not found in metadata")
                return False
            
            # Update local metadata
            self.metadata[model_id].update(new_metadata)
            self._save_metadata()
            
            # Update README on HuggingFace Hub
            repo_id = self._get_repo_id(model_id)
            readme_content = self._generate_model_card(model_id, self.metadata[model_id])
            
            self.api.upload_file(
                path_or_fileobj=readme_content.encode('utf-8'),
                path_in_repo="README.md",
                repo_id=repo_id,
                token=self.token,
                commit_message=f"Update metadata for {model_id}"
            )
            
            logger.info(f"Updated metadata for model {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update metadata for {model_id}: {e}")
            return False
