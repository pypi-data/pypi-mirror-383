"""Config and settings management utilities for Bear Utils."""

from ._base_settings import BaseSetting, BaseSettingHandler
from .config_manager import ConfigManager
from .dir_manager import (
    DirectoryManager,
    clear_temp_directory,
    get_cache_path,
    get_config_path,
    get_local_config_path,
    get_settings_path,
    get_temp_path,
)
from .quick_settings import SimpleSettingsManager
from .settings_manager import BearSettings, SettingsManager, StorageChoices

__all__ = [
    "BaseSetting",
    "BaseSettingHandler",
    "BearSettings",
    "ConfigManager",
    "DirectoryManager",
    "SettingsManager",
    "SimpleSettingsManager",
    "StorageChoices",
    "clear_temp_directory",
    "get_cache_path",
    "get_config_path",
    "get_local_config_path",
    "get_settings_path",
    "get_temp_path",
]
