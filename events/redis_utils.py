"""
Redis utilities for EventMan - Real-time features and caching
"""

import json

from django.conf import settings
from django.core.cache import cache

try:
    from upstash_redis import Redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class EventManRedis:
    """Redis utilities for real-time features"""

    def __init__(self):
        self.redis = None
        if REDIS_AVAILABLE and settings.REDIS_URL:
            try:
                self.redis = Redis(url=settings.REDIS_URL)
            except Exception as e:
                print(f"Redis connection failed: {e}")
                self.redis = None

    def is_available(self):
        """Check if Redis is available"""
        return self.redis is not None

    def set_event_stats(self, stats_data, timeout=300):
        """Cache dashboard statistics"""
        try:
            if self.redis:
                self.redis.setex("dashboard_stats", timeout, json.dumps(stats_data))
            else:
                cache.set("dashboard_stats", stats_data, timeout)
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
            else:
                return cache.get("dashboard_stats")
        except Exception as e:
            print(f"Failed to get cached stats: {e}")
            return None

    def cache_search_results(self, query, results, timeout=600):
        """Cache search results for faster retrieval"""
        try:
            cache_key = f"search:{hash(query)}"
            if self.redis:
                self.redis.setex(cache_key, timeout, json.dumps(results))
            else:
                cache.set(cache_key, results, timeout)
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
            else:
                return cache.get(cache_key)
        except Exception as e:
            print(f"Failed to get cached search: {e}")
            return None

    def increment_event_views(self, event_id):
        """Track event view counts"""
        try:
            key = f"event_views:{event_id}"
            if self.redis:
                return self.redis.incr(key)
            else:
                current = cache.get(key, 0)
                cache.set(key, current + 1, 86400)  # 24 hours
                return current + 1
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
            else:
                return cache.get(key, 0)
        except Exception as e:
            print(f"Failed to get views: {e}")
            return 0


# Global Redis instance
redis_client = EventManRedis()
