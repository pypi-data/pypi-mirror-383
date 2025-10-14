# openapi_generator.py
import inspect
import os
import importlib
import re
from django.views import View
from django.urls import URLPattern, URLResolver
from django.http import JsonResponse
from django_rad.controllers import ApiController  # Your base controller


# ----------------------------
# Serializer to schema helper
# ----------------------------
def serializer_to_schema(serializer):
    schema = {"type": "object", "properties": {}}
    if inspect.isclass(serializer):
        serializer = serializer()
    if hasattr(serializer, "fields"):
        for name, field in serializer.fields.items():
            if hasattr(field, "fields"):  # nested serializer
                schema["properties"][name] = serializer_to_schema(field)
            else:
                schema["properties"][name] = {"type": "string"}
    return schema


# ----------------------------
# Parameter inference
# ----------------------------
def infer_parameters(func, url_pattern: str):
    """Infer parameters from function signature and URL pattern."""
    sig = inspect.signature(func)
    parameters = []

    # Extract path params from Django URL pattern <int:id>, <str:slug>, etc.
    path_params = re.findall(r"<(?:[^:]+:)?([^>]+)>", url_pattern)

    for name in path_params:
        # Determine type from URL pattern
        param_type = "string"
        if f"<int:{name}>" in url_pattern:
            param_type = "integer"
        elif f"<uuid:{name}>" in url_pattern:
            param_type = "string"

        parameters.append(
            {
                "name": name,
                "in": "path",
                "required": True,
                "schema": {"type": param_type},
            }
        )

    # Add query params from function signature
    for name, param in sig.parameters.items():
        if name in ("self", "request") or name in path_params:
            continue
        parameters.append(
            {
                "name": name,
                "in": "query",
                "required": param.default == inspect.Parameter.empty,
                "schema": {"type": "string"},
            }
        )
    return parameters


# ----------------------------
# Get URL path string (handles path() and re_path())
# ----------------------------
def get_path_pattern(entry):
    """Extract URL pattern string from URLPattern."""
    pattern_obj = entry.pattern
    if hasattr(pattern_obj, "_route"):  # path() style
        return pattern_obj._route
    elif hasattr(pattern_obj, "regex"):  # re_path() style
        return pattern_obj.regex.pattern.lstrip("^").rstrip("$")
    else:
        return str(pattern_obj)


# ----------------------------
# Get controller class from callback
# ----------------------------
def get_controller_class(callback):
    """
    Extract the controller class from a Django view callback.
    Works with controller.as_view() pattern.
    """
    # Check if it's a view function from as_view()
    if hasattr(callback, "view_class"):
        return callback.view_class

    # Check closure for view_class (as_view pattern)
    if hasattr(callback, "__closure__") and callback.__closure__:
        for cell in callback.__closure__:
            try:
                cell_content = cell.cell_contents
                if inspect.isclass(cell_content):
                    return cell_content
            except (AttributeError, ValueError):
                continue

    return None


# ----------------------------
# Check if controller is ApiController subclass
# ----------------------------
def is_apicontroller(controller_cls):
    """Check if a class is a subclass of ApiController."""
    if not controller_cls or not inspect.isclass(controller_cls):
        return False
    try:
        return issubclass(controller_cls, ApiController)
    except TypeError:
        return False


# ----------------------------
# Get controller method from action name
# ----------------------------
def get_controller_method(controller_cls, action_name):
    """Get the actual method from controller class by action name."""
    if not controller_cls:
        return None
    return getattr(controller_cls, action_name, None)


# ----------------------------
# Extract HTTP methods from entry
# ----------------------------
def get_http_methods(entry):
    """
    Extract HTTP methods from URLPattern.
    Looks in default_args for methods key.
    """
    # Check default_args (set by register_controller)
    if hasattr(entry, "default_args") and isinstance(entry.default_args, dict):
        methods = entry.default_args.get("methods")
        if methods:
            return methods if isinstance(methods, list) else [methods]

    # Check callback attributes
    callback = entry.callback
    if hasattr(callback, "methods"):
        methods = callback.methods
        return methods if isinstance(methods, list) else [methods]

    # Default to common methods
    return ["GET"]


