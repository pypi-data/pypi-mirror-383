import json
import inspect
from typing import Callable
from django.http import JsonResponse


import re
import inspect
from typing import Callable
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse


import re
from django.shortcuts import render
from django.db.models import Q

from django.core.exceptions import PermissionDenied
import pydantic


from .mixins import (
    CachingMixin,
    AuthPermissionMixin,
    ThrottlingMixin,
)
from math import ceil
from typing import Any, Type
from django.db.models import QuerySet
from django.http import QueryDict
from django.views import View
from django.urls import path

from django_rad.exceptions import AutenticationError
from django.views.decorators.csrf import csrf_exempt
from django_filters import FilterSet


# -------------------
# Base Controller
# -------------------
class BaseController(View):
    base_routes = {
        "index": {"pattern": "", "methods": ["GET"]},
        "show": {"pattern": "<int:id>/", "methods": ["GET"]},
        "create": {"pattern": "create/", "methods": ["POST"]},
        "update": {"pattern": "<int:id>/update/", "methods": ["POST", "PUT", "PATCH"]},
        "destroy": {"pattern": "<int:id>/delete/", "methods": ["POST", "DELETE"]},
    }

    response_type = "api"

    def _get_allowed_methods(self, action: str) -> list[str]:
        """Get allowed methods from route decorator or base routes"""
        # First check if the handler has route_info from decorator
        if hasattr(self, action):
            handler = getattr(self, action)
            if hasattr(handler, "route_info"):
                return handler.route_info.get("methods", ["GET"])

        # Fallback to base routes
        routes = self.__class__.get_routes()
        if action in routes:
            return routes[action]["methods"]
        return ["GET"]

    def render_template(
        self,
        context: dict,
        template_name: str | None = None,
        status: int = 200,
    ):
        raise NotImplementedError()

    @classmethod
    def get_routes(cls) -> dict[str, dict[str, Any]]:
        routes = {}
        for name, conf in cls.base_routes.items():
            if name in cls.__dict__:
                routes[name] = conf
        for name, attr in cls.__dict__.items():
            if callable(attr) and not name.startswith("_") and name not in routes:
                routes[name] = {"pattern": f"{name}/", "methods": ["GET"]}
        return routes

    @classmethod
    def get_urls(cls, prefix: str = "") -> list:
        urlpatterns = []
        controller_view = cls.as_view()
        routes = cls.get_routes()
        for action, conf in routes.items():
            pattern = conf["pattern"]
            urlpatterns.append(
                path(
                    f"{prefix}/{pattern}" if pattern else f"{prefix}/",
                    controller_view,
                    {"action": action},
                    name=action,
                )
            )
        return urlpatterns

    @property
    def urls(self) -> list:
        return self.get_urls()

    def response(self, data: dict | Any, status: int = 200, **kwargs):
        if self.response_type == "template":
            return self.render_template(data, **kwargs)

        return JsonResponse(data, status=status, safe=False)

    def error_response(
        self,
        detail: str,
        status: int = 400,
        code: str | None = None,
        title: str | None = None,
    ):
        """
        JSON:API-compliant error response.
        """
        if not title:
            # Default title based on status
            titles = {
                400: "Bad Request",
                401: "Unauthorized",
                403: "Forbidden",
                404: "Not Found",
                500: "Internal Server Error",
            }
            title = titles.get(status, "Error")

        if not code:
            # default code is a lowercase snake_case version of title
            code = title.lower().replace(" ", "_")

        return JsonResponse(
            {
                "errors": [
                    {
                        "status": str(status),
                        "code": code,
                        "title": title,
                        "detail": detail,
                    }
                ]
            },
            status=status,
        )

    def response_400(self, detail: str, code: str = "bad_request"):
        return self.error_response(detail, status=400, code=code, title="Bad Request")

    def response_401(self, detail: str, code: str = "unauthorized"):
        return self.error_response(detail, status=401, code=code, title="Unauthorized")

    def response_403(self, detail: str, code: str = "forbidden"):
        return self.error_response(detail, status=403, code=code, title="Forbidden")

    def response_404(self, detail: str, code: str = "not_found"):
        return self.error_response(detail, status=404, code=code, title="Not Found")

    def response_405(self, detail: str = "Method not allowed"):
        return self.error_response(
            detail, status=405, code="method_not_allowed", title="Method Not Allowed"
        )

    def response_500(self, detail: str, code: str = "server_error"):
        return self.error_response(
            detail, status=500, code=code, title="Internal Server Error"
        )

    # -------------------
    # Pagination Helpers
    # -------------------
    def paginate(
        self,
        queryset: QuerySet,
        serializer: Type | None = None,
        per_page: int = 10,
        page_param: str = "page",
        per_page_param: str = "per_page",
    ) -> dict:
        request: Any = self.request
        params: QueryDict = request.GET
        page = int(params.get(page_param, 1))
        per_page = int(params.get(per_page_param, per_page))
        total = queryset.count()
        total_pages = ceil(total / per_page) if per_page else 1
        start = (page - 1) * per_page
        end = start + per_page
        results = queryset[start:end]

        if serializer:
            if hasattr(serializer, "serializer_many"):
                results = serializer.serializer_many(results)
            elif callable(serializer):
                results = [serializer(obj) for obj in results]

        return {
            "results": results,
            "pagination": {
                "total": total,
                "per_page": per_page,
                "current_page": page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }

    def paginate_limit_offset(
        self,
        queryset,
        serializer: Type | None = None,
        default_limit: int = 10,
        limit_param: str = "limit",
        offset_param: str = "offset",
    ) -> dict:
        request: Any = self.request
        params: QueryDict = request.GET
        limit = int(params.get(limit_param, default_limit))
        offset = int(params.get(offset_param, 0))
        total = queryset.count()
        results = queryset[offset : offset + limit]

        if serializer:
            if hasattr(serializer, "serializer_many"):
                results = serializer.serializer_many(results)
            elif callable(serializer):
                results = [serializer(obj) for obj in results]

        return {
            "results": results,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_next": offset + limit < total,
                "has_prev": offset > 0,
            },
        }

    # -------------------
    # Filtering Helper
    def filter_queryset(self, queryset):
        """
        Filters a queryset using a two-stage pipeline:
        1. Applies filters from django-filters FilterSet if attached via @route.filter.
        2. Applies dynamic filters from `filterset_fields`, fully supporting __in, OR, and related fields.
        """
        handler = getattr(self, "_current_handler", None)
        action = getattr(self, "_current_action", None)
        params = self.request.GET.dict()

        # --- Stage 1: Django-Filters FilterSet ---
        filterset_class = None
        if handler:
            filterset_class = getattr(handler, "_filter_schema", None)
        if not filterset_class:
            controller_filters = getattr(self, "filter_schema", None)
            if isinstance(controller_filters, dict) and action:
                filterset_class = controller_filters.get(action)
            elif inspect.isclass(controller_filters) and issubclass(
                controller_filters, FilterSet
            ):
                filterset_class = controller_filters

        # Apply django-filters FilterSet if available
        if filterset_class and issubclass(filterset_class, FilterSet):
            # Normalize query parameters to match FilterSet field names
            # Extract base field names from lookup expressions like title__icontains
            normalized_params = {}
            filterset_fields = filterset_class.get_fields()

            for param_key, param_value in self.request.GET.items():
                matched = False

                # Check if param matches any filterset field directly
                if param_key in filterset_fields:
                    normalized_params[param_key] = param_value
                    matched = True
                else:
                    # Try to extract base field from Django ORM-style lookups
                    # e.g., title__icontains -> check if 'title' field exists
                    if "__" in param_key:
                        parts = param_key.split("__")
                        # Try progressively shorter field names
                        for i in range(len(parts), 0, -1):
                            potential_field = "__".join(parts[:i])
                            if potential_field in filterset_fields:
                                # Map the lookup to the base field
                                normalized_params[potential_field] = param_value
                                matched = True
                                break

                # If not matched, keep original (for pagination, ordering, etc.)
                if not matched:
                    normalized_params[param_key] = param_value

            # Create a new QueryDict-like object with normalized params
            from django.http import QueryDict

            normalized_query = QueryDict(mutable=True)
            for key, value in normalized_params.items():
                if isinstance(value, list):
                    normalized_query.setlist(key, value)
                else:
                    normalized_query[key] = value

            filterset = filterset_class(normalized_query, queryset=queryset)
            if filterset.is_valid() or not filterset.errors:
                queryset = filterset.qs

        # --- Stage 2: Dynamic Filtering with Q objects (dict-based) ---
        all_filter_fields = getattr(self, "filterset_fields", {})
        if all_filter_fields:
            fields_to_use = {}
            if (
                action
                and action in all_filter_fields
                and isinstance(all_filter_fields.get(action), dict)
            ):
                fields_to_use = all_filter_fields.get(action, {})
            else:
                fields_to_use = all_filter_fields

            if fields_to_use:
                combined_q = Q()
                for query_key, query_value in params.items():
                    for allowed_field, allowed_lookups in fields_to_use.items():
                        if query_key == allowed_field or query_key.startswith(
                            f"{allowed_field}__"
                        ):
                            # Determine base field and lookup
                            if "__" in query_key:
                                base_field, lookup = query_key.rsplit("__", 1)
                            else:
                                base_field, lookup = query_key, "exact"

                            if lookup not in allowed_lookups:
                                break

                            # Build Q object based on lookup
                            if lookup == "in":
                                values = [v for v in query_value.split(",") if v]
                                if values:
                                    q_obj = Q()
                                    for val in values:
                                        q_obj |= Q(**{base_field: val})
                            elif lookup in [
                                "icontains",
                                "contains",
                                "startswith",
                                "istartswith",
                                "endswith",
                                "iendswith",
                            ]:
                                q_obj = Q(**{query_key: query_value})
                            elif lookup in ["lte", "gte", "lt", "gt"]:
                                try:
                                    numeric_value = float(query_value)
                                except ValueError:
                                    numeric_value = query_value
                                q_obj = Q(**{query_key: numeric_value})
                            else:  # exact or other direct lookups
                                q_obj = Q(**{query_key: query_value})

                            # Combine each filter with AND
                            combined_q &= q_obj
                            break

                if combined_q:
                    try:
                        queryset = queryset.filter(combined_q)
                    except (ValueError, TypeError):
                        return queryset.none()

        return queryset


