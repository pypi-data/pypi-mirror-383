import importlib
import inspect
import re
from typing import Optional, Type
from django.conf import settings
from django.urls import path
from django.http import Http404
from django_rad.exceptions import RouteDefinitionError
from ..controllers import BaseController
from pydantic import BaseModel as PydanticBaseModel

from .versoning import (
    VersioningMethod,
    VersioningStrategy,
    HeaderVersioning,
    AcceptHeaderVersioning,
    HostNameVersioning,
    URLPathVersioning,
    QueryParameterVersioning,
)


class route:
    """
    Unified route decorator for both API and non-API controllers.
    Includes validation to ensure required function arguments (path parameters)
    are present in the decorated URL pattern.
    """

    # Default versioning configuration
    DEFAULT_VERSIONING_METHOD: VersioningMethod = "path"
    DEFAULT_VERSION: str = "1.0.0"
    ALLOWED_VERSIONS: list[str] | None = None  # None means all versions allowed

    @staticmethod
    def filter(filterset_class):
        from django_filters import FilterSet

        """
        A decorator to attach a django-filters FilterSet directly to a view method.

        Args:
            filterset_class: A django-filters FilterSet class

        Usage:
            @route.filter(ArticleFilterSet)
            @route.api.get("test/api/")
            def index(self, request):
                ...
        """

        def decorator(func):
            # Validate that it's a FilterSet class
            if not (
                inspect.isclass(filterset_class)
                and issubclass(filterset_class, FilterSet)
            ):
                raise TypeError(
                    f"@route.filter expects a django-filters FilterSet class, "
                    f"got {type(filterset_class).__name__}"
                )
            func._filter_schema = filterset_class
            return func

        return decorator

    def __init__(
        self,
        pattern=None,
        methods=None,
        is_api=False,
        response=None,
    ):
        self.pattern = (pattern or "").strip("/")
        self.methods = [m.upper() for m in (methods or ["GET"])]
        self.is_api = is_api
        self.response_schema = response  # Store the schema

    def _validate_pattern_params(self, func):
        """
        Validates that all path-like arguments in the function signature
        are present in the URL pattern using Django's path syntax.
        """
        sig = inspect.signature(func)
        func_params = []
        for i, (name, param) in enumerate(sig.parameters.items()):
            if i < 2:
                continue
            annotation = param.annotation
            if inspect.isclass(annotation) and issubclass(
                annotation, PydanticBaseModel
            ):
                continue
            if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
                func_params.append(name)

        pattern_params = re.findall(r"<[^:]+:(\w+)>", self.pattern)

        for param_name in func_params:
            if param_name not in pattern_params:
                raise RouteDefinitionError(
                    f"Route definition error for method '{func.__qualname__}': "
                    f"Function signature requires path parameter '{param_name}', "
                    f"but it is missing from the URL pattern '{self.pattern}'. "
                    f"Expected format: <type:{param_name}>, e.g., 'user/<int:{param_name}>/'. "
                    f"Please ensure path parameters are included in the URL pattern."
                )

    def __call__(self, func):
        self._validate_pattern_params(func)
        func.route_info = {
            "pattern": self.pattern,
            "methods": self.methods,
            "is_api": self.is_api,
            "response": self.response_schema,  # Add the schema to route_info
        }
        func._is_routed = True
        return func

    # -------------------
    # Non-API shortcuts
    # -------------------
    @staticmethod
    def get(pattern=""):
        return route(pattern, ["GET"], is_api=False)

    @staticmethod
    def post(pattern=""):
        return route(pattern, ["POST"], is_api=False)

    @staticmethod
    def put(pattern=""):
        return route(pattern, ["PUT"], is_api=False)

    @staticmethod
    def patch(pattern=""):
        return route(pattern, ["PATCH"], is_api=False)

    @staticmethod
    def delete(pattern=""):
        return route(pattern, ["DELETE"], is_api=False)

    # -------------------
    # API shortcuts
    # -------------------
    class api:
        @staticmethod
        def get(pattern="", response=None):
            return route(pattern, ["GET"], is_api=True, response=response)

        @staticmethod
        def post(pattern="", response=None):
            return route(pattern, ["POST"], is_api=True, response=response)

        @staticmethod
        def put(pattern="", response=None):
            return route(pattern, ["PUT"], is_api=True, response=response)

        @staticmethod
        def patch(pattern="", response=None):
            return route(pattern, ["PATCH"], is_api=True, response=response)

        @staticmethod
        def delete(pattern="", response=None):
            return route(pattern, ["DELETE"], is_api=True, response=response)

    # -------------------
    # Skip decorators for auth/permissions
    # -------------------
    @staticmethod
    def skip_auth(func):
        """Mark a method to skip authentication"""
        func.skip_auth = True
        return func

    @staticmethod
    def skip_permissions(func):
        """Mark a method to skip permission checks"""
        func.skip_perm = True
        return func

    @staticmethod
    def cache(timeout: int):
        """
        A decorator to cache the response of an API endpoint.
        """

        def decorator(func):
            if not hasattr(func, "route_info"):
                func.route_info = {}
            func.route_info["cache_timeout"] = timeout
            return func

        return decorator

    @staticmethod
    def throttle(scope: str, num_requests: int, period: str):
        """
        A decorator to apply a specific rate limit to a view method.
        Can be stacked for multiple rate limits.

        Example: @route.throttle('user_burst', 10, 'minute')
        """

        def decorator(func):
            if not hasattr(func, "_throttle_configs"):
                func._throttle_configs = []
            valid_periods = {"second", "minute", "hour", "day"}
            if period not in valid_periods:
                raise ValueError(
                    f"Invalid period '{period}'. Use one of {valid_periods}."
                )
            rate = f"{num_requests}/{period[0]}"  # e.g., "10/m"
            func._throttle_configs.append({"scope": scope, "rate": rate})
            return func

        return decorator

    # -------------------
    # Ignore decorator
    # -------------------
    @staticmethod
    def ignore(func):
        func._route_ignore = True
        return func

    # -------------------
    # Versioning Strategy Selector
    # -------------------
    @staticmethod
    def get_versioning_strategy(method: VersioningMethod) -> Type[VersioningStrategy]:
        """Get the versioning strategy class based on method name"""
        strategies: dict[VersioningMethod, Type[VersioningStrategy]] = {
            "path": URLPathVersioning,
            "header": HeaderVersioning,
            "accept": AcceptHeaderVersioning,
            "query": QueryParameterVersioning,
            "hostname": HostNameVersioning,
        }
        return strategies.get(method, URLPathVersioning)

    @classmethod
    def _get_all_controllers(cls):
        all_controllers = []
        visited = set()

        def get_all_subclasses(base_cls):
            for subclass in base_cls.__subclasses__():
                if subclass not in visited:
                    visited.add(subclass)
                    all_controllers.append(subclass)
                    get_all_subclasses(subclass)

        try:
            get_all_subclasses(BaseController)
        except NameError:  # In case BaseController is not defined yet
            pass
        return all_controllers

    # -------------------
    # URL Collection
    # -------------------
    @classmethod
    def _auto_discover_controllers(cls):
        """
        Auto-import `views.py` and `controllers.py` from installed apps
        so controllers register themselves.
        """
        for app in settings.INSTALLED_APPS:
            if app.startswith("django."):
                continue
            for mod in ("controllers", "views"):
                try:
                    importlib.import_module(f"{app}.{mod}")
                except (ModuleNotFoundError, ImportError):
                    continue

    @classmethod
    def _get_all_controller_methods(cls, controller_cls):
        """
        Get all methods from a controller class, including inherited ones.
        """
        methods = {}
        for name, method in inspect.getmembers(
            controller_cls, predicate=inspect.isfunction
        ):
            if name.startswith("_"):
                continue
            if getattr(method, "_route_ignore", False):
                continue
            if hasattr(method, "_is_routed") and hasattr(method, "route_info"):
                methods[name] = method
        return methods

    @classmethod
    def _create_dispatcher_view(
        cls,
        version_map: dict[str, Type[BaseController]],
        versioning_method: VersioningMethod,
    ):
        """
        Creates a single view that dispatches to the correct versioned controller.
        """
        strategy = cls.get_versioning_strategy(versioning_method)

        def dispatcher_view(request, *args, **kwargs):
            request_version = strategy.get_version(request)
            if request_version is None:
                request_version = cls.DEFAULT_VERSION

            controller_cls = version_map.get(request_version)

            if not controller_cls:
                raise Http404(
                    f"API version {request_version} is not available for this endpoint."
                )

            # Instantiate and dispatch to the correct controller's view
            return controller_cls.as_view()(request, *args, **kwargs)

        return dispatcher_view

    @classmethod
    def _collect_urls(
        cls,
        api: bool = False,
        version: str | None = None,
        versioning_method: VersioningMethod = "path",
    ):
        """
        Collect URL patterns from all discovered controllers.
        """
        cls._auto_discover_controllers()

        # A dictionary to hold routes, preventing duplicates.
        # Structure: { pattern: { method_name: { version: controller_cls } } }
        routes = {}

        all_controllers = []
        visited = set()

        def get_all_subclasses(base_cls):
            for subclass in base_cls.__subclasses__():
                if subclass not in visited:
                    visited.add(subclass)
                    all_controllers.append(subclass)
                    get_all_subclasses(subclass)

        try:
            get_all_subclasses(BaseController)
        except NameError:
            pass

        # --- Step 1: Collect and group all controllers by path and method ---
        for controller_cls in all_controllers:
            methods = cls._get_all_controller_methods(controller_cls)
            for method_name, method in methods.items():
                info = method.route_info

                # Skip if it doesn't match the API type (api vs non-api)
                if (api and not info.get("is_api", False)) or (
                    not api and info.get("is_api", False)
                ):
                    continue

                pattern = info["pattern"]
                if pattern and not pattern.endswith("/"):
                    pattern += "/"

                controller_version = getattr(
                    controller_cls, "version", cls.DEFAULT_VERSION
                )

                # For path versioning, we must filter by the version specified in urls.py
                if versioning_method == "path" and version is not None:
                    if controller_version != version:
                        continue

                # Group controllers by pattern and method
                routes.setdefault(pattern, {}).setdefault(method_name, {})[
                    controller_version
                ] = controller_cls

        # --- Step 2: Build the final urlpatterns from the grouped routes ---
        urlpatterns = []
        for pattern, methods_map in routes.items():
            for method_name, version_map in methods_map.items():
                # Get a sample controller to extract route info
                sample_controller_cls = next(iter(version_map.values()))
                info = getattr(sample_controller_cls, method_name).route_info

                view_func = None
                if versioning_method == "path":
                    # For path versioning, there's only one controller per version.
                    # The version_map should only have one item.
                    controller_for_path = next(iter(version_map.values()))
                    view_func = controller_for_path.as_view()
                else:
                    # For other methods, create a dispatcher that decides at request time
                    view_func = cls._create_dispatcher_view(
                        version_map, versioning_method
                    )

                # Define the name for the URL pattern
                controller_name = sample_controller_cls.__name__.replace(
                    "ApiController", ""
                ).replace("Controller", "")
                controller_name = re.sub(
                    r"(?<!^)(?=[A-Z])", "_", controller_name
                ).lower()
                app_name = sample_controller_cls.__module__.split(".")[0]
                namespace = f"{app_name}_{controller_name}"
                if versioning_method == "path" and version is not None:
                    namespace = f"v{version}_{namespace}"

                route_kwargs = {"action": method_name, "methods": info["methods"]}

                urlpatterns.append(
                    path(
                        pattern,
                        view_func,
                        route_kwargs,
                        name=f"{namespace}_{method_name}",
                    )
                )

        return urlpatterns

    @classmethod
    def urls(cls):
        """Non-API urls"""
        return cls._collect_urls(api=False), "template", "template"

    @classmethod
    def api_urls(
        cls,
        version: str | None = None,
        versioning_method: VersioningMethod | None = None,
    ):
        """
        API urls, returns include()-ready tuple.
        """
        if versioning_method is None:
            versioning_method = cls.DEFAULT_VERSIONING_METHOD

        if versioning_method == "path" and version is None:
            raise ValueError("version parameter is required when using path versioning")

        namespace = f"api_v{version}" if version is not None else "api"
        return (
            cls._collect_urls(
                api=True,
                version=version,
                versioning_method=versioning_method,
            ),
            namespace,
            namespace,
        )

    @staticmethod
    def perm_required(*permissions):
        def decorator(func):
            func.required_permissions = permissions
            return func

        return decorator

    # -------------------
    # Generate Open API Schema
    # -------------------
    @classmethod
    def generate_openapi_schema(
        cls, version: Optional[int] = None, versioning_method: VersioningMethod = "path"
    ):
        """
        Generate an OpenAPI schema for all registered routes.

        Args:
            version: API version number to generate schema for.
            versioning_method: Versioning strategy used
        """
        version_suffix = f" v{version}" if version is not None else ""
        schema = {
            "openapi": "3.0.0",
            "info": {
                "title": f"Django Rails-like API{version_suffix}",
                "version": f"{version}.0.0" if version else "1.0.0",
                "description": f"Auto-generated OpenAPI schema for Django controllers\nVersioning method: {versioning_method}",
            },
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "SessionAuthentication": {
                        "type": "apiKey",
                        "in": "cookie",
                        "name": "sessionid",
                    }
                },
            },
        }

        # Add versioning parameter to schema based on method
        if versioning_method == "header":
            schema["components"]["parameters"] = {
                "ApiVersion": {
                    "name": "X-API-Version",
                    "in": "header",
                    "required": True,
                    "schema": {"type": "integer"},
                    "description": "API version number",
                }
            }
        elif versioning_method == "query":
            schema["components"]["parameters"] = {
                "ApiVersion": {
                    "name": "version",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "integer"},
                    "description": "API version number",
                }
            }
        elif versioning_method == "accept":
            schema["info"]["description"] += (
                "\nUse Accept header: application/vnd.myapi.v{version}+json"
            )

        cls._auto_discover_controllers()
        all_controllers = []
        visited = set()

        def get_all_subclasses(base_cls):
            for subclass in base_cls.__subclasses__():
                if subclass not in visited:
                    visited.add(subclass)
                    all_controllers.append(subclass)
                    get_all_subclasses(subclass)

        try:
            get_all_subclasses(BaseController)
        except NameError:
            pass

        for controller_cls in all_controllers:
            # Filter by version if specified
            if version is not None:
                controller_version = getattr(controller_cls, "version", None)
                if controller_version != version:
                    continue

            methods = cls._get_all_controller_methods(controller_cls)
            for method_name, method in methods.items():
                info = method.route_info
                if info.get("is_api", False):
                    pattern = info["pattern"]
                    if not pattern.startswith("/"):
                        pattern = f"/{pattern}"
                    if pattern and not pattern.endswith("/"):
                        pattern = f"{pattern}/"

                    if pattern not in schema["paths"]:
                        schema["paths"][pattern] = {}

                    for http_method in info["methods"]:
                        method_key = http_method.lower()
                        operation = {
                            "tags": [controller_cls.__name__.replace("Controller", "")],
                            "summary": f"{method_name} {controller_cls.__name__}",
                            "responses": {
                                "200": {
                                    "description": "Successful response",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "object",
                                                "properties": {},
                                            }
                                        }
                                    },
                                }
                            },
                        }

                        # Add version parameter reference for header/query versioning
                        if versioning_method in ["header", "query"]:
                            operation["parameters"] = [
                                {"$ref": "#/components/parameters/ApiVersion"}
                            ]

                        schema["paths"][pattern][method_key] = operation

                        sig = inspect.signature(method)
                        for param_name, param in sig.parameters.items():
                            if param_name in ("self", "request"):
                                continue
                            annotation = param.annotation
                            if inspect.isclass(annotation) and issubclass(
                                annotation, PydanticBaseModel
                            ):
                                schema_name = annotation.__name__
                                if schema_name not in schema["components"]["schemas"]:
                                    schema["components"]["schemas"][schema_name] = {
                                        "type": "object",
                                        "properties": cls._pydantic_model_to_openapi(
                                            annotation
                                        ),
                                    }
                                schema["paths"][pattern][method_key]["requestBody"] = {
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": f"#/components/schemas/{schema_name}"
                                            }
                                        }
                                    },
                                    "required": True,
                                }

                        if getattr(controller_cls, "authentication_classes", None):
                            schema["paths"][pattern][method_key]["security"] = [
                                {"SessionAuthentication": []}
                            ]

        return schema

    @staticmethod
    def _pydantic_model_to_openapi(model):
        """Convert a Pydantic model to an OpenAPI schema."""
        properties = {}
        for field_name, field_info in model.model_fields.items():
            field_type = field_info.annotation
            if field_type is int:
                properties[field_name] = {"type": "integer"}
            elif field_type is str:
                properties[field_name] = {"type": "string"}
            elif field_type is bool:
                properties[field_name] = {"type": "boolean"}
            elif field_type is list:
                properties[field_name] = {"type": "array", "items": {"type": "string"}}
            elif inspect.isclass(field_type) and issubclass(
                field_type, PydanticBaseModel
            ):
                properties[field_name] = {
                    "$ref": f"#/components/schemas/{field_type.__name__}"
                }
            else:
                properties[field_name] = {"type": "string"}
        return properties

    @classmethod
    def _docs(
        cls,
        url_prefix: str,
        version: Optional[int] = None,
        versioning_method: VersioningMethod = "path",
    ):
        """
        Register OpenAPI documentation endpoints with a given prefix.

        Args:
            url_prefix: URL prefix for documentation
            version: API version number for documentation
            versioning_method: Versioning strategy used
        """
        from django.urls import path
        from django.views.generic import TemplateView
        from django.http import JsonResponse

        prefix = url_prefix.strip("/")

        def openapi_json(request):
            schema = cls.generate_openapi_schema(
                version=version, versioning_method=versioning_method
            )
            return JsonResponse(schema)

        openapi_urls = [
            path(f"{prefix}/openapi.json", openapi_json, name="openapi_json"),
            path(
                f"{prefix}/",
                TemplateView.as_view(
                    template_name="rad/swagger-ui.html",
                    extra_context={"openapi_json_url": "openapi.json"},
                ),
                name="swagger_ui",
            ),
        ]
        return openapi_urls

    @classmethod
    def docs(
        cls,
        prefix: str = "docs",
        version: Optional[int] = None,
        versioning_method: VersioningMethod = "path",
    ):
        """
        Returns a list of URL patterns for API documentation.

        Args:
            prefix: URL prefix for documentation
            version: API version number for documentation
            versioning_method: Versioning strategy used
        """
        return cls._docs(prefix, version=version, versioning_method=versioning_method)
