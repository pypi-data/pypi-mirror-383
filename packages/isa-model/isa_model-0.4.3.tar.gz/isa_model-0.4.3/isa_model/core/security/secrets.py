"""
Secrets Management System

Provides secure handling of API keys, tokens, and other sensitive data.
Supports multiple backends: environment variables, HashiCorp Vault, AWS Secrets Manager.
"""

import os
import json
import logging
import hashlib
import base64
from typing import Dict, Optional, Any, List
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import structlog

logger = structlog.get_logger(__name__)

class SecretsManager:
    """Unified secrets management with multiple backend support"""
    
    def __init__(self, backend: str = "env", **kwargs):
        self.backend = backend
        self.config = kwargs
        self._cache = {}
        self._encryption_key = None
        
        # Initialize encryption key for local storage
        self._init_encryption()
        
        # Initialize backend
        if backend == "vault":
            self._init_vault()
        elif backend == "aws":
            self._init_aws()
        elif backend == "env":
            self._init_env()
        else:
            raise ValueError(f"Unsupported secrets backend: {backend}")
        
        logger.info("Secrets manager initialized", backend=backend)
    
    def _init_encryption(self):
        """Initialize encryption for local secret storage"""
        # Use a combination of environment and system info for key derivation
        password = os.getenv("SECRET_ENCRYPTION_KEY", "default-key-change-in-production").encode()
        salt = os.getenv("SECRET_SALT", "default-salt").encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self._encryption_key = Fernet(key)
    
    def _init_env(self):
        """Initialize environment variable backend"""
        logger.info("Using environment variables for secrets")
    
    def _init_vault(self):
        """Initialize HashiCorp Vault backend"""
        try:
            import hvac
            
            vault_url = self.config.get("vault_url", os.getenv("VAULT_URL"))
            vault_token = self.config.get("vault_token", os.getenv("VAULT_TOKEN"))
            
            if not vault_url:
                raise ValueError("VAULT_URL required for Vault backend")
            
            self.vault_client = hvac.Client(url=vault_url, token=vault_token)
            
            if not self.vault_client.is_authenticated():
                raise ValueError("Vault authentication failed")
            
            logger.info("Vault backend initialized", url=vault_url)
            
        except ImportError:
            raise ImportError("hvac package required for Vault backend: pip install hvac")
    
    def _init_aws(self):
        """Initialize AWS Secrets Manager backend"""
        try:
            import boto3
            
            region = self.config.get("region", os.getenv("AWS_REGION", "us-east-1"))
            self.secrets_client = boto3.client("secretsmanager", region_name=region)
            
            logger.info("AWS Secrets Manager backend initialized", region=region)
            
        except ImportError:
            raise ImportError("boto3 package required for AWS backend: pip install boto3")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret value by key"""
        # Check cache first
        if key in self._cache:
            return self._cache[key]
        
        try:
            if self.backend == "env":
                value = self._get_env_secret(key, default)
            elif self.backend == "vault":
                value = self._get_vault_secret(key, default)
            elif self.backend == "aws":
                value = self._get_aws_secret(key, default)
            else:
                value = default
            
            # Cache the value
            if value is not None:
                self._cache[key] = value
            
            return value
            
        except Exception as e:
            logger.error("Failed to retrieve secret", key=key, error=str(e))
            return default
    
    def _get_env_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment variables"""
        return os.getenv(key, default)
    
    def _get_vault_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from HashiCorp Vault"""
        try:
            secret_path = self.config.get("secret_path", "secret/data/isa-model")
            response = self.vault_client.secrets.kv.v2.read_secret_version(path=secret_path)
            data = response["data"]["data"]
            return data.get(key, default)
        except Exception as e:
            logger.warning("Failed to retrieve secret from Vault", key=key, error=str(e))
            return default
    
    def _get_aws_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from AWS Secrets Manager"""
        try:
            secret_name = self.config.get("secret_name", "isa-model/secrets")
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            secrets = json.loads(response["SecretString"])
            return secrets.get(key, default)
        except Exception as e:
            logger.warning("Failed to retrieve secret from AWS", key=key, error=str(e))
            return default
    
    def set_secret(self, key: str, value: str) -> bool:
        """Set a secret value (only supported for some backends)"""
        try:
            if self.backend == "vault":
                return self._set_vault_secret(key, value)
            elif self.backend == "aws":
                return self._set_aws_secret(key, value)
            else:
                logger.warning("Set operation not supported for backend", backend=self.backend)
                return False
        except Exception as e:
            logger.error("Failed to set secret", key=key, error=str(e))
            return False
    
    def _set_vault_secret(self, key: str, value: str) -> bool:
        """Set secret in HashiCorp Vault"""
        try:
            secret_path = self.config.get("secret_path", "secret/data/isa-model")
            # Get existing secrets first
            try:
                response = self.vault_client.secrets.kv.v2.read_secret_version(path=secret_path)
                existing_data = response["data"]["data"]
            except:
                existing_data = {}
            
            # Update with new secret
            existing_data[key] = value
            
            # Write back to vault
            self.vault_client.secrets.kv.v2.create_or_update_secret(
                path=secret_path,
                secret=existing_data
            )
            
            # Update cache
            self._cache[key] = value
            return True
            
        except Exception as e:
            logger.error("Failed to set secret in Vault", key=key, error=str(e))
            return False
    
    def _set_aws_secret(self, key: str, value: str) -> bool:
        """Set secret in AWS Secrets Manager"""
        try:
            secret_name = self.config.get("secret_name", "isa-model/secrets")
            
            # Get existing secrets
            try:
                response = self.secrets_client.get_secret_value(SecretId=secret_name)
                existing_secrets = json.loads(response["SecretString"])
            except:
                existing_secrets = {}
            
            # Update with new secret
            existing_secrets[key] = value
            
            # Update secret
            self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(existing_secrets)
            )
            
            # Update cache
            self._cache[key] = value
            return True
            
        except Exception as e:
            logger.error("Failed to set secret in AWS", key=key, error=str(e))
            return False
    
    def list_secrets(self) -> List[str]:
        """List available secret keys"""
        try:
            if self.backend == "vault":
                return self._list_vault_secrets()
            elif self.backend == "aws":
                return self._list_aws_secrets()
            elif self.backend == "env":
                # Return common secret environment variables
                common_secrets = [
                    "OPENAI_API_KEY", "REPLICATE_API_TOKEN", "ANTHROPIC_API_KEY",
                    "DATABASE_URL", "REDIS_URL", "ISA_API_KEY"
                ]
                return [key for key in common_secrets if os.getenv(key)]
            else:
                return []
        except Exception as e:
            logger.error("Failed to list secrets", error=str(e))
            return []
    
    def _list_vault_secrets(self) -> List[str]:
        """List secrets in HashiCorp Vault"""
        try:
            secret_path = self.config.get("secret_path", "secret/data/isa-model")
            response = self.vault_client.secrets.kv.v2.read_secret_version(path=secret_path)
            return list(response["data"]["data"].keys())
        except Exception as e:
            logger.warning("Failed to list Vault secrets", error=str(e))
            return []
    
    def _list_aws_secrets(self) -> List[str]:
        """List secrets in AWS Secrets Manager"""
        try:
            secret_name = self.config.get("secret_name", "isa-model/secrets")
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            secrets = json.loads(response["SecretString"])
            return list(secrets.keys())
        except Exception as e:
            logger.warning("Failed to list AWS secrets", error=str(e))
            return []
    
    def rotate_secret(self, key: str) -> bool:
        """Rotate a secret (implementation depends on secret type)"""
        # This is a placeholder for secret rotation logic
        logger.info("Secret rotation requested", key=key)
        # In production, this would implement proper rotation logic
        return True
    
    def clear_cache(self):
        """Clear the secrets cache"""
        self._cache.clear()
        logger.info("Secrets cache cleared")

