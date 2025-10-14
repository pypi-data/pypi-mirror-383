"""Request object with convenient property access"""


class Request(dict):
    """
    Enhanced request dict with convenient property access.

    Backward compatible with dict access while providing cleaner syntax:
        request['method']  -> request.method
        request['form']    -> request.POST
        request['query']   -> request.GET
        request['cookies'] -> request.COOKIES

    Philosophy: PHP-style explicit data sources (no magic merging)
    Plus: Perl-style convenience with param() method
    """

    @property
    def method(self) -> str:
        """HTTP method: GET, POST, PUT, DELETE, etc."""
        return self.get('method', 'GET')

    @property
    def POST(self) -> dict:
        """Form data from POST body (application/x-www-form-urlencoded)"""
        return self.get('form', {})

    @property
    def GET(self) -> dict:
        """Query string parameters from URL"""
        return self.get('query', {})

    @property
    def COOKIES(self) -> dict:
        """Cookies from Cookie header"""
        return self.get('cookies', {})

    @property
    def PATH(self) -> list:
        """Path segments as list. Example: /profile/alice -> ['profile', 'alice']"""
        return self.get('path_parts', [])

    @property
    def body(self) -> bytes:
        """Raw request body as bytes"""
        return self.get('body', b'')

    @property
    def path(self) -> str:
        """Full request path"""
        return self.get('path', '/')

    def param(self, key: str, default=None):
        """
        Get parameter from POST form data first, then GET query string.

        Perl CGI.pm-style convenience method. Explicit lookup order:
        1. POST form data (request.POST)
        2. GET query string (request.GET)

        Example:
            email = request.param('email')  # Checks POST, then GET
            page = request.param('page', '1')  # With default

        This is explicit and documented - not magic!
        """
        # Check POST first (form data)
        if key in self.POST:
            return self.POST[key]

        # Then check GET (query string)
        if key in self.GET:
            return self.GET[key]

        # Return default if not found
        return default

    def cookie(self, key: str, default=None):
        """
        Get cookie value.

        Example:
            session = request.cookie('session')
        """
        return self.COOKIES.get(key, default)
