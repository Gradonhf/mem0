"""
Configuration Manager for OpenMemory

This module provides a centralized configuration management system that:
1. Loads default configuration from JSON files
2. Overrides with environment-specific configurations
3. Applies environment variable overrides
4. Validates required configuration values
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigManager:
    """Manages application configuration with environment variable support."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._config: Optional[Dict[str, Any]] = None
        
    def load_config(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration with environment-specific overrides.
        
        Args:
            environment: Environment name (development, docker, production)
            
        Returns:
            Merged configuration dictionary
        """
        # Load default configuration
        config = self._load_json_file("default.json")
        
        # Load environment-specific configuration if specified
        if environment and environment != "production":
            env_config = self._load_json_file(f"{environment}.json")
            config = self._merge_configs(config, env_config)
        
        # Apply environment variable overrides
        config = self._apply_env_overrides(config)
        
        # Validate required configuration
        self._validate_config(config)
        
        self._config = config
        return config
    
    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """Load JSON configuration file."""
        file_path = self.config_dir / filename
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file {filename}: {e}")
            return {}
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        # Database URL
        if db_url := os.getenv("DATABASE_URL"):
            config["database"]["url"] = db_url
        
        # API configuration
        if api_host := os.getenv("API_HOST"):
            config["api"]["host"] = api_host
        if api_port := os.getenv("API_PORT"):
            config["api"]["port"] = int(api_port)
        
        # Vector store configuration
        if qdrant_host := os.getenv("QDRANT_HOST"):
            config["vector_store"]["host"] = qdrant_host
        if qdrant_port := os.getenv("QDRANT_PORT"):
            config["vector_store"]["port"] = int(qdrant_port)
        
        # LLM configuration
        if openai_key := os.getenv("OPENAI_API_KEY"):
            config["llm"]["api_key"] = openai_key
        if llm_model := os.getenv("LLM_MODEL"):
            config["llm"]["model"] = llm_model
        
        # Embedder configuration
        if embedder_model := os.getenv("EMBEDDER_MODEL"):
            config["embedder"]["model"] = embedder_model
        
        # User configuration
        if user_id := os.getenv("USER_ID"):
            config["user"]["default_id"] = user_id
        
        # UI configuration
        if api_url := os.getenv("NEXT_PUBLIC_API_URL"):
            config["ui"]["api_url"] = api_url
        
        return config
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate required configuration values."""
        required_keys = [
            ("database", "url"),
            ("llm", "provider"),
            ("embedder", "provider"),
            ("user", "default_id"),
        ]
        
        missing_keys = []
        for section, key in required_keys:
            if section not in config or key not in config[section]:
                missing_keys.append(f"{section}.{key}")
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot notation path."""
        if self._config is None:
            self.load_config()
        
        keys = key_path.split(".")
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_mem0_config(self) -> Dict[str, Any]:
        """Get configuration in mem0 format."""
        if self._config is None:
            self.load_config()
        
        return {
            "mem0": {
                "vector_store": {
                    "provider": self.get("vector_store.provider"),
                    "config": {
                        "collection_name": self.get("vector_store.collection_name"),
                        "host": self.get("vector_store.host"),
                        "port": self.get("vector_store.port"),
                        "embedding_model_dims": self.get("vector_store.embedding_model_dims")
                    }
                },
                "llm": {
                    "provider": self.get("llm.provider"),
                    "config": {
                        "model": self.get("llm.model"),
                        "temperature": self.get("llm.temperature"),
                        "max_tokens": self.get("llm.max_tokens"),
                        "api_key": self.get("llm.api_key", "env:OPENAI_API_KEY")
                    }
                },
                "embedder": {
                    "provider": self.get("embedder.provider"),
                    "config": {
                        "model": self.get("embedder.model"),
                        "api_key": self.get("embedder.api_key", "env:OPENAI_API_KEY")
                    }
                }
            }
        }

# Global configuration manager instance
config_manager = ConfigManager() 