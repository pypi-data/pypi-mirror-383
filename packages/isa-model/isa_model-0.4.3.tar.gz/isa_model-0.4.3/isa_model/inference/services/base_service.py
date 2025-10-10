from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, AsyncGenerator, TypeVar, Optional
from ...core.models.model_manager import ModelManager
from ...core.config.config_manager import ConfigManager
from ...core.types import Provider, ServiceType

T = TypeVar('T')  # Generic type for responses

class BaseService(ABC):
    """Base class for all AI services - now uses centralized managers"""
    
    def __init__(self, 
                 provider_name: str, 
                 model_name: str, 
                 model_manager: Optional[ModelManager] = None,
                 config_manager: Optional[ConfigManager] = None):
        self.provider_name = provider_name
        self.model_name = model_name
        self.model_manager = model_manager or ModelManager()
        self.config_manager = config_manager or ConfigManager()
        
        # Validate provider is configured
        if not self.config_manager.is_provider_enabled(provider_name):
            raise ValueError(f"Provider {provider_name} is not configured or enabled")
    
    def get_api_key(self) -> str:
        """Get API key for the provider"""
        api_key = self.config_manager.get_provider_api_key(self.provider_name)
        if not api_key:
            raise ValueError(f"No API key configured for provider {self.provider_name}")
        return api_key
    
    def get_provider_config(self) -> Dict[str, Any]:
        """Get provider configuration"""
        config = self.config_manager.get_provider_config(self.provider_name)
        if not config:
            return {}
        
        return {
            "api_key": config.api_key,
            "api_base_url": config.api_base_url,
            "organization": config.organization,
            "rate_limit_rpm": config.rate_limit_rpm,
            "rate_limit_tpm": config.rate_limit_tpm,
        }
        
    async def _track_usage(
        self,
        service_type: Union[str, ServiceType],
        operation: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        input_units: Optional[float] = None,
        output_units: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track usage for billing purposes using centralized billing tracker"""
        try:
            # Calculate cost using centralized pricing
            cost_usd = None
            if input_tokens is not None and output_tokens is not None:
                cost_usd = self.model_manager.calculate_cost(
                    provider=self.provider_name,
                    model_name=self.model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens
                )
            
            # Track usage through both systems (legacy and new)
            # Legacy detailed tracking (will be phased out)
            self.model_manager.billing_tracker.track_model_usage(
                model_id=self.model_name,
                operation_type="inference",
                provider=self.provider_name,
                service_type=service_type if isinstance(service_type, str) else service_type.value,
                operation=operation,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_units=input_units,
                output_units=output_units,
                cost_usd=cost_usd,
                metadata=metadata
            )
            
            # New aggregated statistics tracking
            self.model_manager.statistics_tracker.track_usage(
                model_id=self.model_name,
                provider=self.provider_name,
                service_type=service_type if isinstance(service_type, str) else service_type.value,
                operation_type="inference",
                operation=operation,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_units=input_units,
                output_units=output_units,
                cost_usd=cost_usd or 0.0,
                metadata=metadata
            )
        except Exception as e:
            # Don't let billing tracking break the service
            import logging
            logging.getLogger(__name__).warning(f"Failed to track usage: {e}")
        
    def __await__(self):
        """Make the service awaitable"""
        yield
        return self

class BaseEmbeddingService(BaseService):
    """Base class for embedding services"""
    
    @abstractmethod
    async def create_text_embedding(self, text: str) -> List[float]:
        """Create embedding for single text"""
        pass
    
    @abstractmethod
    async def create_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        pass
    
    @abstractmethod
    async def create_chunks(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """Create text chunks with embeddings"""
        pass
    
    @abstractmethod
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute similarity between two embeddings"""
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass

class BaseRerankService(BaseService):
    """Base class for reranking services"""
    
    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:
        """Rerank documents based on query relevance"""
        pass
    
    @abstractmethod
    async def rerank_texts(
        self,
        query: str,
        texts: List[str]
    ) -> List[Dict]:
        """Rerank raw texts based on query relevance"""
        pass
