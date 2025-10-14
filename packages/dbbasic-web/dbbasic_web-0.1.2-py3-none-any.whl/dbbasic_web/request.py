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
