"""LLM provider implementations for multi-provider support."""

import os
from typing import Optional, Protocol
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get provider name."""
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini provider."""
        self.api_key = api_key
        self.model = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except ImportError:
                pass
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self.model is not None
    
    def generate(self, prompt: str) -> str:
        """Generate response using Gemini."""
        if not self.is_available():
            raise RuntimeError("Gemini provider not available")
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def get_name(self) -> str:
        """Get provider name."""
        return "Google Gemini"


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize OpenAI provider."""
        self.api_key = api_key
        self.model_name = model
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                pass
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.client is not None
    
    def generate(self, prompt: str) -> str:
        """Generate response using OpenAI."""
        if not self.is_available():
            raise RuntimeError("OpenAI provider not available")
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def get_name(self) -> str:
        """Get provider name."""
        return f"OpenAI ({self.model_name})"


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        """Initialize Anthropic provider."""
        self.api_key = api_key
        self.model_name = model
        self.client = None
        
        if self.api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
            except ImportError:
                pass
    
    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        return self.client is not None
    
    def generate(self, prompt: str) -> str:
        """Generate response using Claude."""
        if not self.is_available():
            raise RuntimeError("Anthropic provider not available")
        
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    def get_name(self) -> str:
        """Get provider name."""
        return f"Anthropic Claude ({self.model_name})"


class MistralProvider(LLMProvider):
    """Mistral AI provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-small-latest"):
        """Initialize Mistral provider."""
        self.api_key = api_key
        self.model_name = model
        self.client = None
        
        if self.api_key:
            try:
                from mistralai import Mistral
                self.client = Mistral(api_key=self.api_key)
            except ImportError:
                pass
    
    def is_available(self) -> bool:
        """Check if Mistral is available."""
        return self.client is not None
    
    def generate(self, prompt: str) -> str:
        """Generate response using Mistral."""
        if not self.is_available():
            raise RuntimeError("Mistral provider not available")
        
        response = self.client.chat.complete(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def get_name(self) -> str:
        """Get provider name."""
        return f"Mistral AI ({self.model_name})"


class GroqProvider(LLMProvider):
    """Groq fast inference provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mixtral-8x7b-32768"):
        """Initialize Groq provider."""
        self.api_key = api_key
        self.model_name = model
        self.client = None
        
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except ImportError:
                pass
    
    def is_available(self) -> bool:
        """Check if Groq is available."""
        return self.client is not None
    
    def generate(self, prompt: str) -> str:
        """Generate response using Groq."""
        if not self.is_available():
            raise RuntimeError("Groq provider not available")
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def get_name(self) -> str:
        """Get provider name."""
        return f"Groq ({self.model_name})"


def get_provider(provider_name: str, api_key: Optional[str] = None, model: Optional[str] = None) -> LLMProvider:
    """
    Factory function to get LLM provider.
    
    Args:
        provider_name: Name of provider (gemini, openai, anthropic, mistral, groq)
        api_key: API key for the provider
        model: Optional model name override
        
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider name is not supported
    """
    provider_name = provider_name.lower()
    
    if provider_name == "gemini":
        return GeminiProvider(api_key)
    elif provider_name == "openai":
        return OpenAIProvider(api_key, model or "gpt-3.5-turbo")
    elif provider_name == "anthropic":
        return AnthropicProvider(api_key, model or "claude-3-haiku-20240307")
    elif provider_name == "mistral":
        return MistralProvider(api_key, model or "mistral-small-latest")
    elif provider_name == "groq":
        return GroqProvider(api_key, model or "mixtral-8x7b-32768")
    else:
        raise ValueError(f"Unsupported provider: {provider_name}. Supported: gemini, openai, anthropic, mistral, groq")


# Supported providers and their default models
SUPPORTED_PROVIDERS = {
    "gemini": {
        "name": "Google Gemini",
        "models": ["gemini-1.5-flash", "gemini-1.5-pro"],
        "default": "gemini-1.5-flash",
        "requires": "google-generativeai"
    },
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        "default": "gpt-3.5-turbo",
        "requires": "openai"
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        "default": "claude-3-haiku-20240307",
        "requires": "anthropic"
    },
    "mistral": {
        "name": "Mistral AI",
        "models": ["mistral-large-latest", "mistral-small-latest"],
        "default": "mistral-small-latest",
        "requires": "mistralai"
    },
    "groq": {
        "name": "Groq",
        "models": ["mixtral-8x7b-32768", "llama3-70b-8192", "gemma-7b-it"],
        "default": "mixtral-8x7b-32768",
        "requires": "groq"
    }
}
