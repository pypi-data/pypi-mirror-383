import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.management import call_command


class Command(BaseCommand):
    help = "Generates a complete 'users' app with CustomUser, Token, auth, permissions, and API controller"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fields",
            nargs="*",
            type=str,
            help="Extra fields to add in the form field:type (e.g., bio:text phone:char)",
        )
        parser.add_argument(
            "--token-lifetime-days",
            type=int,
            default=30,
            help="Number of days before token expires (default: 30)",
        )

    def handle(self, *args, **options):
        project_root = settings.BASE_DIR
        users_app_path = os.path.join(project_root, "users")

        if os.path.exists(users_app_path):
            raise CommandError("App 'users' already exists!")

        # Step 1: Create the app
        self.stdout.write(self.style.NOTICE("📦 Creating users app..."))
        call_command("startapp", "users")

        # -------------------
        # Step 2: models.py
        # -------------------
        base_model = [
            "from django.contrib.auth.models import AbstractUser",
            "from django.db import models",
            "from django.utils import timezone",
            "import secrets",
            "from datetime import timedelta",
            "",
            "class CustomUser(AbstractUser):",
        ]

        fields = options["fields"]
        if not fields:
            add_more = True
            fields = []
            while add_more:
                field_name = input("Field name (leave empty to stop): ").strip()
                if not field_name:
                    break
                field_type = (
                    input(f"Field type for {field_name} [char/text/int/bool]: ")
                    .strip()
                    .lower()
                    or "char"
                )
                fields.append(f"{field_name}:{field_type}")

        field_map = {
            "char": "models.CharField(max_length=255, blank=True, null=True)",
            "text": "models.TextField(blank=True, null=True)",
            "int": "models.IntegerField(blank=True, null=True)",
            "bool": "models.BooleanField(default=False)",
        }

        for field in fields:
            name, ftype = field.split(":")
            code = field_map.get(ftype, field_map["char"])
            base_model.append(f"    {name} = {code}")

        if not fields:
            base_model.append("    # Add custom fields here if needed")
        base_model.append("")
        base_model.append("    def __str__(self):")
        base_model.append("        return self.username")

        # Token model
        token_model = [
            "",
            f"TOKEN_LIFETIME = timedelta(days={options['token_lifetime_days']})",
            "",
            "class Token(models.Model):",
            "    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='token')",
            "    key = models.CharField(max_length=40, unique=True)",
            "    created_at = models.DateTimeField(auto_now_add=True)",
            "    expires_at = models.DateTimeField(blank=True, null=True)",
            "",
            "    def save(self, *args, **kwargs):",
            "        if not self.key:",
            "            self.key = secrets.token_hex(20)",
            "        if not self.expires_at:",
            "            self.expires_at = timezone.now() + TOKEN_LIFETIME",
            "        super().save(*args, **kwargs)",
            "",
            "    def refresh(self):",
            "        self.key = secrets.token_hex(20)",
            "        self.expires_at = timezone.now() + TOKEN_LIFETIME",
            "        self.save()",
            "",
            "    def is_expired(self):",
            "        return self.expires_at and timezone.now() > self.expires_at",
            "",
            "    def __str__(self):",
            '        return f"Token({self.user.username})"',
            "",
            "# Automatically create token when user is created",
            "from django.db.models.signals import post_save",
            "from django.dispatch import receiver",
            "",
            "@receiver(post_save, sender=CustomUser)",
            "def create_user_token(sender, instance, created, **kwargs):",
            "    if created and not hasattr(instance, 'token'):",
            "        Token.objects.create(user=instance)",
        ]

        with open(os.path.join(users_app_path, "models.py"), "w") as f:
            f.write("\n".join(base_model + token_model))

        # -------------------
        # Step 3: admin.py
        # -------------------
        admin_code = """from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Token

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("user", "key", "created_at", "expires_at")
"""
        with open(os.path.join(users_app_path, "admin.py"), "w") as f:
            f.write(admin_code)

        # -------------------
        # Step 4: auth.py
        # -------------------
        auth_code = """from django.contrib.auth import get_user_model
from .models import Token

User = get_user_model()

class SimpleTokenAuthentication:
    \"""
    Usage: Add to ApiController.authentication_classes
    Authorization header: Token <key>
    \"""
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Token "):
            return None

        key = auth_header.split(" ", 1)[1].strip()
        try:
            token = Token.objects.select_related("user").get(key=key)
            if token.is_expired():
                return None
            return token.user, token
        except Token.DoesNotExist:
            return None

def skip_authentication(func):
    func.skip_auth = True
    return func
"""
        with open(os.path.join(users_app_path, "auth.py"), "w") as f:
            f.write(auth_code)

        # -------------------
        # Step 5: permissions.py
        # -------------------
        permissions_code = """class IsAuthenticated:
    \"""
    Usage: Add to ApiController.permission_classes
    \"""
    def has_permission(self, request, view):
        return request.user.is_authenticated

def skip_permissions(func):
    func.skip_perm = True
    return func
"""
        with open(os.path.join(users_app_path, "permissions.py"), "w") as f:
            f.write(permissions_code)

        # -------------------
        # Step 6: controllers.py
        # -------------------
        controllers_code = """from users.auth import SimpleTokenAuthentication, skip_authentication
from users.permissions import IsAuthenticated, skip_permissions
from users.models import CustomUser, Token
from your_project.api_controller import ApiController  # adjust import

class UserController(ApiController):
    authentication_classes = [SimpleTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @skip_authentication
    @skip_permissions
    def me(self, request):
        user = request.user
        return self.response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        })

    def refresh_token(self, request):
        token = getattr(request.user, "token", None)
        if not token:
            return self.response({"error": "Token not found"}, status=404)
        token.refresh()
        return self.response({
            "token": token.key,
            "expires_at": token.expires_at
        })
"""
        with open(os.path.join(users_app_path, "controllers.py"), "w") as f:
            f.write(controllers_code)

        # -------------------
        # Step 7: Update settings.py
        # -------------------
        settings_file = os.path.join(
            project_root, settings.SETTINGS_MODULE.replace(".", "/") + ".py"
        )
        with open(settings_file, "r") as f:
            content = f.read()

        if "'users'," not in content and '"users",' not in content:
            content = content.replace(
                "INSTALLED_APPS = [", "INSTALLED_APPS = [\n    'users',"
            )

        if "AUTH_USER_MODEL" not in content:
            content += "\n\nAUTH_USER_MODEL = 'users.CustomUser'\n"

        with open(settings_file, "w") as f:
            f.write(content)

        self.stdout.write(self.style.SUCCESS("✅ App 'users' created successfully!"))
        self.stdout.write(self.style.SUCCESS("➡ Added 'users' to INSTALLED_APPS"))
        self.stdout.write(
            self.style.SUCCESS("➡ Set AUTH_USER_MODEL = 'users.CustomUser'")
        )
        self.stdout.write(
            self.style.SUCCESS("➡ Token model with expiration & rotation generated")
        )
        self.stdout.write(self.style.SUCCESS("➡ Auth & permissions scaffolds created"))
        self.stdout.write(
            self.style.SUCCESS(
                "➡ UserController with /me and /refresh_token endpoints generated"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                "⚠️ Run `python manage.py makemigrations users && python manage.py migrate`"
            )
        )
