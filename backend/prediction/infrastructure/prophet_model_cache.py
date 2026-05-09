from dataclasses import dataclass
from datetime import timedelta

from utils.time_utils import utc_now_naive


@dataclass
class CacheEntry:
    value: object
    expires_at: object


class InMemoryProphetModelCache:
    def __init__(self, ttl_seconds: int, max_entries: int = 128, now_provider=utc_now_naive):
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self.now_provider = now_provider
        self._entries: dict[tuple, CacheEntry] = {}

    def get(self, key):
        now = self.now_provider()
        self.prune(now=now)
        entry = self._entries.get(key)
        if not entry:
            return None
        if entry.expires_at <= now:
            self._entries.pop(key, None)
            return None
        return entry.value

    def set(self, key, value):
        self.prune()
        if len(self._entries) >= self.max_entries:
            oldest_key = min(self._entries, key=lambda item: self._entries[item].expires_at)
            self._entries.pop(oldest_key, None)
        self._entries[key] = CacheEntry(
            value=value,
            expires_at=self.now_provider() + timedelta(seconds=self.ttl_seconds),
        )
        return value

    def evict(self, key):
        self._entries.pop(key, None)

    def prune(self, now=None):
        now = now or self.now_provider()
        expired = [key for key, entry in self._entries.items() if entry.expires_at <= now]
        for key in expired:
            self._entries.pop(key, None)
