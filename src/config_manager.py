"""
Configuration manager for the Mod Side Checker.
"""
import os
import json
from pathlib import Path

# Try relative import first, fall back to absolute import if needed
try:
    from .utils import ColorPrinter
except ImportError:
    import sys
    import os.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.utils import ColorPrinter
    
from colorama import Fore

class ConfigManager:
    """Class for managing configuration settings."""
    
    DEFAULT_CONFIG = {
        "folders": {
            "input": "input",
            "output": "output",
            "temp": "temp"
        },
        "threading": {
            "max_threads": 10,
            "recommended_max": 6,
            "warning": "Using more than 6 threads may cause UI stability issues depending on your system"
        },
        "api": {
            "request_delay": 0.5,
            "user_agent": "ModEnvironmentChecker/1.0"
        },
        "ui": {
            "progress_bar_width": 80,
            "use_ascii_bars": True
        },
        "files": {
            "mod_index": "modrinth.index.json",
            "server_pack": "server_pack.zip",
            "client_pack": "client_pack.zip"
        }
    }
    
    _config = None
    _config_path = None
    
    @classmethod
    def get_config_path(cls):
        """Get the path to the config file."""
        if cls._config_path is None:
            # Config file is in the root directory of the project
            cls._config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config.json"
            )
        return cls._config_path
    
    @classmethod
    def load_config(cls):
        """
        Load configuration from file or create default if not exists.
        
        Returns:
            dict: The configuration settings
        """
        if cls._config is not None:
            return cls._config
            
        config_path = cls.get_config_path()
        
        # If config file doesn't exist, create it with defaults
        if not os.path.exists(config_path):
            ColorPrinter.print("No configuration file found. Creating default config.json...", Fore.YELLOW)
            cls.save_config(cls.DEFAULT_CONFIG)
            return cls.DEFAULT_CONFIG
        
        # Load existing config
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_config = cls.DEFAULT_CONFIG.copy()
                cls._deep_update(merged_config, config)
                cls._config = merged_config
                return cls._config
        except Exception as e:
            ColorPrinter.print(f"Error loading config: {e}", Fore.RED)
            ColorPrinter.print("Using default configuration.", Fore.YELLOW)
            return cls.DEFAULT_CONFIG
    
    @classmethod
    def save_config(cls, config):
        """
        Save configuration to file.
        
        Args:
            config (dict): Configuration to save
        """
        config_path = cls.get_config_path()
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            cls._config = config
            ColorPrinter.print(f"Configuration saved to {config_path}", Fore.GREEN)
        except Exception as e:
            ColorPrinter.print(f"Error saving config: {e}", Fore.RED)
    
    @classmethod
    def get(cls, *keys, default=None):
        """
        Get a value from the configuration using dot notation.
        
        Args:
            *keys: Key path to the desired config value
            default: Default value if key not found
            
        Returns:
            The value or default if not found
        
        Example:
            get('folders', 'input') -> returns input folder path
        """
        if cls._config is None:
            cls.load_config()
            
        config = cls._config
        try:
            for key in keys:
                config = config[key]
            return config
        except (KeyError, TypeError):
            return default
    
    @classmethod
    def _deep_update(cls, target, source):
        """
        Recursively update a nested dictionary without overwriting entire sections.
        
        Args:
            target (dict): Dictionary to update
            source (dict): Dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                cls._deep_update(target[key], value)
            else:
                target[key] = value
