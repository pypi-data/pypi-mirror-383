import re
from typing import Literal


# Type alias for versioning methods
VersioningMethod = Literal["path", "header", "accept", "query", "hostname"]


class VersioningStrategy:
    """Base class for API versioning strategies"""

    @staticmethod
    def get_version(request):
        """Extract version from request. Return None if not found."""
        raise NotImplementedError


class URLPathVersioning(VersioningStrategy):
    """Version is in URL path: /api/v1/resource/"""

    @staticmethod
    def get_version(request):
        # Version is already handled by URL routing
        return getattr(request, "_api_version", None)


class HeaderVersioning(VersioningStrategy):
    """Version in custom header: X-API-Version: 1"""

    @staticmethod
    def get_version(request):
        version = request.headers.get("X-API-Version")
        if version:
            try:
                return version
            except ValueError:
                return None
        return None


class AcceptHeaderVersioning(VersioningStrategy):
    """Version in Accept header: Accept: application/vnd.myapi.v1+json"""

    @staticmethod
    def get_version(request):
        accept = request.headers.get("Accept", "")
        match = re.search(r"application/vnd\.[^.]+\.v(\d+)", accept)
        if match:
            return str(match.group(1))
        return None


class QueryParameterVersioning(VersioningStrategy):
    """Version in query parameter: ?version=1"""

    @staticmethod
    def get_version(request):
        version = request.GET.get("version")
        if version:
            try:
                return str(version)
            except ValueError:
                return None
        return None


class HostNameVersioning(VersioningStrategy):
    """Version in subdomain: v1.api.example.com"""

    @staticmethod
    def get_version(request):
        host = request.get_host().split(":")[0]  # Remove port if present
        match = re.match(r"^v(\d+)\.", host)
        if match:
            return str(match.group(1))
        return None
