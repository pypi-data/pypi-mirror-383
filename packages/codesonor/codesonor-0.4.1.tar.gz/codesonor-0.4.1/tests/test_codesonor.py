"""Tests for CodeSonor package"""

import pytest
from codesonor.github_client import GitHubClient
from codesonor.language_stats import LanguageAnalyzer


class TestGitHubClient:
    """Tests for GitHub client functionality"""
    
    def test_parse_url_https(self):
        """Test parsing HTTPS GitHub URLs"""
        client = GitHubClient()
        
        # Test HTTPS URL
        owner, repo = client.parse_url("https://github.com/python/cpython")
        assert owner == "python"
        assert repo == "cpython"
        
        # Test with trailing slash and .git
        owner, repo = client.parse_url("https://github.com/python/cpython.git/")
        assert owner == "python"
        assert repo == "cpython"
    
    def test_parse_url_invalid(self):
        """Test parsing invalid URLs returns None"""
        client = GitHubClient()
        
        # Invalid URLs should return (None, None)
        owner, repo = client.parse_url("https://gitlab.com/user/repo")
        assert owner is None
        assert repo is None
        
        owner, repo = client.parse_url("not-a-url")
        assert owner is None
        assert repo is None


class TestLanguageAnalyzer:
    """Tests for language analysis functionality"""
    
    def test_language_extensions(self):
        """Test language extension mappings"""
        analyzer = LanguageAnalyzer()
        
        # Test various extensions
        assert analyzer.LANGUAGE_EXTENSIONS[".py"] == "Python"
        assert analyzer.LANGUAGE_EXTENSIONS[".js"] == "JavaScript"
        assert analyzer.LANGUAGE_EXTENSIONS[".java"] == "Java"
        assert analyzer.LANGUAGE_EXTENSIONS[".cpp"] == "C++"
    
    def test_calculate_stats(self):
        """Test language statistics calculation"""
        analyzer = LanguageAnalyzer()
        
        files = [
            {"name": "app.py", "path": "src/app.py", "size": 1000},
            {"name": "utils.py", "path": "src/utils.py", "size": 500},
            {"name": "script.js", "path": "static/script.js", "size": 300},
            {"name": "README.md", "path": "README.md", "size": 200},
        ]
        
        stats = analyzer.calculate_stats(files)
        
        assert "Python" in stats
        assert "JavaScript" in stats
        assert "Markdown" in stats
        # Python should be ~75% (1500/2000)
        assert stats["Python"] > 70
        assert stats["Python"] < 80
    
    def test_get_primary_language(self):
        """Test primary language detection"""
        analyzer = LanguageAnalyzer()
        
        files = [
            {"name": "main.py", "size": 1000},
            {"name": "test.py", "size": 500},
            {"name": "index.js", "size": 200},
        ]
        
        primary = analyzer.get_primary_language(files)
        assert primary == "Python"
    
    def test_filter_by_language(self):
        """Test filtering files by language"""
        analyzer = LanguageAnalyzer()
        
        files = [
            {"name": "app.py", "path": "src/app.py"},
            {"name": "utils.py", "path": "src/utils.py"},
            {"name": "script.js", "path": "static/script.js"},
        ]
        
        python_files = analyzer.filter_by_language(files, "Python")
        assert len(python_files) == 2
        assert all(f["name"].endswith(".py") for f in python_files)
        
        js_files = analyzer.filter_by_language(files, "JavaScript")
        assert len(js_files) == 1
        assert js_files[0]["name"] == "script.js"


class TestImports:
    """Test that all modules can be imported"""
    
    def test_import_github_client(self):
        """Test importing GitHubClient"""
        from codesonor import GitHubClient
        assert GitHubClient is not None
    
    def test_import_language_analyzer(self):
        """Test importing LanguageAnalyzer"""
        from codesonor import LanguageAnalyzer
        assert LanguageAnalyzer is not None
    
    def test_import_repository_analyzer(self):
        """Test importing RepositoryAnalyzer"""
        from codesonor import RepositoryAnalyzer
        assert RepositoryAnalyzer is not None
    
    def test_package_version(self):
        """Test that package has version"""
        import codesonor
        assert hasattr(codesonor, "__version__")
        assert codesonor.__version__ == "0.4.1"


