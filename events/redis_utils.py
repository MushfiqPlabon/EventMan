"""
Redis utilities for EventMan - Real-time features and caching
"""

import json
import logging

from django_redis import get_redis_connection
from redis.exceptions import ConnectionError, RedisError

from .constants import CACHE_TIMEOUTS

logger = logging.getLogger(__name__)


class EventManRedis:
    """Redis utilities for real-time features"""

    def __init__(self):
        self.redis = get_redis_connection("default")

    def is_available(self):
        """Check if Redis is available"""
        return self.redis is not None

    def set_event_stats(self, stats_data, timeout=None):
        """Cache dashboard statistics"""
        if timeout is None:
            timeout = CACHE_TIMEOUTS["DASHBOARD_STATS"]
        try:
            if self.redis:
                self.redis.set("dashboard_stats", json.dumps(stats_data), ex=timeout)
            return True
        except (ConnectionError, RedisError) as e:
            logger.error(f"Failed to cache stats: {e}")
            return False

    def get_event_stats(self):
        """Get cached dashboard statistics"""
        try:
            if self.redis:
                data = self.redis.get("dashboard_stats")
                return json.loads(data) if data else None
        except (ConnectionError, RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get cached stats: {e}")
            return None

    def cache_search_results(self, query, results, timeout=None):
        """Cache search results for faster retrieval"""
        if timeout is None:
            timeout = CACHE_TIMEOUTS["SEARCH_RESULTS"]
        try:
            cache_key = f"search:{hash(query)}"
            if self.redis:
                self.redis.set(cache_key, json.dumps(results), ex=timeout)
            return True
        except (ConnectionError, RedisError) as e:
            logger.error(f"Failed to cache search results: {e}")
            return False

    def get_cached_search(self, query):
        """Get cached search results"""
        try:
            cache_key = f"search:{hash(query)}"
            if self.redis:
                data = self.redis.get(cache_key)
                return json.loads(data) if data else None
        except (ConnectionError, RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get cached search: {e}")
            return None

    def increment_event_views(self, event_id):
        """Track event view counts"""
        try:
            key = f"event_views:{event_id}"
            if self.redis:
                # Set expiry for view tracking
                result = self.redis.incr(key)
                self.redis.expire(key, CACHE_TIMEOUTS["EVENT_VIEWS"])
                return result
        except (ConnectionError, RedisError) as e:
            logger.error(f"Failed to increment views: {e}")
            return 0

    def get_event_views(self, event_id):
        """Get event view count"""
        try:
            key = f"event_views:{event_id}"
            if self.redis:
                views = self.redis.get(key)
                return int(views) if views else 0
        except (ConnectionError, RedisError, ValueError) as e:
            logger.error(f"Failed to get views: {e}")
            return 0


# Global Redis instance
redis_client = EventManRedis()
