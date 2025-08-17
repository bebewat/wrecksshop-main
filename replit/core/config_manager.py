"""
Configuration manager for handling application settings
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """Manages application configuration settings"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize config manager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config_data = {}
        self.default_config = self._get_default_config()
        
        # Ensure config directory exists
        config_dir = os.path.dirname(os.path.abspath(config_file))
        os.makedirs(config_dir, exist_ok=True)
        
        # Load existing config or create default
        self.load()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            # Discord Configuration
            'discord_bot_token': '',
            'discord_shop_channel_id': '',
            'discord_log_channel_id': '',
            
            # Tip4Serv Configuration
            'tip4serv_secret': '',
            'tip4serv_token': '',
            'tip4serv_webhook_url': 'https://api.tip4serv.com/webhook',
            
            # Reward System Configuration
            'reward_interval': 30,  # minutes
            'reward_amount': 10,  # base points
            
            # Bot Configuration
            'command_prefix': '!',
            'auto_role_assignment': True,
            'enable_point_transfers': True,
            'enable_shop': True,
            
            # Database Configuration
            'database_type': 'sqlite',
            'database_file': 'arkbot.db',
            'database_host': 'localhost',
            'database_port': 5432,
            'database_name': 'arkbot',
            'database_user': '',
            'database_password': '',
            
            # Logging Configuration
            'log_level': 'INFO',
            'log_file': 'logs/arkbot.log',
            'max_log_size': 10485760,  # 10MB
            'log_backup_count': 5,
            
            # Security Configuration
            'max_points_per_transfer': 10000,
            'max_daily_rewards': 1000,
            'admin_user_ids': [],
            
            # Shop Configuration
            'shop_items_per_page': 10,
            'enable_discounts': True,
            'enable_user_shops': False,
            
            # Server Configuration
            'rcon_timeout': 10,
            'rcon_retry_attempts': 3,
            'server_check_interval': 300,  # 5 minutes
            
            # Reward Tiers
            'reward_tiers': [
                {
                    'name': 'Member',
                    'multiplier': 1.0,
                    'requirements': []
                },
                {
                    'name': 'Donor',
                    'multiplier': 1.5,
                    'requirements': ['donor_role']
                },
                {
                    'name': 'VIP',
                    'multiplier': 2.0,
                    'requirements': ['vip_role']
                }
            ]
        }
    
    def load(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults (in case new config options were added)
                self.config_data = self.default_config.copy()
                self.config_data.update(loaded_config)
                
                logging.info(f"Configuration loaded from {self.config_file}")
                return True
            else:
                # Create default config file
                self.config_data = self.default_config.copy()
                self.save()
                logging.info(f"Created default configuration at {self.config_file}")
                return True
                
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            self.config_data = self.default_config.copy()
            return False
    
    def save(self) -> bool:
        """
        Save configuration to file
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create backup of existing config
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.backup"
                try:
                    os.replace(self.config_file, backup_file)
                except:
                    pass  # Backup failed, but continue with save
            
            # Save configuration
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            
            logging.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        try:
            # Support dot notation for nested keys
            keys = key.split('.')
            value = self.config_data
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default if default is not None else self.default_config.get(key, None)
            
            return value
            
        except Exception:
            return default if default is not None else self.default_config.get(key, None)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            value: Value to set
            
        Returns:
            True if set successfully, False otherwise
        """
        try:
            # Support dot notation for nested keys
            keys = key.split('.')
            current = self.config_data
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Set the value
            current[keys[-1]] = value
            logging.debug(f"Configuration updated: {key} = {value}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to set configuration {key}: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get entire configuration dictionary
        
        Returns:
            Copy of configuration dictionary
        """
        return self.config_data.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save entire configuration dictionary
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            self.config_data = config.copy()
            return self.save()
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values
        
        Returns:
            True if reset successfully, False otherwise
        """
        try:
            self.config_data = self.default_config.copy()
            success = self.save()
            if success:
                logging.info("Configuration reset to defaults")
            return success
        except Exception as e:
            logging.error(f"Failed to reset configuration: {e}")
            return False
    
    def validate_config(self) -> Dict[str, str]:
        """
        Validate current configuration
        
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}
        
        try:
            # Check required Discord settings
            if not self.get('discord_bot_token'):
                errors['discord_bot_token'] = "Discord bot token is required"
            
            # Check reward interval
            reward_interval = self.get('reward_interval', 0)
            if not isinstance(reward_interval, int) or reward_interval < 1:
                errors['reward_interval'] = "Reward interval must be at least 1 minute"
            
            # Check reward amount
            reward_amount = self.get('reward_amount', 0)
            if not isinstance(reward_amount, int) or reward_amount < 1:
                errors['reward_amount'] = "Reward amount must be at least 1 point"
            
            # Check database file path
            db_file = self.get('database_file', '')
            if not db_file:
                errors['database_file'] = "Database file path is required"
            
            # Check log file path
            log_file = self.get('log_file', '')
            if log_file:
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    try:
                        os.makedirs(log_dir, exist_ok=True)
                    except:
                        errors['log_file'] = f"Cannot create log directory: {log_dir}"
            
            # Validate reward tiers
            reward_tiers = self.get('reward_tiers', [])
            if not isinstance(reward_tiers, list):
                errors['reward_tiers'] = "Reward tiers must be a list"
            else:
                for i, tier in enumerate(reward_tiers):
                    if not isinstance(tier, dict):
                        errors[f'reward_tiers.{i}'] = "Each reward tier must be a dictionary"
                        continue
                    
                    if 'name' not in tier or not tier['name']:
                        errors[f'reward_tiers.{i}.name'] = "Tier name is required"
                    
                    if 'multiplier' not in tier or not isinstance(tier['multiplier'], (int, float)):
                        errors[f'reward_tiers.{i}.multiplier'] = "Tier multiplier must be a number"
            
        except Exception as e:
            errors['general'] = f"Configuration validation error: {e}"
        
        return errors
    
    def export_config(self, export_file: str) -> bool:
        """
        Export configuration to a different file
        
        Args:
            export_file: Path to export file
            
        Returns:
            True if exported successfully, False otherwise
        """
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            
            logging.info(f"Configuration exported to {export_file}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, import_file: str) -> bool:
        """
        Import configuration from a file
        
        Args:
            import_file: Path to import file
            
        Returns:
            True if imported successfully, False otherwise
        """
        try:
            if not os.path.exists(import_file):
                logging.error(f"Import file does not exist: {import_file}")
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Validate imported config
            if not isinstance(imported_config, dict):
                logging.error("Imported configuration must be a dictionary")
                return False
            
            # Merge with current config
            self.config_data.update(imported_config)
            
            # Save the updated config
            success = self.save()
            if success:
                logging.info(f"Configuration imported from {import_file}")
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to import configuration: {e}")
            return False
    
    def get_secure_config(self) -> Dict[str, Any]:
        """
        Get configuration with sensitive values masked
        
        Returns:
            Configuration dictionary with sensitive values masked
        """
        secure_config = self.config_data.copy()
        
        # List of sensitive keys to mask
        sensitive_keys = [
            'discord_bot_token',
            'tip4serv_secret', 
            'tip4serv_token',
            'database_password'
        ]
        
        for key in sensitive_keys:
            if key in secure_config and secure_config[key]:
                # Show only first and last 4 characters
                value = str(secure_config[key])
                if len(value) > 8:
                    secure_config[key] = value[:4] + '*' * (len(value) - 8) + value[-4:]
                else:
                    secure_config[key] = '*' * len(value)
        
        return secure_config
