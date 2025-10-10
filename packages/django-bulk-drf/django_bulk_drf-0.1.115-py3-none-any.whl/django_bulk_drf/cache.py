"""
Cache utilities for operation progress tracking and result caching.
"""
import json
from typing import Any, Dict, Optional

from django.core.cache import cache


class OperationCache:
    """Cache manager for operation progress and results."""

    # Cache key prefixes
    PROGRESS_PREFIX = "bulk_drf:progress:"
    RESULT_PREFIX = "bulk_drf:result:"
    

    @classmethod
    def _get_progress_key(cls, task_id: str) -> str:
        """Get cache key for task progress."""
        return f"{cls.PROGRESS_PREFIX}{task_id}"

    @classmethod
    def _get_result_key(cls, task_id: str) -> str:
        """Get cache key for task result."""
        return f"{cls.RESULT_PREFIX}{task_id}"

    @classmethod
    def set_task_progress(cls, task_id: str, current: int, total: int, message: str = "") -> None:
        """
        Set task progress in cache.

        Args:
            task_id: Task ID
            current: Current progress count
            total: Total items to process
            message: Optional progress message
        """
        try:
            progress_data = {
                "task_id": task_id,
                "current": current,
                "total": total,
                "percentage": round((current / total) * 100, 2) if total > 0 else 0,
                "message": message,
            }
            
            cache_key = cls._get_progress_key(task_id)
            cache.set(cache_key, progress_data)
        except Exception as e:
            pass

    @classmethod
    def get_task_progress(cls, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task progress from cache.

        Args:
            task_id: Task ID

        Returns:
            Progress data dictionary or None if not found
        """
        try:
            cache_key = cls._get_progress_key(task_id)
            return cache.get(cache_key)
        except Exception as e:
            return None

    @classmethod
    def set_task_result(cls, task_id: str, result_data: Dict[str, Any]) -> None:
        """
        Set task result in cache.

        Args:
            task_id: Task ID
            result_data: Task result data
        """
        try:
            # Add metadata to result
            enriched_result = {
                **result_data,
                "task_id": task_id,
            }
            
            cache_key = cls._get_result_key(task_id)
            cache.set(cache_key, enriched_result)
        except Exception as e:
            pass

    @classmethod
    def get_task_result(cls, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task result from cache.

        Args:
            task_id: Task ID

        Returns:
            Result data dictionary or None if not found
        """
        try:
            cache_key = cls._get_result_key(task_id)
            return cache.get(cache_key)
        except Exception as e:
            return None

    @classmethod
    def delete_task_data(cls, task_id: str) -> None:
        """
        Delete all cached data for a task.

        Args:
            task_id: Task ID
        """
        try:
            progress_key = cls._get_progress_key(task_id)
            result_key = cls._get_result_key(task_id)
            
            cache.delete_many([progress_key, result_key])
        except Exception as e:
            pass

    @classmethod
    def clear_all_task_data(cls) -> None:
        """
        Clear all cached task data.
        
        Warning: This will delete all cached progress and results.
        """
        try:
            # This is cache-backend specific and may not work with all backends
            # For Redis, we can use pattern matching
            from django.core.cache import cache
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(f"{cls.PROGRESS_PREFIX}*")
                cache.delete_pattern(f"{cls.RESULT_PREFIX}*")
        except Exception as e:
            pass

    @classmethod
    def get_task_summary(cls, task_id: str) -> Dict[str, Any]:
        """
        Get combined progress and result summary for a task.

        Args:
            task_id: Task ID

        Returns:
            Combined task summary
        """
        progress = cls.get_task_progress(task_id)
        result = cls.get_task_result(task_id)
        
        summary = {
            "task_id": task_id,
            "has_progress": progress is not None,
            "has_result": result is not None,
        }
        
        if progress:
            summary["progress"] = progress
        
        if result:
            summary["result"] = result
        
        return summary


    @classmethod
    def cleanup_expired_tasks(cls) -> None:
        """
        Cleanup expired task data.
        
        This method should be called periodically (e.g., via a management command
        or cron job) to clean up expired cache entries.
        """
        try:
            # Implementation depends on cache backend
            # For now, we rely on cache timeout mechanisms
            pass
        except Exception as e:
            pass 