"""
HuggingFace Transformers local inference service

Direct model loading and inference using HuggingFace Transformers.
"""

import os
import json
import asyncio
import logging
import threading
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import time
import torch

from .config import LocalGPUConfig, LocalServiceType, LocalBackend
from ...utils.gpu_utils import get_gpu_manager

logger = logging.getLogger(__name__)


class TransformersService:
    """HuggingFace Transformers local inference service"""
    
    def __init__(self, config: LocalGPUConfig):
        """
        Initialize Transformers service.
        
        Args:
            config: Local GPU configuration for Transformers
        """
        if config.backend != LocalBackend.TRANSFORMERS:
            raise ValueError("Config must use TRANSFORMERS backend")
            
        self.config = config
        self.gpu_manager = get_gpu_manager()
        self.model = None
        self.tokenizer = None
        self.processor = None  # For multimodal models
        self.model_loaded = False
        self.startup_time: Optional[datetime] = None
        self.device = None
        
        # Thread safety for inference
        self._inference_lock = threading.Lock()
        
        # Service info
        self.service_info = {
            "service_name": config.service_name,
            "model_id": config.model_id,
            "backend": "transformers",
            "status": "stopped",
            "device": None
        }
    
    async def load_model(self) -> Dict[str, Any]:
        """
        Load HuggingFace model for inference.
        
        Returns:
            Model loading result
        """
        if self.model_loaded:
            return {
                "success": True,
                "message": "Model already loaded",
                "service_info": self.service_info
            }
        
        try:
            logger.info(f"Loading Transformers model: {self.config.model_id}")
            self.startup_time = datetime.now()
            
            # Check GPU requirements
            gpu_check = await self._check_gpu_requirements()
            if not gpu_check["compatible"]:
                return {
                    "success": False,
                    "error": f"GPU requirements not met: {', '.join(gpu_check['warnings'])}",
                    "gpu_check": gpu_check
                }
            
            # Set device
            self.device = await self._setup_device()
            
            # Load model components
            load_result = await self._load_model_components()
            
            if load_result["success"]:
                self.model_loaded = True
                self.service_info.update({
                    "status": "running",
                    "device": str(self.device),
                    "loaded_at": self.startup_time.isoformat(),
                    "load_time": load_result["load_time"],
                    "model_info": load_result["model_info"]
                })
                
                logger.info(f"Transformers model loaded successfully on {self.device}")
                return {
                    "success": True,
                    "service_info": self.service_info,
                    "load_time": load_result["load_time"],
                    "gpu_info": gpu_check.get("selected_gpu")
                }
            else:
                return load_result
                
        except Exception as e:
            logger.error(f"Failed to load Transformers model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def unload_model(self) -> Dict[str, Any]:
        """Unload model and free GPU memory"""
        try:
            if self.model:
                del self.model
                self.model = None
            
            if self.tokenizer:
                del self.tokenizer
                self.tokenizer = None
                
            if self.processor:
                del self.processor
                self.processor = None
            
            self.model_loaded = False
            self.service_info.update({
                "status": "stopped",
                "device": None,
                "unloaded_at": datetime.now().isoformat()
            })
            
            # Free GPU memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("Transformers model unloaded")
            return {
                "success": True,
                "service_info": self.service_info
            }
            
        except Exception as e:
            logger.error(f"Failed to unload model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using the loaded model"""
        if not self.model_loaded:
            return {
                "success": False,
                "error": "Model not loaded"
            }
        
        try:
            with self._inference_lock:
                start_time = time.time()
                
                # Prepare generation parameters
                max_tokens = kwargs.get("max_tokens", 512)
                temperature = kwargs.get("temperature", 0.7)
                top_p = kwargs.get("top_p", 0.9)
                top_k = kwargs.get("top_k", 50)
                do_sample = kwargs.get("do_sample", True)
                
                # Tokenize input
                inputs = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=self.config.max_model_len // 2
                ).to(self.device)
                
                # Generate
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        top_k=top_k,
                        do_sample=do_sample,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        use_cache=True
                    )
                
                # Decode output
                input_length = inputs['input_ids'].shape[-1]
                generated_tokens = outputs[0][input_length:]
                generated_text = self.tokenizer.decode(
                    generated_tokens,
                    skip_special_tokens=True
                ).strip()
                
                generation_time = time.time() - start_time
                
                return {
                    "success": True,
                    "text": generated_text,
                    "model": self.config.model_id,
                    "generation_time": generation_time,
                    "input_tokens": input_length,
                    "output_tokens": len(generated_tokens),
                    "total_tokens": len(outputs[0])
                }
                
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate chat completion response"""
        # Convert messages to prompt
        prompt = await self._format_chat_messages(messages)
        
        # Generate response
        result = await self.generate_text(prompt, **kwargs)
        
        if result["success"]:
            # Format as chat completion
            return {
                "success": True,
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": result["text"]
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": result["input_tokens"],
                    "completion_tokens": result["output_tokens"],
                    "total_tokens": result["total_tokens"]
                },
                "model": result["model"],
                "generation_time": result["generation_time"]
            }
        else:
            return result
    
    async def analyze_image(self, image_data: bytes, prompt: str = "Describe this image.", **kwargs) -> Dict[str, Any]:
        """Analyze image using vision model"""
        if self.config.service_type != LocalServiceType.VISION:
            return {
                "success": False,
                "error": "Service not configured for vision tasks"
            }
        
        if not self.processor:
            return {
                "success": False,
                "error": "Vision processor not loaded"
            }
        
        try:
            with self._inference_lock:
                start_time = time.time()
                
                from PIL import Image
                import io
                
                # Load image
                image = Image.open(io.BytesIO(image_data)).convert('RGB')
                
                # Process inputs
                inputs = self.processor(
                    text=prompt,
                    images=image,
                    return_tensors="pt"
                ).to(self.device)
                
                # Generate
                max_tokens = kwargs.get("max_tokens", 512)
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        do_sample=True,
                        temperature=kwargs.get("temperature", 0.7)
                    )
                
                # Decode
                response = self.processor.decode(outputs[0], skip_special_tokens=True)
                
                # Clean up response (remove prompt)
                if prompt in response:
                    response = response.replace(prompt, "").strip()
                
                generation_time = time.time() - start_time
                
                return {
                    "success": True,
                    "text": response,
                    "model": self.config.model_id,
                    "generation_time": generation_time
                }
                
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def embed_text(self, texts: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
        """Generate text embeddings"""
        if self.config.service_type != LocalServiceType.EMBEDDING:
            return {
                "success": False,
                "error": "Service not configured for embedding tasks"
            }
        
        try:
            with self._inference_lock:
                start_time = time.time()
                
                # Ensure texts is a list
                if isinstance(texts, str):
                    texts = [texts]
                
                # Tokenize
                inputs = self.tokenizer(
                    texts,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=self.config.max_model_len
                ).to(self.device)
                
                # Generate embeddings
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    
                    # Use different pooling strategies based on model
                    if hasattr(outputs, 'pooler_output') and outputs.pooler_output is not None:
                        embeddings = outputs.pooler_output
                    else:
                        # Mean pooling
                        embeddings = outputs.last_hidden_state.mean(dim=1)
                    
                    # Normalize embeddings
                    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
                
                generation_time = time.time() - start_time
                
                return {
                    "success": True,
                    "embeddings": embeddings.cpu().numpy().tolist(),
                    "model": self.config.model_id,
                    "generation_time": generation_time,
                    "embedding_dimension": embeddings.shape[-1]
                }
                
        except Exception as e:
            logger.error(f"Text embedding failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            "healthy": self.model_loaded,
            "status": "running" if self.model_loaded else "stopped",
            "service_info": self.service_info,
            "device": str(self.device) if self.device else None,
            "model_loaded": self.model_loaded
        }
    
    async def _load_model_components(self) -> Dict[str, Any]:
        """Load model, tokenizer, and processor"""
        try:
            start_time = time.time()
            
            from transformers import (
                AutoTokenizer, AutoModel, AutoModelForCausalLM,
                AutoProcessor, AutoModelForVision2Seq,
                BitsAndBytesConfig
            )
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_id,
                revision=self.config.tokenizer_revision,
                trust_remote_code=self.config.trust_remote_code,
                use_fast=True
            )
            
            # Set pad token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load processor for multimodal models
            if self.config.service_type in [LocalServiceType.VISION, LocalServiceType.AUDIO]:
                try:
                    logger.info("Loading processor...")
                    self.processor = AutoProcessor.from_pretrained(
                        self.config.model_id,
                        revision=self.config.revision,
                        trust_remote_code=self.config.trust_remote_code
                    )
                except Exception as e:
                    logger.warning(f"Failed to load processor: {e}")
            
            # Configure quantization
            quantization_config = None
            if self.config.quantization:
                if self.config.quantization in ["4bit", "int4"]:
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
                elif self.config.quantization in ["8bit", "int8"]:
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True
                    )
            
            # Determine model class based on service type
            if self.config.service_type == LocalServiceType.EMBEDDING:
                model_class = AutoModel
            elif self.config.service_type == LocalServiceType.VISION:
                model_class = AutoModelForVision2Seq
            else:
                model_class = AutoModelForCausalLM
            
            # Configure model loading arguments
            model_kwargs = {
                "revision": self.config.revision,
                "trust_remote_code": self.config.trust_remote_code,
                "torch_dtype": self._get_torch_dtype(),
                "device_map": "auto" if self.config.enable_gpu else "cpu",
                "low_cpu_mem_usage": True,
                **self.config.transformers_args
            }
            
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
            
            # Load model
            logger.info(f"Loading model with {model_class.__name__}...")
            self.model = model_class.from_pretrained(
                self.config.model_id,
                **model_kwargs
            )
            
            # Move to device if not using device_map
            if not self.config.transformers_args.get("device_map"):
                self.model.to(self.device)
            
            self.model.eval()
            
            # Try to compile model for faster inference
            if hasattr(torch, 'compile') and self.config.enable_gpu:
                try:
                    self.model = torch.compile(self.model, mode="reduce-overhead")
                    logger.info("Model compiled for faster inference")
                except Exception as e:
                    logger.warning(f"Model compilation failed: {e}")
            
            load_time = time.time() - start_time
            
            # Get model info
            model_info = {
                "model_id": self.config.model_id,
                "model_type": self.config.service_type.value,
                "torch_dtype": str(self.model.dtype) if hasattr(self.model, 'dtype') else None,
                "device": str(next(self.model.parameters()).device) if hasattr(self.model, 'parameters') else None,
                "quantization": self.config.quantization,
                "parameters": self._count_parameters()
            }
            
            logger.info(f"Model loaded successfully in {load_time:.2f}s")
            
            return {
                "success": True,
                "load_time": load_time,
                "model_info": model_info
            }
            
        except Exception as e:
            logger.error(f"Failed to load model components: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _count_parameters(self) -> Optional[int]:
        """Count model parameters"""
        try:
            if hasattr(self.model, 'num_parameters'):
                return self.model.num_parameters()
            else:
                return sum(p.numel() for p in self.model.parameters())
        except:
            return None
    
    def _get_torch_dtype(self) -> torch.dtype:
        """Get appropriate torch dtype"""
        precision_map = {
            "float32": torch.float32,
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "int8": torch.int8
        }
        return precision_map.get(self.config.model_precision, torch.float16)
    
    async def _setup_device(self) -> torch.device:
        """Setup compute device"""
        if not self.config.enable_gpu or not torch.cuda.is_available():
            return torch.device("cpu")
        
        if self.config.gpu_id is not None:
            device = torch.device(f"cuda:{self.config.gpu_id}")
        else:
            device = torch.device("cuda")
        
        # Set memory fraction
        if torch.cuda.is_available():
            torch.cuda.set_per_process_memory_fraction(
                self.config.gpu_memory_fraction,
                device.index if device.index is not None else 0
            )
        
        return device
    
    async def _format_chat_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages into a prompt"""
        formatted_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                formatted_parts.append(f"System: {content}")
            elif role == "user":
                formatted_parts.append(f"Human: {content}")
            elif role == "assistant":
                formatted_parts.append(f"Assistant: {content}")
        
        formatted_parts.append("Assistant:")
        return "\n\n".join(formatted_parts)
    
    async def _check_gpu_requirements(self) -> Dict[str, Any]:
        """Check GPU requirements"""
        if not self.config.enable_gpu:
            return {
                "compatible": True,
                "warnings": ["Using CPU inference"],
                "selected_gpu": None
            }
        
        self.gpu_manager.refresh()
        
        if not self.gpu_manager.cuda_available:
            return {
                "compatible": True,  # Can fallback to CPU
                "warnings": ["CUDA not available, falling back to CPU"],
                "selected_gpu": None
            }
        
        # Estimate memory requirements
        estimated_memory = self.gpu_manager.estimate_model_memory(
            self.config.model_id,
            self.config.model_precision
        )
        
        # Apply quantization reduction
        if self.config.quantization == "int8":
            estimated_memory = int(estimated_memory * 0.5)
        elif self.config.quantization == "int4":
            estimated_memory = int(estimated_memory * 0.25)
        
        # Find suitable GPU
        if self.config.gpu_id is not None:
            selected_gpu = self.gpu_manager.get_gpu_info(self.config.gpu_id)
            if not selected_gpu:
                return {
                    "compatible": True,
                    "warnings": [f"Specified GPU {self.config.gpu_id} not found, falling back to CPU"],
                    "selected_gpu": None
                }
        else:
            selected_gpu = self.gpu_manager.get_best_gpu(estimated_memory)
            if selected_gpu:
                self.config.gpu_id = selected_gpu.gpu_id
        
        if not selected_gpu:
            return {
                "compatible": True,
                "warnings": [
                    f"No suitable GPU found (Required: {estimated_memory}MB), falling back to CPU"
                ],
                "selected_gpu": None
            }
        
        warnings = []
        
        # Check memory requirements
        required_memory = int(estimated_memory * self.config.gpu_memory_fraction)
        if selected_gpu.memory_free < required_memory:
            warnings.append(f"GPU memory may be tight: {selected_gpu.memory_free}MB available, {required_memory}MB required")
        
        return {
            "compatible": True,
            "warnings": warnings,
            "selected_gpu": {
                "gpu_id": selected_gpu.gpu_id,
                "name": selected_gpu.name,
                "memory_total": selected_gpu.memory_total,
                "memory_free": selected_gpu.memory_free,
                "utilization": selected_gpu.utilization,
                "estimated_memory_required": estimated_memory
            }
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get current service information"""
        return {
            **self.service_info,
            "config": self.config.to_dict(),
            "device": str(self.device) if self.device else None,
            "model_loaded": self.model_loaded,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "parameters": self._count_parameters() if self.model_loaded else None
        }