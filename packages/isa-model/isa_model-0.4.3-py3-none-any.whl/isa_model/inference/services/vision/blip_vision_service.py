#!/usr/bin/env python3
"""
BLIP Vision Service
Computer vision service using BLIP for image captioning and description
Based on the notebook implementation
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union, BinaryIO
from PIL import Image
import io

from .base_vision_service import BaseVisionService

logger = logging.getLogger(__name__)

def _lazy_import_blip_deps():
    """Lazy import BLIP dependencies"""
    try:
        import torch
        import tensorflow as tf
        from transformers import BlipProcessor, BlipForConditionalGeneration
        
        return {
            'torch': torch,
            'tf': tf,
            'BlipProcessor': BlipProcessor,
            'BlipForConditionalGeneration': BlipForConditionalGeneration,
            'available': True
        }
    except ImportError as e:
        logger.warning(f"BLIP dependencies not available: {e}")
        return {'available': False}

class BLIPVisionService(BaseVisionService):
    """
    BLIP-based vision service for image captioning and description
    Provides an alternative implementation to VLM-based captioning
    """
    
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base"):
        """
        Initialize BLIP vision service
        
        Args:
            model_name: Hugging Face model name for BLIP
        """
        super().__init__()
        
        self.model_name = model_name
        self.processor = None
        self.model = None
        
        # Lazy load dependencies
        self.blip_components = _lazy_import_blip_deps()
        
        if not self.blip_components['available']:
            raise ImportError("BLIP dependencies (transformers, torch) are required")
        
        # Load BLIP model
        self._load_blip_model()
    
    def _load_blip_model(self):
        """Load BLIP model and processor"""
        try:
            # Load the pretrained BLIP processor and model
            self.processor = self.blip_components['BlipProcessor'].from_pretrained(self.model_name)
            self.model = self.blip_components['BlipForConditionalGeneration'].from_pretrained(self.model_name)
            
            logger.info(f"BLIP model loaded: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error loading BLIP model: {e}")
            raise
    
    def _preprocess_image(self, image: Union[str, BinaryIO]) -> Image.Image:
        """
        Preprocess image for BLIP input
        
        Args:
            image: Image path or binary data
            
        Returns:
            PIL Image in RGB format
        """
        try:
            # Handle different image input types
            if isinstance(image, str):
                # File path
                pil_image = Image.open(image).convert('RGB')
            elif hasattr(image, 'read'):
                # Binary IO
                image_data = image.read()
                pil_image = Image.open(io.BytesIO(image_data)).convert('RGB')
            else:
                raise ValueError("Unsupported image format")
            
            return pil_image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise
    
    def _generate_text(self, image: Image.Image, prompt: str) -> str:
        """
        Generate text for image using BLIP
        
        Args:
            image: PIL Image
            prompt: Text prompt for generation
            
        Returns:
            Generated text
        """
        try:
            # Prepare inputs for BLIP model
            inputs = self.processor(images=image, text=prompt, return_tensors="pt")
            
            # Generate text output
            output = self.model.generate(**inputs)
            
            # Decode output
            result = self.processor.decode(output[0], skip_special_tokens=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    async def describe_image(self, 
                           image: Union[str, BinaryIO], 
                           detail_level: str = "medium") -> Dict[str, Any]:
        """
        Generate description for image using BLIP
        
        Args:
            image: Image path or binary data
            detail_level: Level of detail (not used in BLIP, maintained for compatibility)
            
        Returns:
            Description results
        """
        try:
            # Preprocess image
            pil_image = self._preprocess_image(image)
            
            # Generate caption using BLIP
            prompt = "This is a picture of"  # Following notebook implementation
            caption = self._generate_text(pil_image, prompt)
            
            return {
                "task": "describe",
                "service": "BLIPVisionService",
                "description": caption,
                "detail_level": detail_level,
                "model_type": "BLIP",
                "prompt_used": prompt,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            return {
                "error": str(e),
                "service": "BLIPVisionService",
                "success": False
            }
    
    async def analyze_image(self, 
                          image: Union[str, BinaryIO], 
                          prompt: Optional[str] = None,
                          max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Analyze image using BLIP
        
        Args:
            image: Image path or binary data
            prompt: Optional custom prompt
            max_tokens: Not used for BLIP
            
        Returns:
            Analysis results
        """
        try:
            # Preprocess image
            pil_image = self._preprocess_image(image)
            
            # Use custom prompt or default
            if prompt:
                analysis_prompt = prompt
            else:
                analysis_prompt = "This is a detailed photo showing"  # For summary-like analysis
            
            # Generate analysis using BLIP
            analysis_text = self._generate_text(pil_image, analysis_prompt)
            
            return {
                "task": "analyze",
                "service": "BLIPVisionService",
                "text": analysis_text,
                "model_type": "BLIP",
                "prompt_used": analysis_prompt,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "error": str(e),
                "service": "BLIPVisionService",
                "success": False
            }
    
    async def generate_caption(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """
        Generate caption for image (Task 9 from notebook)
        
        Args:
            image: Image path or binary data
            
        Returns:
            Caption results
        """
        try:
            # Preprocess image
            pil_image = self._preprocess_image(image)
            
            # Generate caption
            prompt = "This is a picture of"  # Following notebook
            caption = self._generate_text(pil_image, prompt)
            
            return {
                "task": "caption",
                "service": "BLIPVisionService",
                "caption": caption,
                "model_type": "BLIP",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            return {
                "error": str(e),
                "service": "BLIPVisionService",
                "success": False
            }
    
    async def generate_summary(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """
        Generate summary for image (Task 10 from notebook)
        
        Args:
            image: Image path or binary data
            
        Returns:
            Summary results
        """
        try:
            # Preprocess image
            pil_image = self._preprocess_image(image)
            
            # Generate summary
            prompt = "This is a detailed photo showing"  # Following notebook
            summary = self._generate_text(pil_image, prompt)
            
            return {
                "task": "summary",
                "service": "BLIPVisionService",
                "summary": summary,
                "model_type": "BLIP",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "error": str(e),
                "service": "BLIPVisionService",
                "success": False
            }
    
    async def batch_generate(self, 
                           images: List[Union[str, BinaryIO]], 
                           task: str = "caption") -> Dict[str, Any]:
        """
        Generate captions or summaries for multiple images
        
        Args:
            images: List of image paths or binary data
            task: Task type ("caption" or "summary")
            
        Returns:
            Batch generation results
        """
        try:
            results = []
            errors = []
            
            for i, image in enumerate(images):
                try:
                    if task == "caption":
                        result = await self.generate_caption(image)
                    elif task == "summary":
                        result = await self.generate_summary(image)
                    else:
                        raise ValueError(f"Unsupported task: {task}")
                    
                    if result.get("success"):
                        results.append({
                            "index": i,
                            "image": str(image) if isinstance(image, str) else f"binary_image_{i}",
                            **result
                        })
                    else:
                        errors.append({
                            "index": i,
                            "image": str(image) if isinstance(image, str) else f"binary_image_{i}",
                            "error": result.get("error", "Unknown error")
                        })
                        
                except Exception as e:
                    errors.append({
                        "index": i,
                        "image": str(image) if isinstance(image, str) else f"binary_image_{i}",
                        "error": str(e)
                    })
            
            return {
                "task": f"batch_{task}",
                "service": "BLIPVisionService",
                "total_images": len(images),
                "successful": len(results),
                "failed": len(errors),
                "results": results,
                "errors": errors,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in batch generation: {e}")
            return {
                "error": str(e),
                "service": "BLIPVisionService",
                "success": False
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            "service_name": "BLIPVisionService",
            "model_name": self.model_name,
            "model_type": "BLIP",
            "capabilities": ["describe", "analyze", "caption", "summary", "batch_generate"],
            "model_loaded": self.model is not None,
            "processor_loaded": self.processor is not None,
            "dependencies_available": self.blip_components['available']
        }