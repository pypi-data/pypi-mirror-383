import os
from django.core.management.base import BaseCommand

CONTROLLER_TEMPLATE = """from django_rad.controllers import {base_controller}

class {controller_name}({base_controller}):

    def index(self, request):
        return self.response({{"message": "index"}})

    def show(self, request, id):
        return self.response({{"id": id}})

    def create(self, request):
        return self.response({{"message": "create"}})

    def update(self, request, id):
        return self.response({{"id": id}})

    def destroy(self, request, id):
        return self.response({{"id": id}})
"""


def normalize_controller_name(raw_name: str, ctrl_type: str) -> str:
    """Normalize a name to PascalCase and add Template/APIController suffix."""
    # Remove any existing "_controller"
    if raw_name.lower().endswith("_controller"):
        raw_name = raw_name[:-11]

    # Convert snake_case or kebab-case to PascalCase
    parts = raw_name.replace("-", "_").split("_")
    base_name = "".join(part.capitalize() for part in parts)

    # Add suffix based on controller type
    if ctrl_type == "template":
        suffix = "TemplateController"
    else:
        suffix = "APIController"

    return base_name + suffix


class Command(BaseCommand):
    help = (
        "Generate an API or Template controller and register it in the project urls.py"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            choices=["api", "template"],
            required=True,
            help="Type of controller: api or template",
        )
        parser.add_argument("--app", type=str, required=True, help="Target Django app")
        parser.add_argument(
            "--name",
            type=str,
            required=True,
            help="Controller name (e.g., 'another' or 'another_name')",
        )

    def handle(self, *args, **options):
        ctrl_type = options["type"]
        app_name = options["app"]
        raw_name = options["name"]

        # Normalize controller name
        controller_name = normalize_controller_name(raw_name, ctrl_type)

        # Detect project folder from DJANGO_SETTINGS_MODULE
        settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
        if not settings_module:
            self.stdout.write(self.style.ERROR("DJANGO_SETTINGS_MODULE not set"))
            return

        project_folder = settings_module.split(".")[0]

        # Paths
        app_dir = os.path.join(os.getcwd(), app_name)
        controllers_file = os.path.join(app_dir, "controllers.py")

        # Determine template folder (Rails-style, snake_case from base name)
        base_folder = raw_name.lower().replace("-", "_").replace("_", "")
        if ctrl_type == "template":
            templates_dir = os.path.join(app_dir, "templates", base_folder)
            os.makedirs(templates_dir, exist_ok=True)
            for action in ["index", "show", "create", "update", "destroy"]:
                path_html = os.path.join(templates_dir, f"{action}.html")
                if not os.path.exists(path_html):
                    with open(path_html, "w") as f:
                        f.write(f"<h1>{action.capitalize()}</h1>\n")

        os.makedirs(app_dir, exist_ok=True)

        # Determine base controller class
        base_controller = (
            "TemplateController" if ctrl_type == "template" else "ApiController"
        )

        # Generate or append controller
        controller_code = CONTROLLER_TEMPLATE.format(
            base_controller=base_controller, controller_name=controller_name
        )

        if os.path.exists(controllers_file):
            with open(controllers_file, "a") as f:
                f.write("\n\n" + controller_code)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Appended controller '{controller_name}' to {controllers_file}"
                )
            )
        else:
            with open(controllers_file, "w") as f:
                f.write(controller_code)
            self.stdout.write(self.style.SUCCESS(f"Created {controllers_file}"))

        # Register in project/urls.py
        project_urls = os.path.join(os.getcwd(), project_folder, "urls.py")
        if not os.path.exists(project_urls):
            self.stdout.write(self.style.ERROR(f"{project_urls} not found!"))
            return

        # URL prefix for API vs Template
        url_prefix = f"api/{base_folder}" if ctrl_type == "api" else base_folder

        register_line = (
            f"    *register_controller_group('{url_prefix}', {controller_name}),\n"
        )
        with open(project_urls, "r") as f:
            content = f.read()

        # Add import for register_controller if missing
        if "from django_rad.routers import register_controller_group" not in content:
            content = content.replace(
                "from django.urls import path",
                "from django.urls import path\nfrom django_rad.routers import register_controller_group",
            )

        # Add import for the controller if missing
        import_line = f"from {app_name}.controllers import {controller_name}\n"
        if import_line not in content:
            content = content.replace(
                "from django_rad.routers import register_controller_group",
                f"from django_rad.routers import register_controller_group\n{import_line.strip()}",
            )

        # Insert register_controller into urlpatterns
        if "urlpatterns = [" in content and register_line.strip() not in content:
            content = content.replace(
                "urlpatterns = [", f"urlpatterns = [\n{register_line}"
            )

        with open(project_urls, "w") as f:
            f.write(content)

        self.stdout.write(
            self.style.SUCCESS(f"Registered {controller_name} in {project_urls}")
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"{ctrl_type.capitalize()} controller '{controller_name}' generated successfully!"
            )
        )