class TestLLMProviders:
    """Tests for multi-LLM provider support"""
    
    def test_import_providers(self):
        """Test importing LLM providers module"""
        from codesonor.llm_providers import get_provider, SUPPORTED_PROVIDERS
        assert get_provider is not None
        assert SUPPORTED_PROVIDERS is not None
    
    def test_supported_providers(self):
        """Test that all expected providers are supported"""
        from codesonor.llm_providers import SUPPORTED_PROVIDERS
        
        expected_providers = ["gemini", "openai", "anthropic", "mistral", "groq", "openrouter", "xai", "ollama"]
        for provider in expected_providers:
            assert provider in SUPPORTED_PROVIDERS
            assert "name" in SUPPORTED_PROVIDERS[provider]
            assert "models" in SUPPORTED_PROVIDERS[provider]
            assert "default" in SUPPORTED_PROVIDERS[provider]
    
    def test_get_provider_factory(self):
        """Test provider factory function"""
        from codesonor.llm_providers import get_provider
        
        # Test creating providers (without API keys, they won't be available)
        providers_to_test = ["gemini", "openai", "anthropic", "mistral", "groq", "openrouter", "xai", "ollama"]
        
        for provider_name in providers_to_test:
            provider = get_provider(provider_name, api_key=None)
            assert provider is not None
            if provider_name != "ollama":  # Ollama might be available locally
                assert not provider.is_available()  # No API key, so not available
    
    def test_invalid_provider(self):
        """Test that invalid provider raises error"""
        from codesonor.llm_providers import get_provider
        
        with pytest.raises(ValueError) as exc_info:
            get_provider("invalid_provider")
        
        assert "Unsupported provider" in str(exc_info.value)
    
    def test_ai_analyzer_with_providers(self):
        """Test AIAnalyzer accepts different providers"""
        from codesonor.ai_analyzer import AIAnalyzer
        
        # Test with different providers (no API keys)
        for provider in ["gemini", "openai", "anthropic"]:
            analyzer = AIAnalyzer(api_key=None, provider=provider)
            assert analyzer.provider_name == provider
            assert not analyzer.is_available()
    
    def test_repository_analyzer_llm_params(self):
        """Test RepositoryAnalyzer accepts LLM parameters"""
        from codesonor.analyzer import RepositoryAnalyzer
        
        # Test with LLM provider parameters
        analyzer = RepositoryAnalyzer(
            github_token=None,
            gemini_key=None,
            llm_provider="openai",
            llm_model="gpt-4"
        )
        assert analyzer is not None
        assert analyzer.ai is not None


class TestNewFeaturesV040:
    """Tests for new features in v0.4.0"""
    
    def test_import_cache_manager(self):
        """Test importing CacheManager"""
        from codesonor.cache_manager import CacheManager
        assert CacheManager is not None
    
    def test_import_quality_scorer(self):
        """Test importing QualityScorer"""
        from codesonor.quality_scorer import QualityScorer
        assert QualityScorer is not None
    
    def test_import_exporter(self):
        """Test importing ExportManager"""
        from codesonor.exporter import ExportManager
        assert ExportManager is not None
    
    def test_import_comparator(self):
        """Test importing RepositoryComparator"""
        from codesonor.comparator import RepositoryComparator
        assert RepositoryComparator is not None
    
    def test_import_watcher(self):
        """Test importing WatchManager"""
        from codesonor.watcher import WatchManager
        assert WatchManager is not None
    
    def test_import_rules_engine(self):
        """Test importing RulesEngine"""
        from codesonor.rules_engine import RulesEngine, Rule
        assert RulesEngine is not None
        assert Rule is not None
    
    def test_import_language_insights(self):
        """Test importing LanguageInsights"""
        from codesonor.language_insights import LanguageInsights
        assert LanguageInsights is not None
    
    def test_import_dashboard(self):
        """Test importing Dashboard classes"""
        from codesonor.dashboard import InteractiveDashboard, DashboardSimple
        assert InteractiveDashboard is not None
        assert DashboardSimple is not None
    
    def test_cache_manager_basic(self):
        """Test basic cache manager functionality"""
        from codesonor.cache_manager import CacheManager
        import tempfile
        from pathlib import Path
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_mgr = CacheManager(cache_dir=Path(temp_dir))
            
            # Test set and get
            test_data = {"test": "data", "value": 123}
            cache_mgr.set("/test/repo", test_data, ttl=3600)
            
            retrieved = cache_mgr.get("/test/repo")
            assert retrieved is not None
            assert retrieved["test"] == "data"
            assert retrieved["value"] == 123
            
            # Test stats
            stats = cache_mgr.get_stats()
            assert stats["total_entries"] >= 1
    
    def test_exporter_formats(self):
        """Test export manager format support"""
        from codesonor.exporter import ExportManager
        
        exporter = ExportManager()
        assert "json" in exporter.supported_formats
        assert "html" in exporter.supported_formats
        assert "markdown" in exporter.supported_formats
    
    def test_rules_engine_config_template(self):
        """Test rules engine config template generation"""
        from codesonor.rules_engine import RulesEngine
        import tempfile
        from pathlib import Path
        
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_engine = RulesEngine(Path(temp_dir))
            template = rules_engine.generate_config_template()
            
            assert template is not None
            assert "rules:" in template
            assert "no-print-statements" in template
            assert "pattern:" in template
