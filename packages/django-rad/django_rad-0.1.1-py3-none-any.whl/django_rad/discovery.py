import inspect
from importlib import import_module
from django.apps import apps
from .controllers import (
    BaseController,
)

from collections import defaultdict


def generate_openapi_schema(controllers, title="My API", version="1.0.0"):
    """
    Introspects a list of controller classes and generates an OpenAPI 3.0 schema.
    """
    schema = {
        "openapi": "3.0.0",
        "info": {"title": title, "version": version},
        "paths": defaultdict(dict),
    }

    # Helper to map Python types to OpenAPI types
    def map_type(py_type):
        if py_type in [int, "int"]:
            return "integer"
        if py_type in [str, "str"]:
            return "string"
        return "string"  # Default

    for controller_cls in controllers:
        # Infer the base path from the controller name (e.g., ArticlesController -> /articles/)
        base_name = controller_cls.__name__.replace("Controller", "").lower()
        base_path = f"/{base_name}/"

        # 1. Inspect default routes (index, show, etc.)
        for action, config in controller_cls.routes.items():
            path_pattern = config["pattern"].replace("<int:id>", "{id}")
            full_path = f"{base_path}{path_pattern}"

            method_obj = getattr(controller_cls, action)
            docstring = (
                inspect.getdoc(method_obj) or f"{action.capitalize()} {base_name}"
            )

            for http_method in config["methods"]:
                schema["paths"][full_path][http_method.lower()] = {
                    "summary": docstring.split("\n")[0],
                    "operationId": f"{base_name}_{action}",
                    "tags": [base_name.capitalize()],
                    "responses": {"200": {"description": "Successful response"}},
                }

        # 2. Inspect custom @route decorated methods
        for name, method in inspect.getmembers(controller_cls, inspect.isfunction):
            if not hasattr(method, "route_info"):
                continue

            info = method.route_info
            path_params = [
                p for p in info["params"] if "{" + p["name"] + "}" in info["pattern"]
            ]

            # Construct the full path
            if info["type"] == "member":
                full_path = f"{base_path}{{id}}/{info['pattern']}"
            else:  # collection
                full_path = f"{base_path}{info['pattern']}"

            parameters = []
            # Add the default {id} parameter for member routes
            if info["type"] == "member":
                parameters.append(
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                    }
                )

            # Add parameters from the function signature
            for param in path_params:
                parameters.append(
                    {
                        "name": param["name"],
                        "in": "path",
                        "required": True,
                        "schema": {"type": map_type(param["type"])},
                    }
                )

            for http_method in info["methods"]:
                schema["paths"][full_path][http_method.lower()] = {
                    "summary": info["doc"].split("\n")[0]
                    or f"{name.capitalize()} {base_name}",
                    "operationId": f"{base_name}_{name}",
                    "tags": [base_name.capitalize()],
                    "parameters": parameters,
                    "responses": {"200": {"description": "Successful response"}},
                }

    return schema


def discover_controllers():
    """
    Finds and returns all BaseController subclasses within the project's installed apps.

    This function looks for a 'controllers.py' file in each app.
    """
    discovered_controllers = []

    # Get all installed app configurations
    for app_config in apps.get_app_configs():
        # We assume controllers are defined in a file named 'controllers.py'
        controllers_module_name = f"{app_config.name}.controllers"
        try:
            # Dynamically import the controllers module for the current app
            module = import_module(controllers_module_name)

            # Inspect the module for classes that are subclasses of BaseController
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseController) and obj is not BaseController:
                    discovered_controllers.append(obj)

        except ImportError:
            # This app doesn't have a controllers.py file, which is fine.
            continue

    return discovered_controllers
