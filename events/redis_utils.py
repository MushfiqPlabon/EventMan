"""
Redis utilities for EventMan - Real-time features and caching
"""

import json

from django.conf import settings
from django_redis import get_redis_connection




class EventManRedis:
    """Redis utilities for real-time features"""

    def __init__(self):
        self.redis = get_redis_connection("default")

    def is_available(self):
        """Check if Redis is available"""
        return self.redis is not None

    def set_event_stats(self, stats_data, timeout=300):
        """Cache dashboard statistics"""
        try:
            if self.redis:
                self.redis.set("dashboard_stats", json.dumps(stats_data), ex=timeout)
            return True
        except Exception as e:
            print(f"Failed to cache stats: {e}")
            return False

    def get_event_stats(self):
        """Get cached dashboard statistics"""
        try:
            if self.redis:
                data = self.redis.get("dashboard_stats")
                return json.loads(data) if data else None
        except Exception as e:
            print(f"Failed to get cached stats: {e}")
            return None

    def cache_search_results(self, query, results, timeout=600):
        """Cache search results for faster retrieval"""
        try:
            cache_key = f"search:{hash(query)}"
            if self.redis:
                self.redis.set(cache_key, json.dumps(results), ex=timeout)
            return True
        except Exception as e:
            print(f"Failed to cache search results: {e}")
            return False

    def get_cached_search(self, query):
        """Get cached search results"""
        try:
            cache_key = f"search:{hash(query)}"
            if self.redis:
                data = self.redis.get(cache_key)
                return json.loads(data) if data else None
        except Exception as e:
            print(f"Failed to get cached search: {e}")
            return None

    def increment_event_views(self, event_id):
        """Track event view counts"""
        try:
            key = f"event_views:{event_id}"
            if self.redis:
                return self.redis.incr(key)
        except Exception as e:
            print(f"Failed to increment views: {e}")
            return 0

    def get_event_views(self, event_id):
        """Get event view count"""
        try:
            key = f"event_views:{event_id}"
            if self.redis:
                views = self.redis.get(key)
                return int(views) if views else 0
        except Exception as e:
            print(f"Failed to get views: {e}")
            return 0


# Global Redis instance
redis_client = EventManRedis()
