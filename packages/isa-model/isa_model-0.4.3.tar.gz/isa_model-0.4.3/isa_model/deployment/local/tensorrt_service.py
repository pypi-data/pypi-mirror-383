"""
TensorRT-LLM local inference service

Direct TensorRT-LLM deployment without containers for maximum performance.
"""

import os
import json
import asyncio
import logging
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
import time

from .config import LocalGPUConfig, LocalServiceType, LocalBackend
from ...utils.gpu_utils import get_gpu_manager

logger = logging.getLogger(__name__)


class TensorRTLLMService:
    """TensorRT-LLM local inference service manager"""
    
    def __init__(self, config: LocalGPUConfig):
        """
        Initialize TensorRT-LLM service.
        
        Args:
            config: Local GPU configuration for TensorRT-LLM
        """
        if config.backend != LocalBackend.TENSORRT_LLM:
            raise ValueError("Config must use TENSORRT_LLM backend")
            
        self.config = config
        self.gpu_manager = get_gpu_manager()
        self.workspace_dir: Optional[Path] = None
        self.engine_path: Optional[Path] = None
        self.model_loaded = False
        self.startup_time: Optional[datetime] = None
        
        # TensorRT-LLM imports (lazy loaded)
        self.tensorrt_llm = None
        self.runtime_mapping = None
        self.generation_session = None
        
        # Service info
        self.service_info = {
            "service_name": config.service_name,
            "model_id": config.model_id,
            "backend": "tensorrt_llm",
            "status": "stopped",
            "engine_path": None
        }
    
    async def build_engine(self) -> Dict[str, Any]:
        """
        Build TensorRT engine from HuggingFace model.
        
        Returns:
            Engine build result
        """
        try:
            logger.info(f"Building TensorRT engine for {self.config.model_id}")
            
            # Check GPU requirements
            gpu_check = await self._check_gpu_requirements()
            if not gpu_check["compatible"]:
                return {
                    "success": False,
                    "error": f"GPU requirements not met: {', '.join(gpu_check['warnings'])}",
                    "gpu_check": gpu_check
                }
            
            # Create workspace
            self.workspace_dir = Path(tempfile.mkdtemp(prefix=f"tensorrt_{self.config.service_name}_"))
            logger.info(f"TensorRT workspace: {self.workspace_dir}")
            
            # Download HuggingFace model
            hf_model_path = await self._download_hf_model()
            
            # Convert to TensorRT engine
            engine_build_result = await self._build_tensorrt_engine(hf_model_path)
            
            if engine_build_result["success"]:
                self.engine_path = engine_build_result["engine_path"]
                self.service_info.update({
                    "engine_path": str(self.engine_path),
                    "build_time": engine_build_result["build_time"],
                    "status": "engine_built"
                })
                
                logger.info(f"TensorRT engine built successfully: {self.engine_path}")
                return {
                    "success": True,
                    "engine_path": str(self.engine_path),
                    "build_time": engine_build_result["build_time"],
                    "workspace": str(self.workspace_dir),
                    "gpu_info": gpu_check["selected_gpu"]
                }
            else:
                return engine_build_result
                
        except Exception as e:
            logger.error(f"Failed to build TensorRT engine: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def load_model(self) -> Dict[str, Any]:
        """
        Load TensorRT engine for inference.
        
        Returns:
            Model loading result
        """
        if self.model_loaded:
            return {
                "success": True,
                "message": "Model already loaded"
            }
        
        if not self.engine_path or not self.engine_path.exists():
            return {
                "success": False,
                "error": "TensorRT engine not found. Build engine first."
            }
        
        try:
            logger.info(f"Loading TensorRT engine: {self.engine_path}")
            self.startup_time = datetime.now()
            
            # Import TensorRT-LLM (lazy loading)
            await self._import_tensorrt_llm()
            
            # Load the engine
            load_result = await self._load_tensorrt_engine()
            
            if load_result["success"]:
                self.model_loaded = True
                self.service_info.update({
                    "status": "running",
                    "loaded_at": self.startup_time.isoformat(),
                    "load_time": load_result["load_time"]
                })
                
                logger.info(f"TensorRT model loaded successfully")
                return {
                    "success": True,
                    "service_info": self.service_info,
                    "load_time": load_result["load_time"]
                }
            else:
                return load_result
                
        except Exception as e:
            logger.error(f"Failed to load TensorRT model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def unload_model(self) -> Dict[str, Any]:
        """Unload TensorRT model"""
        try:
            if self.generation_session:
                del self.generation_session
                self.generation_session = None
            
            self.model_loaded = False
            self.service_info.update({
                "status": "stopped",
                "unloaded_at": datetime.now().isoformat()
            })
            
            # Free GPU memory
            if self.tensorrt_llm:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            logger.info("TensorRT model unloaded")
            return {
                "success": True,
                "service_info": self.service_info
            }
            
        except Exception as e:
            logger.error(f"Failed to unload TensorRT model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using TensorRT-LLM"""
        if not self.model_loaded:
            return {
                "success": False,
                "error": "Model not loaded"
            }
        
        try:
            start_time = time.time()
            
            # Prepare generation parameters
            max_tokens = kwargs.get("max_tokens", 512)
            temperature = kwargs.get("temperature", 0.7)
            top_p = kwargs.get("top_p", 0.9)
            top_k = kwargs.get("top_k", 50)
            
            # Tokenize input
            input_ids = await self._tokenize_input(prompt)
            
            # Generate with TensorRT-LLM
            output_ids = await self._generate_tensorrt(
                input_ids=input_ids,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k
            )
            
            # Decode output
            generated_text = await self._decode_output(output_ids, len(input_ids[0]))
            
            generation_time = time.time() - start_time
            
            return {
                "success": True,
                "text": generated_text,
                "model": self.config.model_id,
                "generation_time": generation_time,
                "input_tokens": len(input_ids[0]),
                "output_tokens": len(output_ids[0]) - len(input_ids[0]),
                "total_tokens": len(output_ids[0])
            }
            
        except Exception as e:
            logger.error(f"TensorRT generation failed: {e}")
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
            "engine_exists": self.engine_path.exists() if self.engine_path else False
        }
    
    async def cleanup(self) -> Dict[str, Any]:
        """Clean up workspace and temporary files"""
        try:
            # Unload model first
            await self.unload_model()
            
            # Clean up workspace
            if self.workspace_dir and self.workspace_dir.exists():
                shutil.rmtree(self.workspace_dir)
                logger.info(f"Cleaned up workspace: {self.workspace_dir}")
            
            return {
                "success": True,
                "message": "Cleanup completed"
            }
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _download_hf_model(self) -> Path:
        """Download HuggingFace model"""
        hf_model_path = self.workspace_dir / "hf_model"
        
        try:
            from huggingface_hub import snapshot_download
            
            logger.info(f"Downloading HF model: {self.config.model_id}")
            snapshot_download(
                repo_id=self.config.model_id,
                local_dir=str(hf_model_path),
                local_dir_use_symlinks=False,
                revision=self.config.revision
            )
            
            logger.info(f"Model downloaded to: {hf_model_path}")
            return hf_model_path
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise
    
    async def _build_tensorrt_engine(self, hf_model_path: Path) -> Dict[str, Any]:
        """Build TensorRT engine using trtllm-build"""
        try:
            engine_output_path = self.workspace_dir / "engines"
            engine_output_path.mkdir(exist_ok=True)
            
            logger.info("Building TensorRT engine...")
            start_time = time.time()
            
            # Prepare build command
            build_cmd = [
                "trtllm-build",
                "--checkpoint_dir", str(hf_model_path),
                "--output_dir", str(engine_output_path),
                "--gemm_plugin", self.config.model_precision,
                "--gpt_attention_plugin", self.config.model_precision,
                "--max_batch_size", str(self.config.max_batch_size),
                "--max_seq_len", str(self.config.max_model_len),
            ]
            
            # Add TensorRT-specific arguments
            tensorrt_args = self.config.tensorrt_args
            for key, value in tensorrt_args.items():
                if isinstance(value, bool):
                    if value:
                        build_cmd.append(f"--{key}")
                else:
                    build_cmd.extend([f"--{key}", str(value)])
            
            # Set environment
            env = os.environ.copy()
            if self.config.gpu_id is not None:
                env["CUDA_VISIBLE_DEVICES"] = str(self.config.gpu_id)
            
            # Run build command
            logger.info(f"TensorRT build command: {' '.join(build_cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *build_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                build_time = time.time() - start_time
                
                # Find the built engine
                engine_files = list(engine_output_path.glob("*.engine"))
                if engine_files:
                    engine_path = engine_files[0]
                else:
                    # Look for rank_0.engine or similar patterns
                    rank_engines = list(engine_output_path.glob("*rank_0*.engine"))
                    if rank_engines:
                        engine_path = rank_engines[0]
                    else:
                        engine_path = engine_output_path / "model.engine"
                
                logger.info(f"TensorRT engine built in {build_time:.2f}s: {engine_path}")
                
                return {
                    "success": True,
                    "engine_path": engine_path,
                    "build_time": build_time,
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else ""
                }
            else:
                error_msg = stderr.decode() if stderr else "Unknown build error"
                logger.error(f"TensorRT build failed: {error_msg}")
                
                return {
                    "success": False,
                    "error": f"TensorRT build failed: {error_msg}",
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else ""
                }
                
        except Exception as e:
            logger.error(f"TensorRT build error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _import_tensorrt_llm(self):
        """Import TensorRT-LLM modules"""
        try:
            import tensorrt_llm
            from tensorrt_llm.runtime import ModelConfig, SamplingConfig
            from tensorrt_llm.runtime.generation import GenerationSession
            
            self.tensorrt_llm = tensorrt_llm
            self.ModelConfig = ModelConfig
            self.SamplingConfig = SamplingConfig
            self.GenerationSession = GenerationSession
            
            logger.info("TensorRT-LLM modules imported successfully")
            
        except ImportError as e:
            raise ImportError(f"TensorRT-LLM not installed: {e}")
    
    async def _load_tensorrt_engine(self) -> Dict[str, Any]:
        """Load TensorRT engine for inference"""
        try:
            start_time = time.time()
            
            # Configure runtime mapping
            from tensorrt_llm.runtime import ModelConfig
            from tensorrt_llm.runtime.generation import GenerationSession
            
            # Load model configuration
            config_path = self.engine_path.parent / "config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    model_config_dict = json.load(f)
                model_config = ModelConfig.from_dict(model_config_dict)
            else:
                # Create default config
                model_config = ModelConfig(
                    max_batch_size=self.config.max_batch_size,
                    max_input_len=self.config.max_model_len // 2,
                    max_output_len=self.config.max_model_len // 2,
                    max_beam_width=1,
                    vocab_size=50000,  # Default, will be updated from tokenizer
                    num_heads=32,
                    num_kv_heads=32,
                    hidden_size=4096,
                    gpt_attention_plugin=True,
                    remove_input_padding=True
                )
            
            # Create generation session
            self.generation_session = GenerationSession(
                model_config=model_config,
                engine_dir=str(self.engine_path.parent),
                runtime_mapping=None  # Single GPU
            )
            
            load_time = time.time() - start_time
            
            return {
                "success": True,
                "load_time": load_time
            }
            
        except Exception as e:
            logger.error(f"Failed to load TensorRT engine: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _tokenize_input(self, text: str) -> List[List[int]]:
        """Tokenize input text"""
        try:
            from transformers import AutoTokenizer
            
            # Load tokenizer
            if not hasattr(self, '_tokenizer'):
                self._tokenizer = AutoTokenizer.from_pretrained(
                    self.config.model_id,
                    revision=self.config.tokenizer_revision,
                    trust_remote_code=self.config.trust_remote_code
                )
            
            # Tokenize
            encoded = self._tokenizer.encode(text, return_tensors="pt")
            return [encoded[0].tolist()]
            
        except Exception as e:
            logger.error(f"Tokenization failed: {e}")
            raise
    
    async def _generate_tensorrt(self, input_ids: List[List[int]], 
                                max_tokens: int, temperature: float,
                                top_p: float, top_k: int) -> List[List[int]]:
        """Generate using TensorRT-LLM"""
        try:
            import torch
            from tensorrt_llm.runtime import SamplingConfig
            
            # Prepare inputs
            batch_size = len(input_ids)
            input_lengths = [len(seq) for seq in input_ids]
            max_input_length = max(input_lengths)
            
            # Pad sequences
            padded_ids = []
            for seq in input_ids:
                padded = seq + [0] * (max_input_length - len(seq))
                padded_ids.append(padded)
            
            input_ids_tensor = torch.tensor(padded_ids, dtype=torch.int32).cuda()
            input_lengths_tensor = torch.tensor(input_lengths, dtype=torch.int32).cuda()
            
            # Configure sampling
            sampling_config = SamplingConfig(
                end_id=self._tokenizer.eos_token_id,
                pad_id=self._tokenizer.pad_token_id or self._tokenizer.eos_token_id,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                num_beams=1,
                length_penalty=1.0
            )
            
            # Generate
            output_ids = self.generation_session.decode(
                input_ids=input_ids_tensor,
                input_lengths=input_lengths_tensor,
                sampling_config=sampling_config,
                max_new_tokens=max_tokens
            )
            
            return output_ids.cpu().numpy().tolist()
            
        except Exception as e:
            logger.error(f"TensorRT generation failed: {e}")
            raise
    
    async def _decode_output(self, output_ids: List[List[int]], input_length: int) -> str:
        """Decode generated tokens to text"""
        try:
            # Extract only the generated part
            generated_ids = output_ids[0][input_length:]
            
            # Decode
            generated_text = self._tokenizer.decode(
                generated_ids, 
                skip_special_tokens=True
            )
            
            return generated_text.strip()
            
        except Exception as e:
            logger.error(f"Decoding failed: {e}")
            raise
    
    async def _check_gpu_requirements(self) -> Dict[str, Any]:
        """Check GPU requirements for TensorRT-LLM"""
        self.gpu_manager.refresh()
        
        if not self.gpu_manager.cuda_available:
            return {
                "compatible": False,
                "warnings": ["CUDA not available"],
                "selected_gpu": None
            }
        
        # TensorRT-LLM requires more memory due to engine optimization
        estimated_memory = self.gpu_manager.estimate_model_memory(
            self.config.model_id, 
            self.config.model_precision
        )
        # Add 50% overhead for TensorRT optimizations
        estimated_memory = int(estimated_memory * 1.5)
        
        # Find suitable GPU
        if self.config.gpu_id is not None:
            selected_gpu = self.gpu_manager.get_gpu_info(self.config.gpu_id)
            if not selected_gpu:
                return {
                    "compatible": False,
                    "warnings": [f"Specified GPU {self.config.gpu_id} not found"],
                    "selected_gpu": None
                }
        else:
            selected_gpu = self.gpu_manager.get_best_gpu(estimated_memory)
            if selected_gpu:
                self.config.gpu_id = selected_gpu.gpu_id
        
        if not selected_gpu:
            return {
                "compatible": False,
                "warnings": [
                    f"No suitable GPU found. Required: {estimated_memory}MB (TensorRT overhead included), "
                    f"Available: {max(gpu.memory_free for gpu in self.gpu_manager.gpus) if self.gpu_manager.gpus else 0}MB"
                ],
                "selected_gpu": None
            }
        
        warnings = []
        
        # Check memory requirements (TensorRT needs more memory)
        if selected_gpu.memory_free < estimated_memory:
            warnings.append(f"GPU memory may be insufficient for TensorRT: {selected_gpu.memory_free}MB available, {estimated_memory}MB required")
        
        # Check compute capability for TensorRT
        if selected_gpu.name and "RTX" not in selected_gpu.name and "Tesla" not in selected_gpu.name:
            warnings.append("TensorRT-LLM works best with RTX/Tesla GPUs")
        
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
            "workspace_dir": str(self.workspace_dir) if self.workspace_dir else None,
            "engine_path": str(self.engine_path) if self.engine_path else None,
            "model_loaded": self.model_loaded,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None
        }