"""Result caching system to avoid expensive re-runs."""

import os
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import asdict
import logging

from evaluators.base import EvaluationResult


class ResultCache:
    """Caches evaluation results to avoid expensive re-computation."""
    
    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours
        self.logger = logging.getLogger(__name__)
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Clean up expired entries on initialization
        self._cleanup_expired()
    
    def _get_cache_key(self, provider_name: str, test_case_id: str) -> str:
        """Generate cache key for a provider-test case combination."""
        key_string = f"{provider_name}:{test_case_id}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """Get file path for cache key."""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get_result(
        self, 
        provider_name: str, 
        test_case_id: str
    ) -> Optional[EvaluationResult]:
        """Get cached result if available and not expired."""
        cache_key = self._get_cache_key(provider_name, test_case_id)
        cache_file = self._get_cache_file_path(cache_key)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Check if expired
            cached_time = datetime.fromisoformat(cached_data["cached_at"])
            if datetime.now() - cached_time > timedelta(hours=self.ttl_hours):
                os.remove(cache_file)
                return None
            
            # Reconstruct EvaluationResult
            result_data = cached_data["result"]
            
            # Convert timestamp back to datetime
            result_data["timestamp"] = datetime.fromisoformat(result_data["timestamp"])
            result_data["response"]["timestamp"] = datetime.fromisoformat(result_data["response"]["timestamp"])
            
            # Reconstruct the result object
            from models.base import ModelResponse
            
            response_data = result_data["response"]
            response = ModelResponse(**response_data)
            
            result_data["response"] = response
            result = EvaluationResult(**result_data)
            
            self.logger.debug(f"Cache hit for {provider_name}:{test_case_id}")
            return result
            
        except Exception as e:
            self.logger.warning(f"Error loading cached result: {str(e)}")
            # Remove corrupted cache file
            if os.path.exists(cache_file):
                os.remove(cache_file)
            return None
    
    def store_result(
        self, 
        provider_name: str, 
        test_case_id: str, 
        result: EvaluationResult
    ) -> None:
        """Store evaluation result in cache."""
        cache_key = self._get_cache_key(provider_name, test_case_id)
        cache_file = self._get_cache_file_path(cache_key)
        
        try:
            # Convert result to dict for JSON serialization
            result_dict = asdict(result)
            
            # Convert datetime objects to ISO strings
            result_dict["timestamp"] = result.timestamp.isoformat()
            result_dict["response"]["timestamp"] = result.response.timestamp.isoformat()
            
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "provider_name": provider_name,
                "test_case_id": test_case_id,
                "result": result_dict
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            self.logger.debug(f"Cached result for {provider_name}:{test_case_id}")
            
        except Exception as e:
            self.logger.warning(f"Error storing result in cache: {str(e)}")
    
    def clear_cache(self) -> None:
        """Clear all cached results."""
        try:
            for file_name in os.listdir(self.cache_dir):
                if file_name.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, file_name)
                    os.remove(file_path)
            
            self.logger.info("Cache cleared successfully")
            
        except Exception as e:
            self.logger.error(f"Error clearing cache: {str(e)}")
    
    def _cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        if not os.path.exists(self.cache_dir):
            return
        
        current_time = datetime.now()
        expired_count = 0
        
        try:
            for file_name in os.listdir(self.cache_dir):
                if not file_name.endswith('.json'):
                    continue
                
                file_path = os.path.join(self.cache_dir, file_name)
                
                try:
                    with open(file_path, 'r') as f:
                        cached_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cached_data["cached_at"])
                    if current_time - cached_time > timedelta(hours=self.ttl_hours):
                        os.remove(file_path)
                        expired_count += 1
                        
                except Exception:
                    # Remove corrupted files
                    os.remove(file_path)
                    expired_count += 1
            
            if expired_count > 0:
                self.logger.info(f"Cleaned up {expired_count} expired cache entries")
                
        except Exception as e:
            self.logger.warning(f"Error during cache cleanup: {str(e)}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not os.path.exists(self.cache_dir):
            return {"total_entries": 0, "cache_size_mb": 0}
        
        try:
            files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            total_entries = len(files)
            
            total_size = 0
            for file_name in files:
                file_path = os.path.join(self.cache_dir, file_name)
                total_size += os.path.getsize(file_path)
            
            cache_size_mb = total_size / (1024 * 1024)
            
            return {
                "total_entries": total_entries,
                "cache_size_mb": round(cache_size_mb, 2),
                "cache_dir": self.cache_dir,
                "ttl_hours": self.ttl_hours
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {str(e)}")
            return {"error": str(e)}
    
    def get_cached_providers(self) -> Dict[str, int]:
        """Get count of cached results per provider."""
        if not os.path.exists(self.cache_dir):
            return {}
        
        provider_counts = {}
        
        try:
            for file_name in os.listdir(self.cache_dir):
                if not file_name.endswith('.json'):
                    continue
                
                file_path = os.path.join(self.cache_dir, file_name)
                
                try:
                    with open(file_path, 'r') as f:
                        cached_data = json.load(f)
                    
                    provider = cached_data.get("provider_name", "unknown")
                    provider_counts[provider] = provider_counts.get(provider, 0) + 1
                    
                except Exception:
                    continue
            
            return provider_counts
            
        except Exception as e:
            self.logger.error(f"Error getting provider stats: {str(e)}")
            return {}