# -------------------
# ApiController
# -------------------
class ApiController(
    BaseController,
    ThrottlingMixin,
    AuthPermissionMixin,
    CachingMixin,
):
    authentication_classes: list = []
    permission_classes: list = []
    skip_authentication_for: list[str] = []
    skip_permissions_for: list[str] = []
    csrf_exempt: bool = False

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)

        # Auto CSRF exempt if no session-based auth requires it
        uses_session = any(
            getattr(auth, "requires_csrf", False)
            for auth in getattr(cls, "authentication_classes", [])
        )

        if not uses_session:
            view = csrf_exempt(view)

        return view

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        action = kwargs.get("action")
        if not action:
            return self.response_400("No action provided")

        handler = getattr(self, action, None)
        if not handler or not callable(handler):
            return self.response_404(f"Action '{action}' not found")

        self._current_action = action
        self._current_handler = handler

        # -------------------
        # Authentication
        # -------------------
        try:
            self._perform_authentication(request, handler, action)
        except AutenticationError:
            return self.response_401("Authentication Error")

        # -------------------
        # Permissions
        # -------------------
        try:
            self._check_permissions(request, handler, action)
        except PermissionDenied:
            return self.response_403("Permission Denied")
        # -------------------
        # HTTP Method check
        # -------------------
        allowed_methods = getattr(handler, "route_info", {}).get("methods", ["GET"])
        if request.method not in allowed_methods:
            return self.response_405(
                f"Method {request.method} not allowed. Allowed: {allowed_methods}",
            )

        # -------------------
        # Parse params using Pydantic
        # -------------------
        parsed_params = self._parse_params(handler, request, kwargs)
        if isinstance(parsed_params, JsonResponse):
            return parsed_params

        # -------------------
        # Call handler
        # -------------------
        result = handler(**parsed_params)
        if isinstance(result, JsonResponse):
            return result

        # Validate against response schema if defined
        response_schema = getattr(handler, "route_info", {}).get("response")
        if response_schema:
            try:
                adapter = pydantic.TypeAdapter(response_schema)
                validated_data = adapter.validate_python(result)
                final_data = adapter.dump_python(validated_data, mode="json")
                return self.response(final_data, safe=not isinstance(final_data, list))
            except pydantic.ValidationError as e:
                return self.response_500(f"Response validation failed: {e}")

        return self.response(result)

    def _parse_params(self, func, request, path_params=None):
        path_params = path_params or {}
        kwargs = {}
        sig = inspect.signature(func)

        for name, param in sig.parameters.items():
            annotation = param.annotation

            if name == "request":
                kwargs[name] = request
            elif inspect.isclass(annotation) and issubclass(
                annotation, pydantic.BaseModel
            ):
                try:
                    body = request.body.decode("utf-8")
                    data_dict = json.loads(body) if body else {}
                    kwargs[name] = annotation(**data_dict)
                except pydantic.ValidationError as e:
                    errors = [
                        {
                            "loc": ".".join(str(loc) for loc in err["loc"]),
                            "msg": err["msg"],
                        }
                        for err in e.errors()
                    ]
                    return self.response_400(f"Invalid body for '{name}': {errors}")
                except json.JSONDecodeError:
                    return self.response_400(f"Invalid JSON body for '{name}'")
            elif name in path_params:
                kwargs[name] = path_params[name]
            else:
                kwargs[name] = request.GET.get(name, None)

        return kwargs


