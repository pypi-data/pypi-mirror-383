#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Custom Model Manager - Handles registration and management of custom trained models
Provides integration for models trained through ISA Model training pipeline
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class CustomModelInfo:
    """Information about a custom model"""
    model_id: str
    model_name: str
    model_type: str  # 'text', 'vision', 'audio', etc.
    provider: str
    base_model: str  # The base model this was fine-tuned from
    training_date: str
    model_path: str  # Local path or HuggingFace repo
    metadata: Dict[str, Any]
    capabilities: List[str]
    performance_metrics: Optional[Dict[str, float]] = None
    deployment_config: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class CustomModelManager:
    """
    Manages custom trained models in the ISA Model ecosystem
    Handles registration, discovery, and integration of custom models
    """
    
    def __init__(self, models_registry_path: str = None):
        self.models_registry_path = models_registry_path or os.path.join(
            os.path.expanduser("~"), ".isa_model", "custom_models.json"
        )
        self._models: Dict[str, CustomModelInfo] = {}
        self._load_models_registry()
    
    def _load_models_registry(self):
        """Load custom models registry from file"""
        if os.path.exists(self.models_registry_path):
            try:
                with open(self.models_registry_path, 'r', encoding='utf-8') as f:
                    models_data = json.load(f)
                
                for model_data in models_data.get('models', []):
                    model_info = CustomModelInfo(**model_data)
                    self._models[model_info.model_id] = model_info
                
                logger.info(f"Loaded {len(self._models)} custom models from registry")
            except Exception as e:
                logger.warning(f"Failed to load models registry: {e}")
                self._models = {}
        else:
            # Create default registry with some ISA models
            self._create_default_registry()
    
    def _create_default_registry(self):
        """Create default registry with ISA models"""
        default_models = [
            CustomModelInfo(
                model_id="isa-llm-service",
                model_name="ISA LLM Service",
                model_type="text",
                provider="isa",
                base_model="DialoGPT-small",
                training_date="2024-12-19",
                model_path="modal://isa-llm-inference",
                metadata={
                    "description": "ISA custom LLM service with fallback support",
                    "parameters": "124M",
                    "context_length": 1024,
                    "languages": ["en", "zh"]
                },
                capabilities=["chat", "text_generation", "conversation"],
                performance_metrics={
                    "perplexity": 3.2,
                    "bleu_score": 0.75,
                    "response_time_ms": 850
                },
                deployment_config={
                    "platform": "modal",
                    "gpu_type": "A10G",
                    "memory_gb": 16,
                    "concurrent_requests": 5
                }
            ),
            CustomModelInfo(
                model_id="xenodennis/dialoGPT-small-20241219-v1",
                model_name="ISA Fine-tuned DialoGPT",
                model_type="text",
                provider="huggingface",
                base_model="microsoft/DialoGPT-small",
                training_date="2024-12-19",
                model_path="xenodennis/dialoGPT-small-20241219-v1",
                metadata={
                    "description": "DialoGPT model fine-tuned with ISA training pipeline",
                    "parameters": "124M",
                    "trainable_parameters": "294K (LoRA)",
                    "training_steps": 1000,
                    "languages": ["en", "zh"]
                },
                capabilities=["chat", "text_generation", "dialogue"],
                performance_metrics={
                    "final_loss": 2.1234,
                    "eval_loss": 2.3456,
                    "training_time_minutes": 15
                }
            ),
            CustomModelInfo(
                model_id="isa-custom-embeddings",
                model_name="ISA Custom Embeddings",
                model_type="embedding",
                provider="isa",
                base_model="sentence-transformers/all-MiniLM-L6-v2",
                training_date="2024-12-19",
                model_path="local://models/isa-embeddings",
                metadata={
                    "description": "Custom embeddings trained on ISA domain data",
                    "dimensions": 384,
                    "max_sequence_length": 512
                },
                capabilities=["embed", "similarity", "clustering"]
            )
        ]
        
        for model in default_models:
            self._models[model.model_id] = model
        
        self._save_models_registry()
        logger.info(f"Created default registry with {len(default_models)} models")
    
    def _save_models_registry(self):
        """Save models registry to file"""
        try:
            os.makedirs(os.path.dirname(self.models_registry_path), exist_ok=True)
            
            registry_data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "models": [model.to_dict() for model in self._models.values()]
            }
            
            with open(self.models_registry_path, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved models registry to {self.models_registry_path}")
        except Exception as e:
            logger.error(f"Failed to save models registry: {e}")
    
    def register_model(self, model_info: CustomModelInfo) -> bool:
        """Register a new custom model"""
        try:
            self._models[model_info.model_id] = model_info
            self._save_models_registry()
            logger.info(f"Registered custom model: {model_info.model_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register model {model_info.model_id}: {e}")
            return False
    
    def unregister_model(self, model_id: str) -> bool:
        """Unregister a custom model"""
        if model_id in self._models:
            del self._models[model_id]
            self._save_models_registry()
            logger.info(f"Unregistered custom model: {model_id}")
            return True
        return False
    
    def get_model(self, model_id: str) -> Optional[CustomModelInfo]:
        """Get custom model information"""
        return self._models.get(model_id)
    
    def list_models(self, model_type: str = None, provider: str = None) -> List[CustomModelInfo]:
        """List custom models with optional filtering"""
        models = list(self._models.values())
        
        if model_type:
            models = [m for m in models if m.model_type == model_type]
        
        if provider:
            models = [m for m in models if m.provider == provider]
        
        return models
    
    def get_models_for_api(self) -> List[Dict[str, Any]]:
        """Get models in API format for model listing"""
        api_models = []
        
        for model in self._models.values():
            api_model = {
                "model_id": model.model_id,
                "service_type": model.model_type,
                "provider": model.provider,
                "description": model.metadata.get("description", ""),
                "capabilities": model.capabilities,
                "custom": True,
                "base_model": model.base_model,
                "training_date": model.training_date
            }
            
            # Add performance metrics if available
            if model.performance_metrics:
                api_model["performance"] = model.performance_metrics
            
            api_models.append(api_model)
        
        return api_models
    
    def search_models(self, query: str) -> List[CustomModelInfo]:
        """Search custom models by query"""
        query_lower = query.lower()
        matching_models = []
        
        for model in self._models.values():
            # Search in model_id, name, description, and capabilities
            searchable_text = f"{model.model_id} {model.model_name} {model.metadata.get('description', '')} {' '.join(model.capabilities)}".lower()
            
            if query_lower in searchable_text:
                matching_models.append(model)
        
        return matching_models
    
    def get_deployment_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment configuration for a model"""
        model = self.get_model(model_id)
        return model.deployment_config if model else None
    
    def update_performance_metrics(self, model_id: str, metrics: Dict[str, float]) -> bool:
        """Update performance metrics for a model"""
        model = self.get_model(model_id)
        if model:
            model.performance_metrics = metrics
            self._save_models_registry()
            return True
        return False
    
    def get_provider_models(self, provider: str) -> List[CustomModelInfo]:
        """Get all models for a specific provider"""
        return [model for model in self._models.values() if model.provider == provider]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about custom models"""
        models_by_type = {}
        models_by_provider = {}
        
        for model in self._models.values():
            models_by_type[model.model_type] = models_by_type.get(model.model_type, 0) + 1
            models_by_provider[model.provider] = models_by_provider.get(model.provider, 0) + 1
        
        return {
            "total_models": len(self._models),
            "models_by_type": models_by_type,
            "models_by_provider": models_by_provider,
            "registry_path": self.models_registry_path
        }

# Global instance
_custom_model_manager = None

def get_custom_model_manager() -> CustomModelManager:
    """Get the global custom model manager instance"""
    global _custom_model_manager
    if _custom_model_manager is None:
        _custom_model_manager = CustomModelManager()
    return _custom_model_manager