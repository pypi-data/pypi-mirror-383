"""
Cache management for CodeSonor analysis results.
Uses SQLite for persistent caching with TTL support.
"""

import sqlite3
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class CacheManager:
    """Manages caching of repository analysis results."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache storage. Defaults to ~/.codesonor/cache
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".codesonor" / "cache"
        
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "analysis_cache.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with cache schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                cache_key TEXT PRIMARY KEY,
                repo_path TEXT NOT NULL,
                analysis_data TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                hits INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_repo_path ON cache(repo_path)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)
        """)
        
        conn.commit()
        conn.close()
    
    def _generate_cache_key(self, repo_path: str, options: Dict[str, Any] = None) -> str:
        """
        Generate unique cache key for repository and options.
        
        Args:
            repo_path: Path to repository
            options: Analysis options that affect results
            
        Returns:
            MD5 hash as cache key
        """
        key_data = {
            'repo_path': str(repo_path),
            'options': options or {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, repo_path: str, options: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result if available and not expired.
        
        Args:
            repo_path: Path to repository
            options: Analysis options
            
        Returns:
            Cached analysis data or None if not found/expired
        """
        cache_key = self._generate_cache_key(repo_path, options)
        current_time = int(time.time())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT analysis_data, expires_at, hits
            FROM cache
            WHERE cache_key = ? AND expires_at > ?
        """, (cache_key, current_time))
        
        result = cursor.fetchone()
        
        if result:
            analysis_data, expires_at, hits = result
            
            # Update hit count
            cursor.execute("""
                UPDATE cache
                SET hits = hits + 1
                WHERE cache_key = ?
            """, (cache_key,))
            conn.commit()
            
            conn.close()
            return json.loads(analysis_data)
        
        conn.close()
        return None
    
    def set(self, repo_path: str, analysis_data: Dict[str, Any], 
            ttl: int = 3600, options: Dict[str, Any] = None):
        """
        Cache analysis result with TTL.
        
        Args:
            repo_path: Path to repository
            analysis_data: Analysis results to cache
            ttl: Time to live in seconds (default: 1 hour)
            options: Analysis options
        """
        cache_key = self._generate_cache_key(repo_path, options)
        current_time = int(time.time())
        expires_at = current_time + ttl
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO cache
            (cache_key, repo_path, analysis_data, created_at, expires_at, hits)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (cache_key, str(repo_path), json.dumps(analysis_data), 
              current_time, expires_at))
        
        conn.commit()
        conn.close()
    
    def clear(self, repo_path: Optional[str] = None):
        """
        Clear cache entries.
        
        Args:
            repo_path: If provided, clear only this repository's cache.
                      If None, clear all cache.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if repo_path:
            cursor.execute("DELETE FROM cache WHERE repo_path = ?", (str(repo_path),))
        else:
            cursor.execute("DELETE FROM cache")
        
        conn.commit()
        conn.close()
    
    def clean_expired(self):
        """Remove expired cache entries."""
        current_time = int(time.time())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM cache WHERE expires_at <= ?", (current_time,))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        current_time = int(time.time())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total entries
        cursor.execute("SELECT COUNT(*) FROM cache")
        total_entries = cursor.fetchone()[0]
        
        # Active entries (not expired)
        cursor.execute("SELECT COUNT(*) FROM cache WHERE expires_at > ?", (current_time,))
        active_entries = cursor.fetchone()[0]
        
        # Expired entries
        expired_entries = total_entries - active_entries
        
        # Total hits
        cursor.execute("SELECT SUM(hits) FROM cache")
        total_hits = cursor.fetchone()[0] or 0
        
        # Cache size (approximate)
        cursor.execute("SELECT SUM(LENGTH(analysis_data)) FROM cache")
        cache_size_bytes = cursor.fetchone()[0] or 0
        
        # Most hit entries
        cursor.execute("""
            SELECT repo_path, hits
            FROM cache
            WHERE expires_at > ?
            ORDER BY hits DESC
            LIMIT 5
        """, (current_time,))
        top_entries = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_entries': total_entries,
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'total_hits': total_hits,
            'cache_size_mb': round(cache_size_bytes / (1024 * 1024), 2),
            'top_entries': [{'repo': repo, 'hits': hits} for repo, hits in top_entries]
        }
    
    def is_cached(self, repo_path: str, options: Dict[str, Any] = None) -> bool:
        """
        Check if repository analysis is cached and valid.
        
        Args:
            repo_path: Path to repository
            options: Analysis options
            
        Returns:
            True if valid cache exists
        """
        return self.get(repo_path, options) is not None