class TemplateController(
    ThrottlingMixin,
    AuthPermissionMixin,
    CachingMixin,
    BaseController,
):
    """
    Controller for rendering Django templates with session-based authentication.

    Key features:
    - Only uses session authentication (Django's built-in request.user)
    - Supports skip_authentication_for for public pages
    - Integrates with permission system
    - Auto-detects template directory from controller name

    Example:
        class HomeTemplateController(TemplateController):
            skip_authentication_for = ['index', 'about']  # Public pages

            def index(self, request):
                return self.response({'message': 'Welcome!'})

            def dashboard(self, request):
                # Requires authentication (not in skip list)
                return self.response({'user': request.user})
    """

    response_type = "template"
    template_dir: str | None = None

    # Session auth only - no additional auth classes needed
    authentication_classes: list = []
    permission_classes: list = []
    skip_authentication_for: list[str] = []
    skip_permissions_for: list[str] = []

    # Custom error handlers
    error_handler: Callable | None = None
    authentication_handler: Callable | None = None
    permission_handler: Callable | None = None

    def dispatch(self, request, *args, **kwargs):
        """
        Main dispatch method that handles:
        1. Action resolution
        2. Session authentication check
        3. Permission validation
        4. HTTP method validation
        5. Handler execution
        """
        self.request = request

        action = kwargs.pop("action", None)
        kwargs.pop("methods", None)

        if not action:
            return self.error_response("No action provided", status=400)

        handler = getattr(self, action, None)
        if not handler or not callable(handler):
            return self.error_response(f"Action '{action}' not found", status=404)

        # Store current action/handler for mixins
        self.current_action = action
        self._current_action = action
        self._current_handler = handler

        # -------------------
        # Session Authentication
        # -------------------
        # Only check if action is NOT in skip list
        if action not in self.skip_authentication_for:
            if not request.user.is_authenticated:
                return self.authentication_error("User not authenticated")

        # -------------------
        # Permissions
        # -------------------
        try:
            self._check_permissions(request, handler, action)
        except PermissionDenied as e:
            return self.permission_error(str(e))

        # -------------------
        # HTTP Method Validation
        # -------------------
        allowed_methods = self._get_allowed_methods(action)
        if request.method not in allowed_methods:
            return self.error_response(
                f"Method {request.method} not allowed", status=405
            )

        # -------------------
        # Execute Handler
        # -------------------
        try:
            return handler(request, *args, **kwargs)
        except Exception as e:
            # Re-raise for Django's error handling
            raise

    # -------------------
    # Error Handlers
    # -------------------
    def error_response(self, message: str, status: int = 400):
        """
        Render error template or use custom error handler.

        Default error templates:
        - errors/403.html (Forbidden)
        - errors/500.html (Server Error)
        - errors/error.html (Generic)
        """
        if self.error_handler and callable(self.error_handler):
            return self.error_handler(self.request, message, status)

        template_map = {
            403: "errors/403.html",
            404: "errors/404.html",
            500: "errors/500.html",
        }
        template_path = template_map.get(status, "errors/error.html")

        try:
            return render(
                self.request,
                template_path,
                {"error": message, "status": status},
                status=status,
            )
        except Exception:
            # Fallback to plain text if template not found
            from django.http import HttpResponse

            return HttpResponse(
                f"Error {status}: {message}", status=status, content_type="text/plain"
            )

    def authentication_error(self, message="Authentication required", status=401):
        """
        Handle authentication errors.
        Default: redirect to login or show error page.
        """
        if self.authentication_handler and callable(self.authentication_handler):
            return self.authentication_handler(self.request, message, status)

        # You can customize this to redirect to login page
        # from django.shortcuts import redirect
        # return redirect('login')

        return self.error_response(message, status=status)

    def permission_error(self, message: str):
        """
        Handle permission denied errors.
        """
        if self.permission_handler and callable(self.permission_handler):
            return self.permission_handler(self.request, message)
        return self.error_response(f"Permission denied: {message}", status=403)

    # -------------------
    # Template Rendering
    # -------------------
    def response(
        self,
        context: dict,
        template_name: str | None = None,
        status: int = 200,
    ):
        """
        Render a full page template.

        Convention: If no template_name provided, uses {action}.html
        Example: index() -> users/index.html (where 'users' is from UsersTemplateController)
        """
        return self.render_template(context, template_name, status)

    def render_template(
        self,
        context: dict,
        template_name: str | None = None,
        status: int = 200,
    ):
        """
        Render a template with automatic path resolution.
        """
        if not template_name:
            action = getattr(self, "current_action", None)
            if not action:
                raise Exception("No current action found for template rendering")
            template_name = f"{action}.html"

        template_path = f"{self.get_template_dir()}/{template_name}"

        try:
            return render(self.request, template_path, context, status=status)
        except Exception as e:
            return self.error_response(
                f"Template not found: {template_path}", status=500
            )

    def response_partial(
        self,
        context: dict,
        template_name: str | None = None,
        status: int = 200,
    ):
        """
        Render a partial template (HTMX/AJAX).

        Convention: Uses _action.html format
        Example: hello() -> users/_hello.html

        Great for HTMX responses:
            <div hx-get="/users/profile_partial/" hx-target="#profile">
                Load Profile
            </div>
        """
        if not template_name:
            action = getattr(self, "current_action", None)
            if not action:
                raise Exception("No action found for partial rendering")
            template_name = f"_{action}.html"
        else:
            # Ensure underscore prefix
            base_name = template_name.replace(".html", "").lstrip("_")
            template_name = f"_{base_name}.html"

        template_path = f"{self.get_template_dir()}/{template_name}"

        try:
            return render(self.request, template_path, context, status=status)
        except Exception:
            return self.error_response(
                f"Partial template not found: {template_path}", status=500
            )

    # -------------------
    # Template Directory Resolution
    # -------------------
    def get_template_dir(self) -> str:
        """
        Auto-detect template directory from controller class name.

        Examples:
        - UsersTemplateController -> users/
        - BlogPostTemplateController -> blog_post/
        - HomeTemplateController -> home/
        """
        if self.template_dir:
            return self.template_dir

        class_name = self.__class__.__name__

        # Remove 'TemplateController' suffix
        if class_name.endswith("TemplateController"):
            class_name = class_name[:-18]

        # Convert CamelCase to snake_case
        folder_name = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()
        return folder_name

    def _get_allowed_methods(self, action: str):
        """Get allowed HTTP methods for an action."""
        handler = getattr(self, action)
        return getattr(handler, "methods", ["GET", "POST"])
