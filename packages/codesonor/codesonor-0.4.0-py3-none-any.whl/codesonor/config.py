"""Configuration management for CodeSonor."""

import os
import json
from pathlib import Path
from typing import Optional


class Config:
    """Manages CodeSonor configuration and API keys."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / '.codesonor'
        self.config_file = self.config_dir / 'config.json'
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(exist_ok=True)
    
    def save_config(
        self, 
        github_token: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        llm_model: Optional[str] = None,
        # Legacy support
        gemini_key: Optional[str] = None
    ):
        """
        Save API keys and LLM configuration to config file.
        
        Args:
            github_token: GitHub Personal Access Token
            llm_provider: LLM provider name (gemini, openai, anthropic, mistral, groq)
            llm_api_key: API key for the LLM provider
            llm_model: Optional model name override
            gemini_key: (Legacy) Google Gemini API Key - converts to llm_api_key with gemini provider
        """
        config = self.load_config()
        
        if github_token is not None:
            config['github_token'] = github_token
        
        # Handle legacy gemini_key parameter
        if gemini_key is not None:
            config['llm_provider'] = 'gemini'
            config['llm_api_key'] = gemini_key
        
        if llm_provider is not None:
            config['llm_provider'] = llm_provider.lower()
        
        if llm_api_key is not None:
            config['llm_api_key'] = llm_api_key
        
        if llm_model is not None:
            config['llm_model'] = llm_model
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self) -> dict:
        """
        Load configuration from file.
        
        Returns:
            Dictionary containing configuration
        """
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def get_github_token(self) -> Optional[str]:
        """
        Get GitHub token from config or environment.
        
        Priority: Environment variable > Config file
        
        Returns:
            GitHub token or None
        """
        # Check environment first
        token = os.getenv('GITHUB_TOKEN')
        if token:
            return token
        
        # Check config file
        config = self.load_config()
        return config.get('github_token')
    
    def get_llm_provider(self) -> str:
        """
        Get LLM provider name from config.
        
        Returns:
            LLM provider name (default: 'gemini')
        """
        config = self.load_config()
        # Check for new format first
        provider = config.get('llm_provider')
        if provider:
            return provider
        
        # Legacy: if gemini_key exists, return gemini
        if config.get('gemini_key'):
            return 'gemini'
        
        return 'gemini'  # default
    
    def get_llm_api_key(self) -> Optional[str]:
        """
        Get LLM API key from config or environment.
        
        Priority: Environment variable > Config file
        
        Returns:
            LLM API key or None
        """
        config = self.load_config()
        provider = self.get_llm_provider()
        
        # Check provider-specific environment variable first
        env_var_map = {
            'gemini': 'GEMINI_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'mistral': 'MISTRAL_API_KEY',
            'groq': 'GROQ_API_KEY'
        }
        
        env_var = env_var_map.get(provider)
        if env_var:
            key = os.getenv(env_var)
            if key:
                return key
        
        # Check new config format
        key = config.get('llm_api_key')
        if key:
            return key
        
        # Legacy: check gemini_key for backwards compatibility
        if provider == 'gemini':
            return config.get('gemini_key')
        
        return None
    
    def get_llm_model(self) -> Optional[str]:
        """
        Get LLM model name from config.
        
        Returns:
            Model name or None (will use provider default)
        """
        config = self.load_config()
        return config.get('llm_model')
    
    def get_gemini_key(self) -> Optional[str]:
        """
        Get Gemini API key from config or environment.
        
        DEPRECATED: Use get_llm_api_key() instead.
        Kept for backwards compatibility.
        
        Priority: Environment variable > Config file
        
        Returns:
            Gemini API key or None
        """
        # Check environment first
        key = os.getenv('GEMINI_API_KEY')
        if key:
            return key
        
        # Check config file
        config = self.load_config()
        # Check both old and new formats
        return config.get('llm_api_key') or config.get('gemini_key')
    
    def clear_config(self):
        """Clear all stored configuration."""
        if self.config_file.exists():
            self.config_file.unlink()
    
    def get_config_status(self) -> dict:
        """
        Get current configuration status.
        
        Returns:
            Dictionary with status of each configuration item
        """
        github_env = bool(os.getenv('GITHUB_TOKEN'))
        
        config = self.load_config()
        github_config = bool(config.get('github_token'))
        
        # LLM configuration
        llm_provider = self.get_llm_provider()
        llm_api_key = self.get_llm_api_key()
        llm_model = self.get_llm_model()
        
        # Determine source of LLM API key
        llm_source = None
        if llm_api_key:
            env_var_map = {
                'gemini': 'GEMINI_API_KEY',
                'openai': 'OPENAI_API_KEY',
                'anthropic': 'ANTHROPIC_API_KEY',
                'mistral': 'MISTRAL_API_KEY',
                'groq': 'GROQ_API_KEY'
            }
            env_var = env_var_map.get(llm_provider)
            if env_var and os.getenv(env_var):
                llm_source = 'environment'
            else:
                llm_source = 'config'
        
        return {
            'github_token': {
                'set': github_env or github_config,
                'source': 'environment' if github_env else ('config' if github_config else None)
            },
            'llm_provider': llm_provider,
            'llm_api_key': {
                'set': bool(llm_api_key),
                'source': llm_source
            },
            'llm_model': llm_model,
            'config_file': str(self.config_file)
        }
