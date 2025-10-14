"""Filesystem-based routing - like CGI but async"""
import importlib.util
import urllib.parse
from pathlib import Path
from .settings import BASE_DIR
from .responses import html, text
from .templating import render
from .static import serve_static
from .request import Request


def parse_query_string(query_string: str) -> dict:
    """Parse URL query string into dict"""
    if not query_string:
        return {}
    return dict(urllib.parse.parse_qsl(query_string))


def parse_form_data(body: bytes, content_type: str) -> dict:
    """Parse form data from request body"""
    if not body:
        return {}

    # Handle application/x-www-form-urlencoded
    if "application/x-www-form-urlencoded" in content_type:
        return dict(urllib.parse.parse_qsl(body.decode("utf-8")))

    # Handle multipart/form-data (requires python-multipart)
    if "multipart/form-data" in content_type:
        try:
            from multipart import parse_form_data as parse_multipart
            # TODO: Implement multipart parsing
            return {}
        except ImportError:
            return {}

    return {}


def parse_cookies(headers: list) -> dict:
    """Parse cookies from request headers"""
    cookies = {}
    for name, value in headers:
        if name.lower() == b"cookie":
            cookie_str = value.decode("utf-8") if isinstance(value, bytes) else value
            for cookie in cookie_str.split(";"):
                cookie = cookie.strip()
                if "=" in cookie:
                    key, val = cookie.split("=", 1)
                    cookies[key.strip()] = val.strip()
    return cookies


def route(scope: dict, body: bytes = b"") -> tuple[int, list, list]:
    """
    Route a request based on filesystem conventions.

    Routing order:
    1. API handlers: api/{path}.py or parent api handlers
    2. Templates: templates/{path}.html
    3. Static files: public/{path}
    4. 404

    API handlers can handle sub-paths:
    - /user/123 → api/user.py gets request with path_parts=['user', '123']
    """
    method = scope["method"]
    path = scope["path"]
    query_string = scope.get("query_string", b"").decode("utf-8")
    headers = scope.get("headers", [])

    # Get content type for form parsing
    content_type = ""
    for name, value in headers:
        if name.lower() == b"content-type":
            content_type = value.decode("utf-8") if isinstance(value, bytes) else value
            break

    # Clean path
    clean_path = path.strip("/")
    path_parts = [p for p in clean_path.split("/") if p] if clean_path else []

    # Build request context
    request = Request({
        "method": method,
        "path": path,
        "path_parts": path_parts,
        "query": parse_query_string(query_string),
        "form": parse_form_data(body, content_type),
        "cookies": parse_cookies(headers),
        "body": body,
        "scope": scope,
    })

    # 1. Try API handlers (with hierarchical fallback)
    api_result = try_api_handler(path_parts, request)
    if api_result:
        return api_result

    # 2. Try templates (GET only)
    if method == "GET":
        template_result = try_template(path_parts)
        if template_result:
            return template_result

    # 3. Try static files (GET only)
    if method == "GET":
        static_result = serve_static(clean_path)
        if static_result[0] != 404:
            return static_result

    # 4. 404
    return 404, [("content-type", "text/plain")], [b"Not Found"]


def try_api_handler(path_parts: list[str], request: dict):
    """
    Try to find an API handler, checking from most specific to least specific.

    For /user/123/edit:
    1. Try api/user/123/edit.py
    2. Try api/user/123.py (pass ['user', '123', 'edit'])
    3. Try api/user.py (pass ['user', '123', 'edit'])
    4. Try api.py (pass ['user', '123', 'edit'])
    """
    api_dir = BASE_DIR / "api"

    if not path_parts:
        # Root path: try api.py only (skip __init__.py as it's just a package marker)
        root_handler = BASE_DIR / "api.py"
        if root_handler.exists():
            return load_and_call_handler(root_handler, request)
        return None

    # Try increasingly general paths
    for i in range(len(path_parts), 0, -1):
        # Build path to handler
        partial_path = "/".join(path_parts[:i])
        handler_file = api_dir / f"{partial_path}.py"

        if handler_file.exists():
            # Update request with remaining path parts
            request["matched_parts"] = path_parts[:i]
            request["remaining_parts"] = path_parts[i:]
            return load_and_call_handler(handler_file, request)

    # Try root api handler
    root_handler = BASE_DIR / "api.py"
    if root_handler.exists():
        return load_and_call_handler(root_handler, request)

    return None


def load_and_call_handler(handler_file: Path, request: dict):
    """Load a Python module and call its handle() function"""
    try:
        spec = importlib.util.spec_from_file_location("handler", handler_file)
        if not spec or not spec.loader:
            return 500, [("content-type", "text/plain")], [b"Failed to load handler"]

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "handle"):
            return 500, [("content-type", "text/plain")], [b"Handler missing handle() function"]

        result = module.handle(request)

        # Support various return formats
        if isinstance(result, tuple) and len(result) == 3:
            return result
        else:
            return 500, [("content-type", "text/plain")], [b"Invalid handler return format"]

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return 500, [("content-type", "text/plain")], [f"Handler error: {e}\n\n{tb}".encode()]


def try_template(path_parts: list[str]):
    """Try to render a template"""
    if not path_parts:
        # Root: try index.html
        template_name = "index.html"
    else:
        # Try exact path
        template_name = "/".join(path_parts)
        if not template_name.endswith(".html"):
            template_name += ".html"

    template_file = BASE_DIR / "templates" / template_name

    if template_file.exists():
        try:
            rendered = render(template_name)
            return html(rendered)
        except Exception as e:
            return 500, [("content-type", "text/plain")], [f"Template error: {e}".encode()]

    return None
