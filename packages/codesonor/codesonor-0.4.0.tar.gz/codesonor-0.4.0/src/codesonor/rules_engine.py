"""
Custom rules engine for CodeSonor.
Allows users to define custom analysis rules via .codesonor.yml
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Rule:
    """Represents a custom analysis rule."""
    id: str
    name: str
    description: str
    pattern: str
    severity: str = "warning"  # error, warning, info
    file_patterns: List[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class RuleViolation:
    """Represents a rule violation."""
    rule_id: str
    rule_name: str
    file_path: Path
    line_number: int
    line_content: str
    severity: str
    message: str


class RulesEngine:
    """Manages and executes custom analysis rules."""
    
    def __init__(self, repo_path: Path):
        """
        Initialize rules engine.
        
        Args:
            repo_path: Path to repository
        """
        self.repo_path = Path(repo_path)
        self.rules: List[Rule] = []
        self.violations: List[RuleViolation] = []
        self._load_rules()
    
    def _load_rules(self):
        """Load rules from .codesonor.yml file."""
        config_file = self.repo_path / '.codesonor.yml'
        
        if not config_file.exists():
            # Load default rules
            self._load_default_rules()
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config or 'rules' not in config:
                self._load_default_rules()
                return
            
            for rule_data in config['rules']:
                rule = Rule(
                    id=rule_data.get('id', ''),
                    name=rule_data.get('name', ''),
                    description=rule_data.get('description', ''),
                    pattern=rule_data.get('pattern', ''),
                    severity=rule_data.get('severity', 'warning'),
                    file_patterns=rule_data.get('file_patterns', ['**/*.py']),
                    enabled=rule_data.get('enabled', True)
                )
                self.rules.append(rule)
        
        except Exception as e:
            print(f"Warning: Could not load .codesonor.yml: {e}")
            self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default built-in rules."""
        default_rules = [
            Rule(
                id="no-print-statements",
                name="No Print Statements",
                description="Avoid using print() in production code, use logging instead",
                pattern=r'^\s*print\s*\(',
                severity="warning",
                file_patterns=['**/*.py']
            ),
            Rule(
                id="no-todo-comments",
                name="No TODO Comments",
                description="TODO comments should be converted to issues",
                pattern=r'#\s*TODO',
                severity="info",
                file_patterns=['**/*']
            ),
            Rule(
                id="no-hardcoded-passwords",
                name="No Hardcoded Passwords",
                description="Potential hardcoded password detected",
                pattern=r'password\s*=\s*["\'][^"\']+["\']',
                severity="error",
                file_patterns=['**/*.py', '**/*.js', '**/*.java']
            ),
            Rule(
                id="no-broad-except",
                name="No Broad Exception Catching",
                description="Avoid catching broad Exception, be specific",
                pattern=r'except\s+Exception\s*:',
                severity="warning",
                file_patterns=['**/*.py']
            ),
            Rule(
                id="no-debug-code",
                name="No Debug Code",
                description="Debug code should not be committed",
                pattern=r'(debugger|console\.log|pdb\.set_trace)',
                severity="warning",
                file_patterns=['**/*.py', '**/*.js']
            ),
            Rule(
                id="no-long-lines",
                name="Line Too Long",
                description="Lines should not exceed 120 characters",
                pattern=r'^.{121,}$',
                severity="info",
                file_patterns=['**/*.py', '**/*.js', '**/*.java']
            )
        ]
        
        self.rules.extend(default_rules)
    
    def analyze(self) -> List[RuleViolation]:
        """
        Run all enabled rules against repository.
        
        Returns:
            List of rule violations
        """
        self.violations.clear()
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            self._execute_rule(rule)
        
        return self.violations
    
    def _execute_rule(self, rule: Rule):
        """
        Execute a single rule.
        
        Args:
            rule: Rule to execute
        """
        # Find files matching patterns
        files_to_check = set()
        for pattern in rule.file_patterns:
            files_to_check.update(self.repo_path.glob(pattern))
        
        # Check each file
        for file_path in files_to_check:
            if not file_path.is_file():
                continue
            
            # Skip common ignored directories
            if any(ignore in file_path.parts for ignore in 
                   ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
                continue
            
            try:
                self._check_file(file_path, rule)
            except Exception as e:
                # Skip files that can't be read
                continue
    
    def _check_file(self, file_path: Path, rule: Rule):
        """
        Check a file against a rule.
        
        Args:
            file_path: Path to file
            rule: Rule to check against
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            pattern = re.compile(rule.pattern, re.IGNORECASE)
            
            for line_num, line in enumerate(lines, 1):
                if pattern.search(line):
                    violation = RuleViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        severity=rule.severity,
                        message=rule.description
                    )
                    self.violations.append(violation)
        
        except Exception:
            pass
    
    def get_violations_by_severity(self) -> Dict[str, List[RuleViolation]]:
        """
        Group violations by severity.
        
        Returns:
            Dictionary mapping severity to violations
        """
        grouped = {
            'error': [],
            'warning': [],
            'info': []
        }
        
        for violation in self.violations:
            grouped[violation.severity].append(violation)
        
        return grouped
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of rule violations.
        
        Returns:
            Summary dictionary
        """
        by_severity = self.get_violations_by_severity()
        
        return {
            'total_violations': len(self.violations),
            'errors': len(by_severity['error']),
            'warnings': len(by_severity['warning']),
            'info': len(by_severity['info']),
            'files_with_violations': len(set(v.file_path for v in self.violations)),
            'rules_violated': len(set(v.rule_id for v in self.violations))
        }
    
    def generate_config_template(self) -> str:
        """
        Generate a template .codesonor.yml file.
        
        Returns:
            YAML configuration template
        """
        template = """# CodeSonor Custom Rules Configuration
# Define custom analysis rules for your repository

rules:
  # Example: Detect print statements
  - id: no-print-statements
    name: No Print Statements
    description: Avoid using print() in production code, use logging instead
    pattern: ^\\s*print\\s*\\(
    severity: warning  # error, warning, info
    file_patterns:
      - '**/*.py'
    enabled: true
  
  # Example: Detect TODO comments
  - id: no-todo-comments
    name: No TODO Comments
    description: TODO comments should be converted to issues
    pattern: '#\\s*TODO'
    severity: info
    file_patterns:
      - '**/*'
    enabled: true
  
  # Example: Detect hardcoded credentials
  - id: no-hardcoded-passwords
    name: No Hardcoded Passwords
    description: Potential hardcoded password detected
    pattern: password\\s*=\\s*["'][^"']+["']
    severity: error
    file_patterns:
      - '**/*.py'
      - '**/*.js'
      - '**/*.java'
    enabled: true
  
  # Add your custom rules here
  # - id: my-custom-rule
  #   name: My Custom Rule
  #   description: Description of what this rule checks
  #   pattern: regular_expression_pattern
  #   severity: warning
  #   file_patterns:
  #     - '**/*.py'
  #   enabled: true

# Quality thresholds (optional)
thresholds:
  min_quality_score: 70
  max_complexity: 10
  max_file_lines: 500
  min_test_coverage: 80

# Analysis options (optional)
options:
  exclude_patterns:
    - '**/test_*.py'
    - '**/tests/**'
    - '**/docs/**'
  
  include_patterns:
    - '**/*.py'
    - '**/*.js'
    - '**/*.ts'
"""
        
        return template
    
    def save_config_template(self):
        """Save configuration template to .codesonor.yml"""
        config_file = self.repo_path / '.codesonor.yml'
        
        if config_file.exists():
            print(f"⚠️  .codesonor.yml already exists at {config_file}")
            return False
        
        template = self.generate_config_template()
        config_file.write_text(template, encoding='utf-8')
        print(f"✅ Created .codesonor.yml template at {config_file}")
        return True
