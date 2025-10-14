import time
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from .settings import rad_api_settings


class Throttled(PermissionDenied):
    def __init__(self, wait=None):
        self.wait = wait
        detail = f"Request was throttled. Expected available in {wait:.2f} seconds."
        super().__init__(detail)


class BaseThrottle:
    def allow_request(self, request, view):
        raise NotImplementedError(".allow_request() must be implemented")

    def get_ident(self, request):
        if request.user and request.user.is_authenticated:
            return request.user.pk
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        remote_addr = request.META.get("REMOTE_ADDR")
        return "".join(xff.split()) if xff else remote_addr

    def wait(self):
        return None


class ScopedRateThrottle(BaseThrottle):
    scope = None

    def __init__(self):
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)

    def get_rate(self):
        try:
            return rad_api_settings.THROTTLING["RATES"][self.scope]
        except KeyError:
            raise Exception(f"No throttle rate configured for scope '{self.scope}'")

    def parse_rate(self, rate):
        if rate is None:
            return (None, None)
        num, period = rate.split("/")
        num_requests = int(num)
        duration = {"s": 1, "m": 60, "h": 3600, "d": 86400}[period[0]]
        return (num_requests, duration)

    def get_cache_key(self, request, view):
        return f"throttle_{self.scope}_{self.get_ident(request)}"

    def allow_request(self, request, view):
        if self.rate is None:
            return True
        self.key = self.get_cache_key(request, view)
        self.history = cache.get(self.key, [])
        self.now = time.time()
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()

    def throttle_success(self):
        self.history.insert(0, self.now)
        cache.set(self.key, self.history, self.duration)
        return True

    def throttle_failure(self):
        return False

    def wait(self):
        if self.history:
            return self.duration - (self.now - self.history[-1])
        return None


class DecoratorRateThrottle(BaseThrottle):
    """
    A throttle class that gets its rate and scope directly from the
    decorator, not from settings.
    """

    def __init__(self, scope, rate):
        self.scope = scope
        self.rate = rate
        self.num_requests, self.duration = self.parse_rate(self.rate)

    def parse_rate(self, rate):
        num, period = rate.split("/")
        num_requests = int(num)
        duration = {"s": 1, "m": 60, "h": 3600, "d": 86400}[period[0]]
        return (num_requests, duration)

    def get_cache_key(self, request, view):
        # The scope makes the cache key unique for each decorator
        return f"throttle_{self.scope}_{self.get_ident(request)}"

    def allow_request(self, request, view):
        # This logic is copied from ScopedRateThrottle and works the same way
        self.key = self.get_cache_key(request, view)
        self.history = cache.get(self.key, [])
        self.now = time.time()
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()

    def throttle_success(self):
        self.history.insert(0, self.now)
        cache.set(self.key, self.history, self.duration)
        return True

    def throttle_failure(self):
        return False

    def wait(self):
        if self.history:
            return self.duration - (self.now - self.history[-1])
        return None
