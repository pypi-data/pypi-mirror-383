import hashlib
from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.http import JsonResponse

from django_rad.exceptions import AutenticationError
from django_rad.settings import rad_api_settings
from django_rad.throttling import DecoratorRateThrottle, Throttled
from django.core.exceptions import PermissionDenied


# -------------------
# Throttling Mixin
# -------------------
class ThrottlingMixin:
    throttle_classes: list = []

    def get_throttles(self, handler):
        """
        Builds a list of throttle instances to check against.
        Prioritizes @route.throttle decorators, then falls back.
        """
        # 1. Check for @route.throttle decorators
        decorator_configs = getattr(handler, "_throttle_configs", None)
        if decorator_configs:
            # If decorators are present, use them exclusively
            return [DecoratorRateThrottle(**config) for config in decorator_configs]

        # 2. Fall back to controller-level throttle_classes
        if self.throttle_classes:
            return self._build_throttles_from_config(self.throttle_classes)

        # 3. Fall back to global settings
        return rad_api_settings.THROTTLING["DEFAULT_CLASSES"]

    def _build_throttles_from_config(self, config_list):
        """Helper to instantiate throttles from the (Class, scope) tuple format."""
        throttles = []
        for throttle_config in config_list:
            if isinstance(throttle_config, tuple):
                throttle_class, scope = throttle_config
                throttle = throttle_class()
                throttle.scope = scope
            else:
                throttle_class = throttle_config
                throttle = throttle_class()
            throttles.append(throttle)
        return throttles

    def _check_throttles(self, request, handler):
        """
        Checks the request against the resolved list of throttle instances.
        """
        for throttle in self.get_throttles(handler):
            if not throttle.allow_request(request, self):
                raise Throttled(wait=throttle.wait())
        return None


# -------------------
# Auth / Permission Mixin
# -------------------
class AuthPermissionMixin:
    authentication_classes: list = []
    permission_classes: list = []
    skip_authentication_for: list[str] = []
    skip_permissions_for: list[str] = []

    def error_response(self, message: dict[str, Any] | str, status: int = 400):
        raise NotImplementedError()

    def _perform_authentication(self, request, handler, action: str):
        """Authenticates the user and sets request.user."""
        if (
            not getattr(handler, "skip_auth", False)
            and action not in self.skip_authentication_for
        ):
            user = None
            for auth_class in self.authentication_classes:
                authenticator = auth_class()
                user = authenticator.authenticate(request)
                if user:
                    break
            request.user = user or AnonymousUser()
        else:
            request.user = getattr(request, "user", AnonymousUser())

    def _check_permissions(self, request, handler, action: str) -> JsonResponse | None:
        """
        Checks both general permission_classes and method-specific required_permissions.
        Returns JsonResponse error if forbidden.
        """

        if getattr(handler, "skip_perm", False) or action in self.skip_permissions_for:
            return None

        # 1. Check method-specific required_permissions (from @route.perm_required)
        required_perms = getattr(handler, "required_permissions", [])

        if required_perms:
            user = request.user
            if not user or not user.is_authenticated:
                raise AutenticationError()

            # Use Django's has_perms method to check against the list
            if not user.has_perms(required_perms):
                raise PermissionDenied()

        # 2. Check general permission_classes (e.g., IsAuthenticated)
        for perm_class in self.permission_classes:
            perm = perm_class()
            if not perm.has_permission(request, self):
                raise PermissionDenied()

        return None  # Permissions passed


# -------------------
# Cache Mixin
# -------------------
class CachingMixin:
    """
    A mixin that adds response caching to a controller.
    It checks for a cached response before calling the main dispatch logic.
    """

    def dispatch(self, request, *args, **kwargs):
        handler = self._get_handler_for_dispatch(request, **kwargs)
        if not handler:
            # Fallback to super if handler can't be determined early
            return super().dispatch(request, *args, **kwargs)

        # Check for a cache timeout defined on the view method
        cache_timeout = getattr(handler, "route_info", {}).get("cache_timeout")

        if cache_timeout is not None and request.method == "GET":
            # Create a unique cache key based on the path and query parameters
            query_params = request.GET.urlencode()
            path_info = request.path_info

            key_string = f"{path_info}?{query_params}"
            cache_key = f"rad_api_cache_{hashlib.md5(key_string.encode()).hexdigest()}"

            # 1. Check for a cache hit
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response

            # 2. Cache Miss: Execute the main logic by calling super()
            response = super().dispatch(request, *args, **kwargs)

            # Only cache successful (2xx) responses
            if 200 <= response.status_code < 300:
                cache.set(cache_key, response, timeout=cache_timeout)

            return response

        # If caching is not applicable, proceed to the main dispatch logic
        return super().dispatch(request, *args, **kwargs)

    def _get_handler_for_dispatch(self, request, **kwargs):
        """Helper to safely get the handler method without running full dispatch."""
        action = kwargs.get("action", None)
        if action:
            return getattr(self, action, None)
        return None
