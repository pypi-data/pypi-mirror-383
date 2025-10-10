"""
isA_Model - A simple interface for AI model integration

Main Components:
- ISAModelClient: Unified client with intelligent model selection
- AIFactory: Legacy factory pattern (still supported)
"""

__version__ = "0.3.91"

# Main unified client interface
from isa_model.client import ISAModelClient, create_client

# Legacy support - still available for backward compatibility
from isa_model.inference.ai_factory import AIFactory

# Core components for advanced usage
try:
    from isa_model.core.models.model_manager import ModelManager
    from isa_model.core.config import ConfigManager
    _core_available = True
except ImportError:
    ModelManager = None
    ConfigManager = None
    _core_available = False

__all__ = [
    "ISAModelClient",
    "create_client", 
    "AIFactory"
]

if _core_available:
    __all__.extend(["ModelManager", "ConfigManager"])
