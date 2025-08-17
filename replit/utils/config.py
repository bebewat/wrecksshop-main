"""
Configuration management utility for the Ark Discord Bot
"""

import json
import os
from typing import Any, Dict, Optional

class Config:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config_data = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                # Create default configuration
                self.config_data = self.get_default_config()
                self.save()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.config_data = self.get_default_config()
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self.config_data
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update configuration with dictionary"""
        for key, value in data.items():
            self.set(key, value)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "discord_bot_token": "",
            "discord_shop_channel_id": "",
            "discord_log_channel_id": "",
            "tip4serv_secret": "",
            "tip4serv_token": "",
            "reward_interval": 60,
            "reward_amount": 10,
            "player_tiers": {
                "default": {
                    "multiplier": 1.0,
                    "requirements": "None"
                },
                "donor": {
                    "multiplier": 1.5,
                    "requirements": "Donation"
                },
                "vip": {
                    "multiplier": 2.0,
                    "requirements": "VIP Status"
                },
                "admin": {
                    "multiplier": 3.0,
                    "requirements": "Admin Role"
                }
            },
            "rcon_servers": [],
            "databases": [
                {
                    "name": "Default SQLite",
                    "type": "sqlite",
                    "path": "data/bot_database.db",
                    "host": "localhost",
                    "port": "",
                    "database": "bot_database.db"
                }
            ],
            "admin_roles": [
                {
                    "name": "Owner",
                    "discord_role_id": "",
                    "permissions": ["*"],
                    "point_multiplier": 5.0,
                    "enabled": True
                },
                {
                    "name": "Admin",
                    "discord_role_id": "",
                    "permissions": ["shop.manage", "users.manage", "points.give"],
                    "point_multiplier": 3.0,
                    "enabled": True
                },
                {
                    "name": "Moderator",
                    "discord_role_id": "",
                    "permissions": ["shop.view", "users.view"],
                    "point_multiplier": 2.0,
                    "enabled": True
                }
            ],
            "logging": {
                "level": "INFO",
                "file": "logs/bot.log",
                "max_file_size": 10485760,
                "backup_count": 5
            },
            "shop": {
                "currency_name": "points",
                "default_category": "General",
                "max_items_per_page": 10
            },
            "security": {
                "command_cooldown": 3,
                "max_transfer_amount": 10000,
                "require_steam_linking": True
            }
        }
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        try:
            # Check required fields
            required_fields = [
                "discord_bot_token",
                "reward_interval",
                "reward_amount"
            ]
            
            for field in required_fields:
                if not self.get(field):
                    print(f"Missing required configuration: {field}")
                    return False
            
            # Validate types
            if not isinstance(self.get("reward_interval"), int):
                print("reward_interval must be an integer")
                return False
            
            if not isinstance(self.get("reward_amount"), int):
                print("reward_amount must be an integer")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validating configuration: {e}")
            return False
    
    def backup_config(self, backup_file: Optional[str] = None) -> str:
        """Create backup of current configuration"""
        if backup_file is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"config_backup_{timestamp}.json"
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            return backup_file
        except Exception as e:
            print(f"Error creating config backup: {e}")
            raise
    
    def restore_config(self, backup_file: str) -> None:
        """Restore configuration from backup"""
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            self.save()
        except Exception as e:
            print(f"Error restoring config from backup: {e}")
            raise
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config_data = self.get_default_config()
        self.save()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.get(section, {})
    
    def has_section(self, section: str) -> bool:
        """Check if configuration section exists"""
        return section in self.config_data
    
    def remove_section(self, section: str) -> None:
        """Remove configuration section"""
        if section in self.config_data:
            del self.config_data[section]
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration data"""
        return self.config_data.copy()
