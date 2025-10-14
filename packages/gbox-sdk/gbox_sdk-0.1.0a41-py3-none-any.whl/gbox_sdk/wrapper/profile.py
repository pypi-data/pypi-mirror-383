import os
import base64
import logging
from typing import Any, Dict, Callable, Optional
from pathlib import Path

try:
    import tomllib  # type: ignore[import-not-found,import-untyped]
except ImportError:
    # Python < 3.11 fallback
    try:
        import tomli as tomllib  # type: ignore[import-untyped]
    except ImportError:
        tomllib = None

# Define Logger and LogLevel locally since they're not available in _logs.py


class LogLevel:
    OFF = "off"
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    DEBUG = "debug"


class Logger:
    """Simple logger interface for profile operations."""

    def __init__(
        self,
        error: Optional[Callable[..., None]] = None,
        warn: Optional[Callable[..., None]] = None,
        info: Optional[Callable[..., None]] = None,
        debug: Optional[Callable[..., None]] = None,
    ):
        self.error = error or logging.error
        self.warn = warn or logging.warning
        self.info = info or logging.info
        self.debug = debug or logging.debug


class ProfileData:
    """Profile data structure for storing organization and API key information."""

    def __init__(
        self,
        org_name: str,
        org_slug: str,
        key: str,
        base_url: Optional[str] = None,
    ):
        self.org_name = org_name
        self.org_slug = org_slug
        self.key = key
        self.base_url = base_url


class ProfileConfig:
    """Profile configuration structure for managing multiple profiles."""

    def __init__(
        self,
        profiles: Dict[str, ProfileData],
        current: Optional[str] = None,
        defaults: Optional[Dict[str, Any]] = None,
    ):
        self.profiles = profiles
        self.current = current
        self.defaults = defaults or {}


class ProfileOptions:
    """Options for profile-based client initialization."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        logger: Optional[Logger] = None,
        log_level: Optional[LogLevel] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logger
        self.log_level = log_level


class Profile:
    """
    Simple profile reader for gbox profile configuration.
    Read-only implementation using tomllib for parsing.
    """

    def __init__(self) -> None:
        # Profile path priority: GBOX_HOME env > default (~/.gbox/profiles.toml)
        gbox_home = os.environ.get("GBOX_HOME", str(Path.home() / ".gbox"))
        self.profile_path = Path(gbox_home) / "profiles.toml"
        self._config: Optional[ProfileConfig] = None

    def load(self) -> Optional[ProfileConfig]:
        """Load profiles from the profile file."""
        try:
            if not self.profile_path.exists():
                return None

            if not self.profile_path.stat().st_size:
                return None

            if tomllib is None:
                # TOML parsing not available for Python < 3.11
                return None

            with open(self.profile_path, "rb") as f:
                data = tomllib.load(f)  # type: ignore[union-attr]

            self._config = self._validate_and_transform_config(data)
            return self._config

        except Exception:
            # Failed to load profile file
            return None

    def get_api_key(self) -> Optional[str]:
        """Get API key from the current profile."""
        if not self._config:
            self._config = self.load()

        if not self._config or not self._config.profiles or not self._config.current:
            return None

        current_profile = self._config.profiles.get(self._config.current)
        if not current_profile or not current_profile.key:
            return None

        try:
            # Decode base64 encoded API key
            return base64.b64decode(current_profile.key).decode("utf-8")
        except Exception:
            # Failed to decode API key
            return None

    def get_base_url(self) -> Optional[str]:
        """Get base URL from the current profile or defaults."""
        if not self._config:
            self._config = self.load()

        if not self._config:
            return None

        # First try to get from current profile
        if self._config.current and self._config.current in self._config.profiles:
            current_profile = self._config.profiles[self._config.current]
            if current_profile and current_profile.base_url:
                return current_profile.base_url

        # Fall back to defaults
        return self._config.defaults.get("base_url")

    def build_client_options(self, user_options: Optional[ProfileOptions] = None) -> ProfileOptions:
        """
        Build client options with priority:
        1. User-provided options (highest priority)
        2. Environment variables (GBOX_CLIENT_BASE_URL > GBOX_BASE_URL)
        3. Profile file values (lowest priority)
        """
        # Load profile and update internal config
        profile = self.load()
        if profile:
            self._config = profile

        options = user_options or ProfileOptions()

        # API Key priority: user_options > GBOX_API_KEY env > profile
        api_key = options.api_key
        if not api_key:
            env_api_key = os.environ.get("GBOX_API_KEY")
            if env_api_key:
                api_key = env_api_key
            elif profile:
                profile_api_key = self.get_api_key()
                if profile_api_key:
                    api_key = profile_api_key

        # Base URL priority: user_options > GBOX_CLIENT_BASE_URL env > GBOX_BASE_URL env > profile > default
        base_url = options.base_url
        if not base_url:
            # Try GBOX_CLIENT_BASE_URL first (higher priority)
            client_base_url = os.environ.get("GBOX_CLIENT_BASE_URL")
            if client_base_url:
                base_url = client_base_url
            else:
                # Try GBOX_BASE_URL as fallback
                env_base_url = os.environ.get("GBOX_BASE_URL")
                if env_base_url:
                    base_url = env_base_url
                elif profile:
                    profile_base_url = self.get_base_url()
                    if profile_base_url:
                        base_url = profile_base_url

        return ProfileOptions(
            api_key=api_key,
            base_url=base_url,
            logger=options.logger,
            log_level=options.log_level,
        )

    def _validate_and_transform_config(self, parsed: Any) -> Optional[ProfileConfig]:
        """Validate and transform parsed TOML data to ProfileConfig."""
        try:
            # Ensure the parsed data has the expected structure
            if not parsed or not isinstance(parsed, dict):
                return None

            config = ProfileConfig(
                profiles={},
                defaults={},
            )

            # Set current if it exists
            if "current" in parsed:
                config.current = str(parsed["current"])  # type: ignore[arg-type]

            # Extract profiles
            if "profiles" in parsed and isinstance(parsed["profiles"], dict):
                profiles_dict: Dict[str, Any] = parsed["profiles"]  # type: ignore[assignment]
                for key, profile in profiles_dict.items():
                    if profile and isinstance(profile, dict) and "key" in profile:
                        profile_data: Dict[str, Any] = profile  # type: ignore[assignment]
                        # Support both 'org' and 'org_name' fields for backward compatibility
                        org_name = str(profile_data.get("org_name") or profile_data.get("org", ""))
                        config.profiles[str(key)] = ProfileData(
                            org_name=org_name,
                            org_slug=str(profile_data.get("org_slug", "")),
                            key=str(profile_data.get("key", "")),
                            base_url=profile_data.get("base_url"),
                        )

            # Extract defaults
            if "defaults" in parsed and isinstance(parsed["defaults"], dict) and "base_url" in parsed["defaults"]:
                defaults: Dict[str, Any] = parsed["defaults"]  # type: ignore[assignment]
                config.defaults = {
                    "base_url": str(defaults["base_url"]),
                }

            return config

        except Exception:
            # Failed to validate profile config
            return None
