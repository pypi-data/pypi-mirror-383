from .base import BaseAuthentication


class SessionAuthentication(BaseAuthentication):
    requires_csrf = True  # header-based, no CSRF needed

    def authenticate(self, request):
        return getattr(request, "user", None) if request.user.is_authenticated else None
