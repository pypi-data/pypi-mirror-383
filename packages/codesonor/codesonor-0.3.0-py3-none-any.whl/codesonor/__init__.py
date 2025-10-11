"""
CodeSonor - AI-Powered GitHub Repository Analyzer

A powerful tool for analyzing GitHub repositories with AI-generated insights.
Supports multiple LLM providers: Gemini, OpenAI, Claude, Mistral, and Groq.
"""

__version__ = "0.3.0"
__author__ = "Farhan Mir"
__email__ = "your.email@example.com"

from .analyzer import RepositoryAnalyzer
from .github_client import GitHubClient
from .language_stats import LanguageAnalyzer

__all__ = ["RepositoryAnalyzer", "GitHubClient", "LanguageAnalyzer"]
