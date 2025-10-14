from __future__ import annotations

import logging
import os
import sys
from collections.abc import MutableMapping
from typing import Any, Iterator

from ruamel.yaml import YAML

logger = logging.getLogger(__name__)


DEFAULT_CONFIG_FILENAME: str = "config.yml"
DEFAULT_SETTINGS: dict[str, Any] = {
    "use_blissdata_api": False,
    "dynamic_hdf5_retry_timeout": 0.1,
}


class Config(MutableMapping[str, Any]):
    """A singleton class to provide access to the configuration settings."""

    _instance: Config | None = None
    _settings: dict[str, Any] | None = None

    def __new__(cls) -> Config:
        """
        Create or return the singleton instance of the Config class.
        Ensures configuration is loaded when first instantiated.
        If no configuration file exists, creates one with default values.

        Returns:
            Config: The singleton instance of the Config class.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.read()

            # Check if any config file was loaded.
            config_path = cls._instance._get_global_config_dir()
            config_file = os.path.join(config_path, DEFAULT_CONFIG_FILENAME)

            if not os.path.exists(config_file):
                # Create default configuration file if none exists.
                cls._instance.write(default=True)

        return cls._instance

    def __getitem__(self, key: str) -> Any:
        """Get configuration value by key."""
        if self._settings is None:
            raise KeyError(key)
        return self._settings[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        if self._settings is not None:
            self._settings[key] = value

    def __delitem__(self, key: str) -> None:
        """Delete configuration value by key."""
        if self._settings is not None:
            del self._settings[key]

    def __iter__(self) -> Iterator[str]:
        """Iterate through configuration keys."""
        if self._settings is not None:
            return iter(self._settings)
        return iter([])

    def __len__(self) -> int:
        """Get number of configuration items."""
        return len(self._settings) if self._settings is not None else 0

    def _get_global_config_dir(self) -> str:
        """Return the platform-specific directory path for storing the configuration.

        Creates the directory if it does not exist and falls back to the current
        working directory if creation fails.

        Returns:
            str: Path to the configuration directory.
        """
        package = "daxs"
        if sys.platform.startswith("win"):
            base_dir = os.environ.get("APPDATA", "")
            if not base_dir:
                base_dir = os.path.join(
                    os.environ.get("USERPROFILE", ""), "AppData", "Roaming"
                )
            config_dir = os.path.join(base_dir, package)
        elif sys.platform.startswith("darwin"):
            base_dir = os.path.expanduser("~")
            config_dir = os.path.join(
                base_dir, "Library", "Application Support", package
            )
        else:
            xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "")
            if not xdg_config_home:
                xdg_config_home = os.path.join(os.path.expanduser("~"), ".config")
            config_dir = os.path.join(xdg_config_home, package)

        # Create the config directory if it does not exist.
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except OSError as e:
                logger.info(f"Could not create config directory: {e}")
                # Fall back to current directory if the directory could not be created.
                return os.path.join(os.getcwd())

        return config_dir

    def read(self) -> None:
        """Read the configuration settings from YAML files.

        Checks multiple locations in order of priority:

        1. Path specified in ``DAXS_CONFIG`` environment variable (highest)
        2. ``config.yml`` in current working directory
        3. ``config.yml`` in platform-specific global configuration directory (lowest)

        Settings from higher priority files override those from lower priority files.
        Falls back to the internal default configuration if no files are found.
        """
        # Start with default configuration.
        self._settings = DEFAULT_SETTINGS.copy()

        locations: list[str | None] = [
            os.path.join(self._get_global_config_dir(), DEFAULT_CONFIG_FILENAME),
            os.path.join(os.getcwd(), DEFAULT_CONFIG_FILENAME),
            os.environ.get("DAXS_CONFIG"),
        ]

        # Filter out invalid locations.
        locations = [location for location in locations if location is not None]

        config_found = False
        for location in locations:
            if location is None:
                continue
            try:
                yaml = YAML(typ="safe")
                with open(location, "r") as fh:
                    config = yaml.load(fh)
                    if config is not None:
                        self._settings.update(config)
                    logger.info(f"Loaded configuration from {location}")
                    config_found = True
                    return
            except (FileNotFoundError, PermissionError):
                continue

        if not config_found:
            logger.info("No configuration found, using internal defaults.")

    def write(self, default: bool = False) -> bool:
        """Write configuration to the global configuration file.

        Args:
            default:
                If True, write the default configuration instead of the current one,
                but only if the file does not exist yet.

        Returns:
            bool: True if the configuration was written successfully, False otherwise.
        """
        config_path = self._get_global_config_dir()
        config_file = os.path.join(config_path, DEFAULT_CONFIG_FILENAME)

        if default and os.path.exists(config_file):
            logger.info(f"Configuration file already exists at {config_file}.")
            return False

        # Determine which configuration to write.
        config_to_write = DEFAULT_SETTINGS if default else self._settings

        try:
            yaml = YAML()
            with open(config_file, "w") as file:
                yaml.dump(config_to_write, file)
            logger.info(f"Saved configuration to {config_file}")
            return True
        except (PermissionError, OSError) as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    def __str__(self) -> str:
        """Return a string representation of the current configuration.

        Returns:
        str: A formatted string showing all configuration keys and values.
        """
        if self._settings is None:
            return "No configuration was read."

        items = [f"{key}: {value}" for key, value in self._settings.items()]
        return "\n".join(items)
