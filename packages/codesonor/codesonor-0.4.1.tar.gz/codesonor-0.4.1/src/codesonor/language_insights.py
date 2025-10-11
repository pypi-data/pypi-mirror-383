"""
Language-specific deep analysis for CodeSonor.
Provides framework detection and best practices for popular languages.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict


class LanguageInsights:
    """Provides deep language-specific analysis and insights."""
    
    def __init__(self, repo_path: Path):
        """
        Initialize language insights analyzer.
        
        Args:
            repo_path: Path to repository
        """
        self.repo_path = Path(repo_path)
        self.insights = {}
    
    def analyze(self, languages: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze repository with language-specific insights.
        
        Args:
            languages: Dictionary of languages and their percentages
            
        Returns:
            Dictionary of insights per language
        """
        self.insights.clear()
        
        for language in languages.keys():
            lang_lower = language.lower()
            
            if lang_lower == 'python':
                self.insights['Python'] = self._analyze_python()
            elif lang_lower in ['javascript', 'typescript']:
                self.insights[language] = self._analyze_javascript()
            elif lang_lower == 'java':
                self.insights['Java'] = self._analyze_java()
            elif lang_lower == 'go':
                self.insights['Go'] = self._analyze_go()
        
        return self.insights
    
    def _analyze_python(self) -> Dict[str, Any]:
        """Deep analysis for Python projects."""
        insights = {
            'frameworks': self._detect_python_frameworks(),
            'dependencies': self._get_python_dependencies(),
            'project_type': self._detect_python_project_type(),
            'best_practices': self._check_python_best_practices(),
            'testing': self._check_python_testing(),
            'packaging': self._check_python_packaging()
        }
        
        return insights
    
    def _analyze_javascript(self) -> Dict[str, Any]:
        """Deep analysis for JavaScript/TypeScript projects."""
        insights = {
            'frameworks': self._detect_js_frameworks(),
            'dependencies': self._get_js_dependencies(),
            'project_type': self._detect_js_project_type(),
            'best_practices': self._check_js_best_practices(),
            'testing': self._check_js_testing(),
            'bundler': self._detect_js_bundler()
        }
        
        return insights
    
    def _analyze_java(self) -> Dict[str, Any]:
        """Deep analysis for Java projects."""
        insights = {
            'frameworks': self._detect_java_frameworks(),
            'build_tool': self._detect_java_build_tool(),
            'project_type': self._detect_java_project_type(),
            'best_practices': self._check_java_best_practices()
        }
        
        return insights
    
    def _analyze_go(self) -> Dict[str, Any]:
        """Deep analysis for Go projects."""
        insights = {
            'frameworks': self._detect_go_frameworks(),
            'dependencies': self._get_go_dependencies(),
            'project_type': self._detect_go_project_type(),
            'best_practices': self._check_go_best_practices()
        }
        
        return insights
    
    # Python-specific methods
    def _detect_python_frameworks(self) -> List[str]:
        """Detect Python frameworks used."""
        frameworks = []
        
        # Check common framework imports
        framework_patterns = {
            'Django': [r'import django', r'from django'],
            'Flask': [r'import flask', r'from flask'],
            'FastAPI': [r'import fastapi', r'from fastapi'],
            'Pyramid': [r'import pyramid', r'from pyramid'],
            'Tornado': [r'import tornado', r'from tornado'],
            'Streamlit': [r'import streamlit', r'streamlit as st'],
            'Pandas': [r'import pandas', r'pandas as pd'],
            'NumPy': [r'import numpy', r'numpy as np'],
            'TensorFlow': [r'import tensorflow', r'tensorflow as tf'],
            'PyTorch': [r'import torch'],
            'Requests': [r'import requests'],
            'SQLAlchemy': [r'import sqlalchemy', r'from sqlalchemy']
        }
        
        for py_file in list(self.repo_path.rglob('*.py'))[:30]:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                for framework, patterns in framework_patterns.items():
                    if any(re.search(pattern, content) for pattern in patterns):
                        if framework not in frameworks:
                            frameworks.append(framework)
            except:
                continue
        
        return frameworks
    
    def _get_python_dependencies(self) -> Dict[str, Any]:
        """Get Python dependencies information."""
        deps = {
            'has_requirements': False,
            'has_pipfile': False,
            'has_poetry': False,
            'count': 0,
            'packages': []
        }
        
        # Check requirements.txt
        req_file = self.repo_path / 'requirements.txt'
        if req_file.exists():
            deps['has_requirements'] = True
            try:
                content = req_file.read_text(encoding='utf-8')
                packages = [line.split('==')[0].split('>=')[0].split('<=')[0].strip() 
                           for line in content.split('\n') 
                           if line.strip() and not line.startswith('#')]
                deps['count'] = len(packages)
                deps['packages'] = packages[:20]  # First 20
            except:
                pass
        
        # Check Pipfile
        if (self.repo_path / 'Pipfile').exists():
            deps['has_pipfile'] = True
        
        # Check pyproject.toml (Poetry)
        if (self.repo_path / 'pyproject.toml').exists():
            deps['has_poetry'] = True
        
        return deps
    
    def _detect_python_project_type(self) -> str:
        """Detect type of Python project."""
        # Check for web frameworks
        if any(f in self._detect_python_frameworks() for f in ['Django', 'Flask', 'FastAPI']):
            return 'Web Application'
        
        # Check for data science
        if any(f in self._detect_python_frameworks() for f in ['Pandas', 'NumPy', 'TensorFlow', 'PyTorch']):
            return 'Data Science / ML'
        
        # Check for CLI
        cli_indicators = ['click', 'argparse', 'typer']
        for py_file in list(self.repo_path.rglob('*.py'))[:10]:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if any(f'import {lib}' in content for lib in cli_indicators):
                    return 'Command Line Tool'
            except:
                continue
        
        # Check for package
        if (self.repo_path / 'setup.py').exists() or (self.repo_path / 'pyproject.toml').exists():
            return 'Python Package/Library'
        
        return 'General Python Project'
    
    def _check_python_best_practices(self) -> List[str]:
        """Check Python best practices."""
        practices = []
        
        # Virtual environment
        if any((self.repo_path / env).exists() for env in ['venv', '.venv', 'env']):
            practices.append('✅ Uses virtual environment')
        else:
            practices.append('⚠️  No virtual environment detected')
        
        # Requirements
        if (self.repo_path / 'requirements.txt').exists():
            practices.append('✅ Has requirements.txt')
        else:
            practices.append('⚠️  No requirements.txt found')
        
        # Type hints
        type_hint_count = 0
        for py_file in list(self.repo_path.rglob('*.py'))[:10]:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                type_hint_count += len(re.findall(r':\s*[A-Z]\w+', content))
            except:
                continue
        
        if type_hint_count > 10:
            practices.append('✅ Uses type hints')
        else:
            practices.append('⚠️  Limited use of type hints')
        
        # Docstrings
        docstring_ratio = self._calculate_docstring_ratio()
        if docstring_ratio > 0.7:
            practices.append('✅ Good docstring coverage')
        elif docstring_ratio > 0.3:
            practices.append('⚠️  Moderate docstring coverage')
        else:
            practices.append('❌ Low docstring coverage')
        
        return practices
    
    def _check_python_testing(self) -> Dict[str, Any]:
        """Check Python testing setup."""
        testing = {
            'framework': None,
            'has_tests': False,
            'test_files': 0
        }
        
        # Detect testing framework
        if (self.repo_path / 'pytest.ini').exists() or \
           any('pytest' in str(f) for f in self.repo_path.rglob('*.py')[:20]):
            testing['framework'] = 'pytest'
        elif any('unittest' in str(f) for f in self.repo_path.rglob('*.py')[:20]):
            testing['framework'] = 'unittest'
        
        # Count test files
        test_files = list(self.repo_path.rglob('test_*.py')) + \
                    list(self.repo_path.rglob('*_test.py'))
        testing['test_files'] = len(test_files)
        testing['has_tests'] = len(test_files) > 0
        
        return testing
    
    def _check_python_packaging(self) -> Dict[str, bool]:
        """Check Python packaging configuration."""
        return {
            'has_setup_py': (self.repo_path / 'setup.py').exists(),
            'has_pyproject_toml': (self.repo_path / 'pyproject.toml').exists(),
            'has_manifest': (self.repo_path / 'MANIFEST.in').exists(),
            'has_init': len(list(self.repo_path.rglob('__init__.py'))) > 0
        }
    
    # JavaScript-specific methods
    def _detect_js_frameworks(self) -> List[str]:
        """Detect JavaScript/TypeScript frameworks."""
        frameworks = []
        
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            try:
                import json
                data = json.loads(package_json.read_text(encoding='utf-8'))
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                framework_map = {
                    'react': 'React',
                    'vue': 'Vue.js',
                    'angular': 'Angular',
                    'svelte': 'Svelte',
                    'next': 'Next.js',
                    'nuxt': 'Nuxt.js',
                    'express': 'Express.js',
                    'nestjs': 'NestJS',
                    'gatsby': 'Gatsby'
                }
                
                for dep_key, framework_name in framework_map.items():
                    if any(dep_key in dep.lower() for dep in deps.keys()):
                        frameworks.append(framework_name)
            except:
                pass
        
        return frameworks
    
    def _get_js_dependencies(self) -> Dict[str, Any]:
        """Get JavaScript dependencies."""
        deps = {
            'has_package_json': False,
            'count': 0,
            'dev_count': 0
        }
        
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            deps['has_package_json'] = True
            try:
                import json
                data = json.loads(package_json.read_text(encoding='utf-8'))
                deps['count'] = len(data.get('dependencies', {}))
                deps['dev_count'] = len(data.get('devDependencies', {}))
            except:
                pass
        
        return deps
    
    def _detect_js_project_type(self) -> str:
        """Detect JavaScript project type."""
        frameworks = self._detect_js_frameworks()
        
        if any(f in frameworks for f in ['React', 'Vue.js', 'Angular', 'Svelte']):
            return 'Frontend Application'
        elif any(f in frameworks for f in ['Express.js', 'NestJS']):
            return 'Backend API'
        elif any(f in frameworks for f in ['Next.js', 'Nuxt.js', 'Gatsby']):
            return 'Full-stack / SSR Application'
        
        return 'JavaScript Project'
    
    def _check_js_best_practices(self) -> List[str]:
        """Check JavaScript best practices."""
        practices = []
        
        if (self.repo_path / 'package-lock.json').exists() or \
           (self.repo_path / 'yarn.lock').exists():
            practices.append('✅ Uses dependency locking')
        
        if (self.repo_path / '.eslintrc.js').exists() or \
           (self.repo_path / '.eslintrc.json').exists():
            practices.append('✅ Uses ESLint')
        
        if (self.repo_path / '.prettierrc').exists():
            practices.append('✅ Uses Prettier')
        
        if (self.repo_path / 'tsconfig.json').exists():
            practices.append('✅ Uses TypeScript')
        
        return practices
    
    def _check_js_testing(self) -> Dict[str, Any]:
        """Check JavaScript testing setup."""
        testing = {
            'framework': None,
            'has_tests': False
        }
        
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            try:
                import json
                data = json.loads(package_json.read_text(encoding='utf-8'))
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                if any('jest' in dep.lower() for dep in deps.keys()):
                    testing['framework'] = 'Jest'
                elif any('mocha' in dep.lower() for dep in deps.keys()):
                    testing['framework'] = 'Mocha'
                elif any('vitest' in dep.lower() for dep in deps.keys()):
                    testing['framework'] = 'Vitest'
                
                testing['has_tests'] = testing['framework'] is not None
            except:
                pass
        
        return testing
    
    def _detect_js_bundler(self) -> Optional[str]:
        """Detect JavaScript bundler."""
        if (self.repo_path / 'webpack.config.js').exists():
            return 'Webpack'
        elif (self.repo_path / 'vite.config.js').exists() or \
             (self.repo_path / 'vite.config.ts').exists():
            return 'Vite'
        elif (self.repo_path / 'rollup.config.js').exists():
            return 'Rollup'
        elif (self.repo_path / 'parcel.config.js').exists():
            return 'Parcel'
        
        return None
    
    # Java-specific methods
    def _detect_java_frameworks(self) -> List[str]:
        """Detect Java frameworks."""
        frameworks = []
        
        # Check pom.xml for Maven dependencies
        pom_file = self.repo_path / 'pom.xml'
        if pom_file.exists():
            try:
                content = pom_file.read_text(encoding='utf-8')
                if 'spring-boot' in content:
                    frameworks.append('Spring Boot')
                elif 'springframework' in content:
                    frameworks.append('Spring Framework')
                if 'hibernate' in content:
                    frameworks.append('Hibernate')
            except:
                pass
        
        return frameworks
    
    def _detect_java_build_tool(self) -> Optional[str]:
        """Detect Java build tool."""
        if (self.repo_path / 'pom.xml').exists():
            return 'Maven'
        elif (self.repo_path / 'build.gradle').exists() or \
             (self.repo_path / 'build.gradle.kts').exists():
            return 'Gradle'
        
        return None
    
    def _detect_java_project_type(self) -> str:
        """Detect Java project type."""
        frameworks = self._detect_java_frameworks()
        
        if 'Spring Boot' in frameworks or 'Spring Framework' in frameworks:
            return 'Enterprise Application'
        
        return 'Java Project'
    
    def _check_java_best_practices(self) -> List[str]:
        """Check Java best practices."""
        practices = []
        
        if self._detect_java_build_tool():
            practices.append(f'✅ Uses {self._detect_java_build_tool()}')
        
        if list(self.repo_path.rglob('*Test.java')):
            practices.append('✅ Has unit tests')
        
        return practices
    
    # Go-specific methods
    def _detect_go_frameworks(self) -> List[str]:
        """Detect Go frameworks."""
        frameworks = []
        
        go_mod = self.repo_path / 'go.mod'
        if go_mod.exists():
            try:
                content = go_mod.read_text(encoding='utf-8')
                
                if 'gin-gonic/gin' in content:
                    frameworks.append('Gin')
                if 'gorilla/mux' in content:
                    frameworks.append('Gorilla Mux')
                if 'echo' in content:
                    frameworks.append('Echo')
            except:
                pass
        
        return frameworks
    
    def _get_go_dependencies(self) -> Dict[str, Any]:
        """Get Go dependencies."""
        deps = {
            'has_go_mod': (self.repo_path / 'go.mod').exists(),
            'has_go_sum': (self.repo_path / 'go.sum').exists()
        }
        
        return deps
    
    def _detect_go_project_type(self) -> str:
        """Detect Go project type."""
        if self._detect_go_frameworks():
            return 'Web Service'
        
        if (self.repo_path / 'cmd').exists():
            return 'CLI Application'
        
        return 'Go Project'
    
    def _check_go_best_practices(self) -> List[str]:
        """Check Go best practices."""
        practices = []
        
        if (self.repo_path / 'go.mod').exists():
            practices.append('✅ Uses Go modules')
        
        if list(self.repo_path.rglob('*_test.go')):
            practices.append('✅ Has unit tests')
        
        return practices
    
    # Helper methods
    def _calculate_docstring_ratio(self) -> float:
        """Calculate docstring coverage ratio."""
        py_files = list(self.repo_path.rglob('*.py'))[:15]
        total_functions = 0
        documented = 0
        
        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                funcs = re.findall(r'def\s+\w+', content)
                total_functions += len(funcs)
                docs = re.findall(r'def\s+\w+[^:]*:[\s\n]*"""', content)
                documented += len(docs)
            except:
                continue
        
        return documented / total_functions if total_functions > 0 else 0
