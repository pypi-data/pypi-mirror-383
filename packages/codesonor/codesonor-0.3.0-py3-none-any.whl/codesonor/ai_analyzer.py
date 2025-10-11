"""AI-powered code analyzer with multi-provider support."""

import os
from typing import Optional, List, Dict
from .llm_providers import get_provider, LLMProvider, SUPPORTED_PROVIDERS


class AIAnalyzer:
    """AI-powered code analyzer supporting multiple LLM providers."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        provider: str = "gemini",
        model: Optional[str] = None
    ):
        """
        Initialize AI analyzer.
        
        Args:
            api_key: API key for the LLM provider
            provider: LLM provider name (gemini, openai, anthropic, mistral, groq)
            model: Optional model name override
        """
        self.provider_name = provider.lower()
        self.api_key = api_key
        self.model_name = model
        self.provider: Optional[LLMProvider] = None
        
        # Try to initialize the provider
        if self.api_key:
            try:
                self.provider = get_provider(self.provider_name, self.api_key, self.model_name)
            except Exception as e:
                print(f"Warning: Failed to initialize {self.provider_name}: {e}")
                self.provider = None
    
    def is_available(self) -> bool:
        """Check if AI analysis is available."""
        return self.provider is not None and self.provider.is_available()
    
    def get_provider_name(self) -> str:
        """Get the name of the current provider."""
        if self.provider:
            return self.provider.get_name()
        return "No provider configured"
    
    def generate_summary(self, code: str, filename: str) -> str:
        """
        Generate AI summary for code.
        
        Args:
            code: Source code content
            filename: Name of the file
            
        Returns:
            AI-generated summary or error message
        """
        if not self.is_available():
            return f"AI summary not available. Please configure API key for {self.provider_name}."
        
        try:
            prompt = f"""Analyze this code file named '{filename}' and provide:
1. A brief summary (2-3 sentences) of what this code does
2. The main purpose/functionality
3. Key components or classes (if any)

Code:
```
{code[:3000]}
```

Provide a concise, professional summary."""

            response = self.provider.generate(prompt)
            return response
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def analyze_key_files(self, files: List[Dict], github_client) -> List[Dict]:
        """
        Analyze key source code files with AI.
        
        Args:
            files: List of file dictionaries
            github_client: GitHubClient instance to fetch file content
            
        Returns:
            List of analysis results
        """
        if not self.is_available():
            return []
        
        priority_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.go', '.rb']
        
        # Filter and prioritize files
        key_files = []
        for file in files:
            ext = os.path.splitext(file['name'])[1].lower()
            if ext in priority_extensions and file['size'] < 50000:
                name_lower = file['name'].lower()
                if any(keyword in name_lower for keyword in ['main', 'index', 'app', 'server']):
                    key_files.insert(0, file)
                else:
                    key_files.append(file)
        
        # Analyze up to 3 key files
        analyses = []
        for file in key_files[:3]:
            if file.get('download_url'):
                content = github_client.get_file_content(file['download_url'])
                if content:
                    summary = self.generate_summary(content, file['name'])
                    analyses.append({
                        'file': file['path'],
                        'summary': summary
                    })
        
        return analyses
