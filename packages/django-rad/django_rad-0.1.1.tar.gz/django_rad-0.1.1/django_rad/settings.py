# in rad/settings.py

from django.conf import settings
from typing import Any, Dict

# NEW: Define defaults with a nested structure
DEFAULTS: Dict[str, Any] = {
    "THROTTLING": {
        "DEFAULT_CLASSES": [],
        "RATES": {},
    }
}


class APISettings:
    # This class remains exactly the same!
    def __init__(
        self,
        user_settings: Dict[str, Any] | None = None,
        defaults: Dict[str, Any] | None = None,
    ):
        if user_settings is None:
            user_settings = {}
        if defaults is None:
            defaults = {}
        self._user_settings = user_settings
        self.defaults = defaults

    def __getattr__(self, attr: str) -> Any:
        if attr not in self.defaults:
            raise AttributeError(f"Invalid API setting: '{attr}'")
        try:
            val = self._user_settings[attr]
            # If the user's setting is a dict, merge it with the default
            if isinstance(val, dict):
                return {**self.defaults[attr], **val}
            return val
        except KeyError:
            return self.defaults[attr]


rad_api_settings = APISettings(getattr(settings, "RAD_API_SETTINGS", None), DEFAULTS)
