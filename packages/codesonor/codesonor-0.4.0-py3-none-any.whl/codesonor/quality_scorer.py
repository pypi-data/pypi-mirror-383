"""
Code quality scoring system for CodeSonor.
Analyzes code quality across multiple dimensions and generates a comprehensive score.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict


class QualityScorer:
    """Calculates comprehensive code quality scores."""
    
    # Score weights for different metrics
    WEIGHTS = {
        'documentation': 0.20,
        'complexity': 0.25,
        'structure': 0.20,
        'best_practices': 0.20,
        'maintainability': 0.15
    }
    
    def __init__(self, repo_path: Path):
        """
        Initialize quality scorer.
        
        Args:
            repo_path: Path to repository to analyze
        """
        self.repo_path = Path(repo_path)
        self.files_analyzed = 0
        self.issues_found = defaultdict(list)
    
    def calculate_score(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive quality score.
        
        Args:
            analysis_data: Repository analysis data
            
        Returns:
            Dictionary with overall score and component scores
        """
        scores = {
            'documentation': self._score_documentation(analysis_data),
            'complexity': self._score_complexity(analysis_data),
            'structure': self._score_structure(analysis_data),
            'best_practices': self._score_best_practices(analysis_data),
            'maintainability': self._score_maintainability(analysis_data)
        }
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[component] * self.WEIGHTS[component]
            for component in scores.keys()
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'component_scores': scores,
            'grade': self._get_grade(overall_score),
            'issues': dict(self.issues_found),
            'recommendations': self._generate_recommendations(scores)
        }
    
    def _score_documentation(self, data: Dict[str, Any]) -> float:
        """Score documentation quality (0-100)."""
        score = 100.0
        issues = []
        
        # Check for README
        if not self._has_readme():
            score -= 20
            issues.append("Missing README.md")
        
        # Check for LICENSE
        if not self._has_license():
            score -= 10
            issues.append("Missing LICENSE file")
        
        # Check for docstrings in Python files
        docstring_coverage = self._check_docstring_coverage()
        if docstring_coverage < 0.5:
            score -= 20
            issues.append(f"Low docstring coverage ({docstring_coverage*100:.1f}%)")
        elif docstring_coverage < 0.8:
            score -= 10
            issues.append(f"Moderate docstring coverage ({docstring_coverage*100:.1f}%)")
        
        # Check for comments
        comment_ratio = self._calculate_comment_ratio(data)
        if comment_ratio < 0.05:
            score -= 15
            issues.append(f"Low comment ratio ({comment_ratio*100:.1f}%)")
        
        # Check for CONTRIBUTING guide
        if not self._has_contributing():
            score -= 5
            issues.append("Missing CONTRIBUTING.md")
        
        self.issues_found['documentation'] = issues
        return max(0, score)
    
    def _score_complexity(self, data: Dict[str, Any]) -> float:
        """Score code complexity (0-100)."""
        score = 100.0
        issues = []
        
        # Analyze file sizes
        large_files = self._find_large_files(threshold=500)
        if large_files:
            penalty = min(30, len(large_files) * 5)
            score -= penalty
            issues.append(f"{len(large_files)} files exceed 500 lines")
        
        # Check function/method complexity
        complex_functions = self._find_complex_functions()
        if complex_functions:
            penalty = min(25, len(complex_functions) * 3)
            score -= penalty
            issues.append(f"{len(complex_functions)} functions with high complexity")
        
        # Check nesting depth
        deep_nesting = self._find_deep_nesting()
        if deep_nesting:
            penalty = min(20, len(deep_nesting) * 4)
            score -= penalty
            issues.append(f"{len(deep_nesting)} locations with deep nesting")
        
        self.issues_found['complexity'] = issues
        return max(0, score)
    
    def _score_structure(self, data: Dict[str, Any]) -> float:
        """Score repository structure (0-100)."""
        score = 100.0
        issues = []
        
        # Check for standard directories
        expected_dirs = ['src', 'tests', 'docs']
        missing_dirs = [d for d in expected_dirs if not (self.repo_path / d).exists()]
        
        if 'tests' in missing_dirs or 'test' not in str(self.repo_path).lower():
            score -= 30
            issues.append("No tests directory found")
        
        if 'docs' in missing_dirs:
            score -= 15
            issues.append("No docs directory found")
        
        # Check for proper package structure
        if not self._has_proper_package_structure():
            score -= 20
            issues.append("Improper package structure")
        
        # Check for configuration files
        config_files = ['setup.py', 'pyproject.toml', 'requirements.txt', 'package.json']
        has_config = any((self.repo_path / f).exists() for f in config_files)
        if not has_config:
            score -= 15
            issues.append("Missing configuration files")
        
        self.issues_found['structure'] = issues
        return max(0, score)
    
    def _score_best_practices(self, data: Dict[str, Any]) -> float:
        """Score adherence to best practices (0-100)."""
        score = 100.0
        issues = []
        
        # Check for .gitignore
        if not (self.repo_path / '.gitignore').exists():
            score -= 15
            issues.append("Missing .gitignore")
        
        # Check for CI/CD configuration
        ci_files = ['.github/workflows', '.gitlab-ci.yml', '.travis.yml', 'Jenkinsfile']
        has_ci = any((self.repo_path / f).exists() for f in ci_files)
        if not has_ci:
            score -= 20
            issues.append("No CI/CD configuration found")
        
        # Check for dependency management
        if not self._has_dependency_lock():
            score -= 15
            issues.append("No dependency lock file")
        
        # Check for security files
        if not (self.repo_path / 'SECURITY.md').exists():
            score -= 10
            issues.append("Missing SECURITY.md")
        
        # Code smell detection
        code_smells = self._detect_code_smells()
        if code_smells:
            penalty = min(25, len(code_smells) * 2)
            score -= penalty
            issues.append(f"{len(code_smells)} potential code smells detected")
        
        self.issues_found['best_practices'] = issues
        return max(0, score)
    
    def _score_maintainability(self, data: Dict[str, Any]) -> float:
        """Score code maintainability (0-100)."""
        score = 100.0
        issues = []
        
        # Check for duplicated code
        duplication_ratio = self._estimate_duplication()
        if duplication_ratio > 0.15:
            score -= 30
            issues.append(f"High code duplication ({duplication_ratio*100:.1f}%)")
        elif duplication_ratio > 0.08:
            score -= 15
            issues.append(f"Moderate code duplication ({duplication_ratio*100:.1f}%)")
        
        # Check average file size
        avg_file_size = self._calculate_avg_file_size()
        if avg_file_size > 300:
            score -= 20
            issues.append(f"Large average file size ({avg_file_size:.0f} lines)")
        
        # Check for consistent naming
        naming_issues = self._check_naming_consistency()
        if naming_issues:
            score -= 15
            issues.append(f"{len(naming_issues)} naming inconsistencies")
        
        self.issues_found['maintainability'] = issues
        return max(0, score)
    
    def _get_grade(self, score: float) -> str:
        """Convert numerical score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations based on scores."""
        recommendations = []
        
        if scores['documentation'] < 70:
            recommendations.append("📚 Improve documentation: Add README, docstrings, and comments")
        
        if scores['complexity'] < 70:
            recommendations.append("🔧 Reduce complexity: Break down large functions and reduce nesting")
        
        if scores['structure'] < 70:
            recommendations.append("📁 Improve structure: Add tests directory and proper package organization")
        
        if scores['best_practices'] < 70:
            recommendations.append("✅ Follow best practices: Add CI/CD, .gitignore, and security policies")
        
        if scores['maintainability'] < 70:
            recommendations.append("🔨 Enhance maintainability: Reduce duplication and improve naming consistency")
        
        return recommendations
    
    # Helper methods
    def _has_readme(self) -> bool:
        """Check if README exists."""
        return any((self.repo_path / f).exists() for f in ['README.md', 'README.rst', 'README.txt', 'README'])
    
    def _has_license(self) -> bool:
        """Check if LICENSE exists."""
        return any((self.repo_path / f).exists() for f in ['LICENSE', 'LICENSE.md', 'LICENSE.txt'])
    
    def _has_contributing(self) -> bool:
        """Check if CONTRIBUTING guide exists."""
        return (self.repo_path / 'CONTRIBUTING.md').exists()
    
    def _has_dependency_lock(self) -> bool:
        """Check for dependency lock files."""
        lock_files = ['poetry.lock', 'Pipfile.lock', 'package-lock.json', 'yarn.lock']
        return any((self.repo_path / f).exists() for f in lock_files)
    
    def _has_proper_package_structure(self) -> bool:
        """Check for proper Python package structure."""
        has_src = (self.repo_path / 'src').exists()
        has_init = list(self.repo_path.rglob('__init__.py'))
        has_setup = (self.repo_path / 'setup.py').exists() or (self.repo_path / 'pyproject.toml').exists()
        return (has_src or has_init) and has_setup
    
    def _check_docstring_coverage(self) -> float:
        """Calculate docstring coverage in Python files."""
        python_files = list(self.repo_path.rglob('*.py'))
        if not python_files:
            return 1.0
        
        total_functions = 0
        documented_functions = 0
        
        for file_path in python_files[:20]:  # Sample first 20 files
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Find function definitions
                functions = re.findall(r'^\s*def\s+\w+\s*\(', content, re.MULTILINE)
                total_functions += len(functions)
                
                # Find docstrings
                docstrings = re.findall(r'^\s*def\s+\w+\s*\([^)]*\):[^"]*"""', content, re.MULTILINE)
                documented_functions += len(docstrings)
            except:
                continue
        
        return documented_functions / total_functions if total_functions > 0 else 1.0
    
    def _calculate_comment_ratio(self, data: Dict[str, Any]) -> float:
        """Calculate ratio of comment lines to code lines."""
        code_files = list(self.repo_path.rglob('*.py'))[:20]
        total_lines = 0
        comment_lines = 0
        
        for file_path in code_files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                total_lines += len(lines)
                comment_lines += sum(1 for line in lines if line.strip().startswith('#'))
            except:
                continue
        
        return comment_lines / total_lines if total_lines > 0 else 0
    
    def _find_large_files(self, threshold: int = 500) -> List[Path]:
        """Find files exceeding line threshold."""
        large_files = []
        for file_path in self.repo_path.rglob('*.py'):
            try:
                lines = len(file_path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                if lines > threshold:
                    large_files.append(file_path)
            except:
                continue
        return large_files
    
    def _find_complex_functions(self) -> List[str]:
        """Find functions with high cyclomatic complexity."""
        complex_funcs = []
        # Simplified complexity detection based on control flow keywords
        for file_path in list(self.repo_path.rglob('*.py'))[:20]:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):[^d]*?(?=\ndef|\nclass|\Z)', content, re.DOTALL)
                
                for func_content in functions:
                    # Count control flow statements
                    complexity = len(re.findall(r'\b(if|elif|for|while|and|or|except)\b', func_content))
                    if complexity > 10:
                        complex_funcs.append(func_content[:50])
            except:
                continue
        return complex_funcs
    
    def _find_deep_nesting(self, max_depth: int = 4) -> List[str]:
        """Find code with deep nesting levels."""
        deep_nesting = []
        for file_path in list(self.repo_path.rglob('*.py'))[:20]:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    indent = len(line) - len(line.lstrip())
                    if indent >= max_depth * 4:  # Assuming 4-space indentation
                        deep_nesting.append(f"{file_path.name}:{i+1}")
            except:
                continue
        return deep_nesting[:10]  # Limit to 10 examples
    
    def _detect_code_smells(self) -> List[str]:
        """Detect common code smells."""
        smells = []
        for file_path in list(self.repo_path.rglob('*.py'))[:20]:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Long parameter lists
                if re.search(r'def\s+\w+\s*\([^)]{100,}\)', content):
                    smells.append(f"{file_path.name}: Long parameter list")
                
                # Magic numbers
                if len(re.findall(r'\b\d{4,}\b', content)) > 3:
                    smells.append(f"{file_path.name}: Magic numbers")
                
                # Global variables
                if len(re.findall(r'^[A-Z_]{2,}\s*=', content, re.MULTILINE)) > 5:
                    smells.append(f"{file_path.name}: Many global variables")
            except:
                continue
        return smells
    
    def _estimate_duplication(self) -> float:
        """Estimate code duplication ratio."""
        # Simplified duplication detection
        files = list(self.repo_path.rglob('*.py'))[:15]
        all_lines = []
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
                all_lines.extend(lines)
            except:
                continue
        
        if not all_lines:
            return 0.0
        
        unique_lines = set(all_lines)
        duplication = 1 - (len(unique_lines) / len(all_lines))
        return duplication
    
    def _calculate_avg_file_size(self) -> float:
        """Calculate average file size in lines."""
        files = list(self.repo_path.rglob('*.py'))
        if not files:
            return 0.0
        
        total_lines = 0
        for file_path in files[:30]:
            try:
                lines = len(file_path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                total_lines += lines
            except:
                continue
        
        return total_lines / min(len(files), 30)
    
    def _check_naming_consistency(self) -> List[str]:
        """Check for naming convention inconsistencies."""
        issues = []
        for file_path in list(self.repo_path.rglob('*.py'))[:20]:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Check for mixed naming styles in functions
                snake_case = re.findall(r'def\s+([a-z_]+)\s*\(', content)
                camel_case = re.findall(r'def\s+([a-z]+[A-Z][a-zA-Z]+)\s*\(', content)
                
                if snake_case and camel_case:
                    issues.append(f"{file_path.name}: Mixed function naming styles")
            except:
                continue
        return issues