# Global secrets manager instance
_secrets_manager = None

def get_secrets_manager() -> SecretsManager:
    """Get the global secrets manager instance"""
    global _secrets_manager
    
    if _secrets_manager is None:
        # Determine backend from environment
        backend = os.getenv("SECRETS_BACKEND", "env")
        
        # Initialize with backend-specific configuration
        if backend == "vault":
            _secrets_manager = SecretsManager(
                backend="vault",
                vault_url=os.getenv("VAULT_URL"),
                vault_token=os.getenv("VAULT_TOKEN"),
                secret_path=os.getenv("VAULT_SECRET_PATH", "secret/data/isa-model")
            )
        elif backend == "aws":
            _secrets_manager = SecretsManager(
                backend="aws",
                region=os.getenv("AWS_REGION", "us-east-1"),
                secret_name=os.getenv("AWS_SECRET_NAME", "isa-model/secrets")
            )
        else:
            _secrets_manager = SecretsManager(backend="env")
    
    return _secrets_manager

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Convenience function to get a secret"""
    return get_secrets_manager().get_secret(key, default)

def set_secret(key: str, value: str) -> bool:
    """Convenience function to set a secret"""
    return get_secrets_manager().set_secret(key, value)

# Predefined secret getters for common secrets
def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key"""
    return get_secret("OPENAI_API_KEY")

def get_replicate_api_token() -> Optional[str]:
    """Get Replicate API token"""
    return get_secret("REPLICATE_API_TOKEN")

def get_anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key"""
    return get_secret("ANTHROPIC_API_KEY")

def get_database_url() -> Optional[str]:
    """Get database URL"""
    return get_secret("DATABASE_URL")

def get_redis_url() -> Optional[str]:
    """Get Redis URL"""
    return get_secret("REDIS_URL", "redis://localhost:6379")

def get_isa_api_key() -> Optional[str]:
    """Get ISA API key"""
    return get_secret("ISA_API_KEY")

# Health check for secrets manager
async def check_secrets_health() -> Dict[str, Any]:
    """Check secrets manager health"""
    try:
        manager = get_secrets_manager()
        
        # Test basic functionality
        test_secret = manager.get_secret("HEALTH_CHECK_TEST", "test")
        
        return {
            "secrets_manager": "ok",
            "backend": manager.backend,
            "cached_secrets": len(manager._cache),
            "status": "healthy"
        }
    except Exception as e:
        return {
            "secrets_manager": "error",
            "status": "unhealthy",
            "error": str(e)
        }