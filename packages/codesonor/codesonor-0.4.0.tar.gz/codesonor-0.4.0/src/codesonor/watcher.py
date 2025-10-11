"""
Watch mode for CodeSonor - continuous monitoring of repository changes.
"""

import time
from pathlib import Path
from typing import Callable, Dict, Any, Set
from datetime import datetime
import hashlib


class WatchManager:
    """Manages continuous monitoring of repository changes."""
    
    def __init__(self, repo_path: Path, interval: int = 10):
        """
        Initialize watch manager.
        
        Args:
            repo_path: Path to repository to watch
            interval: Check interval in seconds (default: 10)
        """
        self.repo_path = Path(repo_path)
        self.interval = interval
        self.file_hashes: Dict[str, str] = {}
        self.is_watching = False
    
    def start(self, on_change_callback: Callable[[Set[Path]], None]):
        """
        Start watching repository for changes.
        
        Args:
            on_change_callback: Function to call when changes detected.
                               Receives set of changed file paths.
        """
        self.is_watching = True
        print(f"👀 Watching {self.repo_path} for changes (interval: {self.interval}s)")
        print("Press Ctrl+C to stop...\n")
        
        # Initial scan
        self._scan_files()
        
        try:
            while self.is_watching:
                time.sleep(self.interval)
                changed_files = self._detect_changes()
                
                if changed_files:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"\n[{timestamp}] 🔄 Detected {len(changed_files)} change(s)")
                    for file_path in list(changed_files)[:5]:
                        print(f"  - {file_path.relative_to(self.repo_path)}")
                    if len(changed_files) > 5:
                        print(f"  - ... and {len(changed_files) - 5} more")
                    
                    # Trigger callback
                    on_change_callback(changed_files)
                    
                    # Re-scan to update hashes
                    self._scan_files()
        
        except KeyboardInterrupt:
            print("\n\n✋ Stopping watch mode...")
            self.is_watching = False
    
    def stop(self):
        """Stop watching."""
        self.is_watching = False
    
    def _scan_files(self):
        """Scan all files and compute hashes."""
        self.file_hashes.clear()
        
        # Patterns to ignore
        ignore_patterns = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', 'dist', 'build', '.egg-info'
        }
        
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                # Skip ignored directories
                if any(pattern in file_path.parts for pattern in ignore_patterns):
                    continue
                
                # Skip binary files and common non-code files
                if file_path.suffix in {'.pyc', '.pyo', '.so', '.dll', '.exe', 
                                       '.jpg', '.png', '.gif', '.pdf', '.zip'}:
                    continue
                
                try:
                    file_hash = self._compute_file_hash(file_path)
                    self.file_hashes[str(file_path)] = file_hash
                except:
                    continue
    
    def _detect_changes(self) -> Set[Path]:
        """
        Detect changed files since last scan.
        
        Returns:
            Set of changed file paths
        """
        changed_files = set()
        current_files = {}
        
        # Scan current state
        ignore_patterns = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', 'dist', 'build', '.egg-info'
        }
        
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                if any(pattern in file_path.parts for pattern in ignore_patterns):
                    continue
                
                if file_path.suffix in {'.pyc', '.pyo', '.so', '.dll', '.exe',
                                       '.jpg', '.png', '.gif', '.pdf', '.zip'}:
                    continue
                
                try:
                    file_hash = self._compute_file_hash(file_path)
                    current_files[str(file_path)] = file_hash
                    
                    # Check if modified
                    if str(file_path) in self.file_hashes:
                        if self.file_hashes[str(file_path)] != file_hash:
                            changed_files.add(file_path)
                    else:
                        # New file
                        changed_files.add(file_path)
                except:
                    continue
        
        # Check for deleted files
        deleted_files = set(self.file_hashes.keys()) - set(current_files.keys())
        for deleted_file in deleted_files:
            changed_files.add(Path(deleted_file))
        
        return changed_files
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute MD5 hash of file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            MD5 hash string
        """
        md5 = hashlib.md5()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    md5.update(chunk)
            return md5.hexdigest()
        except:
            return ""


class AnalysisScheduler:
    """Schedules re-analysis with debouncing."""
    
    def __init__(self, debounce_seconds: int = 5):
        """
        Initialize scheduler.
        
        Args:
            debounce_seconds: Wait time after last change before re-analyzing
        """
        self.debounce_seconds = debounce_seconds
        self.last_change_time = None
        self.pending_changes = set()
    
    def register_change(self, changed_files: Set[Path]):
        """
        Register file changes.
        
        Args:
            changed_files: Set of changed file paths
        """
        self.pending_changes.update(changed_files)
        self.last_change_time = time.time()
    
    def should_analyze(self) -> bool:
        """
        Check if enough time has passed since last change.
        
        Returns:
            True if analysis should be triggered
        """
        if not self.last_change_time or not self.pending_changes:
            return False
        
        time_since_last_change = time.time() - self.last_change_time
        return time_since_last_change >= self.debounce_seconds
    
    def get_pending_changes(self) -> Set[Path]:
        """Get and clear pending changes."""
        changes = self.pending_changes.copy()
        self.pending_changes.clear()
        self.last_change_time = None
        return changes
