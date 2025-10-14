class BaseAuthentication:
    requires_csrf = True

    def authenticate(self, request):
        """
        Return a user object if authentication is successful.
        Otherwise return None.
        """
        raise NotImplementedError