# ----------------------------
# Generate OpenAPI spec
# ----------------------------
def generate_openapi_from_urlpatterns(urlpatterns):
    """
    Scans all urlpatterns, includes only callbacks from ApiController subclasses.
    """
    openapi = {
        "openapi": "3.0.0",
        "info": {"title": "My API", "version": "1.0.0"},
        "paths": {},
        "components": {
            "securitySchemes": {
                "sessionAuth": {"type": "apiKey", "in": "cookie", "name": "sessionid"}
            }
        },
    }

    def recursive_scan(urlpatterns, prefix=""):
        for entry in urlpatterns:
            if isinstance(entry, URLPattern):
                path_str = prefix + get_path_pattern(entry)
                callback = entry.callback

                # Get controller class from callback
                controller_cls = get_controller_class(callback)

                # Check if it's an ApiController
                if not is_apicontroller(controller_cls):
                    continue

                # Get action name from default_args
                action_name = None
                if hasattr(entry, "default_args") and isinstance(
                    entry.default_args, dict
                ):
                    action_name = entry.default_args.get("action")

                if not action_name:
                    continue

                # Get the actual method
                method_func = get_controller_method(controller_cls, action_name)
                if not method_func:
                    continue

                # Get HTTP methods
                http_methods = get_http_methods(entry)

                # Generate parameters
                parameters = infer_parameters(method_func, path_str)

                # Convert Django path format to OpenAPI format
                # <int:id> -> {id}, <str:slug> -> {slug}, etc.
                openapi_path = re.sub(r"<(?:[^:]+:)?([^>]+)>", r"{\1}", path_str)

                # Ensure path starts with /
                openapi_path = (
                    f"/{openapi_path}"
                    if not openapi_path.startswith("/")
                    else openapi_path
                )

                # Initialize path entry
                if openapi_path not in openapi["paths"]:
                    openapi["paths"][openapi_path] = {}

                # Add operation for each HTTP method
                for http_method in http_methods:
                    method_lower = http_method.lower()

                    # Build operation object
                    operation = {
                        "summary": f"{action_name}",
                        "operationId": f"{controller_cls.__name__}_{action_name}_{method_lower}",
                        "parameters": parameters,
                        "responses": {
                            "200": {"description": "Successful response"},
                            "401": {"description": "Unauthorized"},
                            "403": {"description": "Forbidden"},
                            "404": {"description": "Not found"},
                        },
                        "security": [{"sessionAuth": []}],
                    }

                    # Add request body for POST/PUT/PATCH
                    if http_method in ["POST", "PUT", "PATCH"]:
                        operation["requestBody"] = {
                            "required": True,
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            },
                        }

                    openapi["paths"][openapi_path][method_lower] = operation

            elif isinstance(entry, URLResolver):
                nested_prefix = prefix + get_path_pattern(entry)
                recursive_scan(entry.url_patterns, prefix=nested_prefix)

    recursive_scan(urlpatterns)
    return openapi


# ----------------------------
# Dynamically import root urlpatterns
# ----------------------------
def get_root_urlpatterns():
    """Import urlpatterns from Django settings."""
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    if not settings_module:
        raise RuntimeError("DJANGO_SETTINGS_MODULE not set")

    project_root = settings_module.split(".")[0]
    urls_module_path = f"{project_root}.urls"
    urls_module = importlib.import_module(urls_module_path)
    return getattr(urls_module, "urlpatterns")


# ----------------------------
# Django view
# ----------------------------
class OpenAPISchemaView(View):
    """
    Global OpenAPI generator based on the project's urlpatterns.
    """

    def get(self, request, *args, **kwargs):
        try:
            urlpatterns = get_root_urlpatterns()
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        schema = generate_openapi_from_urlpatterns(urlpatterns)
        return JsonResponse(schema, json_dumps_params={"indent": 2})
