"""
CodeSonor - AI-Powered GitHub Repository Analyzer

A powerful tool for analyzing GitHub repositories with AI-generated insights.
Supports multiple LLM providers: Gemini, OpenAI, Claude, Mistral, and Groq.

New in v0.4.0:
- Repository comparison
- Intelligent caching
- Code quality scoring
- Export to JSON/HTML/Markdown
- Watch mode for continuous monitoring
- Custom rules engine
- Language-specific deep insights
- Interactive dashboard
"""

__version__ = "0.4.0"
__author__ = "Farhan Mir"
__email__ = "your.email@example.com"

from .analyzer import RepositoryAnalyzer
from .github_client import GitHubClient
from .language_stats import LanguageAnalyzer

__all__ = ["RepositoryAnalyzer", "GitHubClient", "LanguageAnalyzer"]
