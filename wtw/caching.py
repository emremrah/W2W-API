import diskcache

from wtw.helpers import validate_kwargs

cache = None


class Cache:
    """Cache class."""

    def __init__(self, path: str = "./.cache"):
        """Initialize cache."""
        self.cache = diskcache.Cache(path)

    def __contains__(self, key: str):
        """Check if key is in cache."""
        return key in self.cache

    def get(self, key: str):
        """Get value from cache."""
        return self.cache.get(key)

    def set(self, key: str, value, expire: int = 0):
        """Set value in cache."""
        self.cache.set(key, value, expire=expire)


def init_cache(**kwargs):
    """Initialize cache."""
    global cache

    if cache is not None:
        return cache

    # validate kwargs
    kwargs = validate_kwargs(kwargs, Cache.__init__)

    cache = Cache(**kwargs)

    return cache
