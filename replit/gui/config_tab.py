"""
Configuration Tab Module
Handles Discord bot configuration settings
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

class ConfigTab:
    """Configuration tab for bot settings"""
    
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.entries = {}
        
        self.create_widgets()
        self.load_config()
    
    def create_widgets(self):
        """Create configuration form widgets"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Bot Configuration", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Configuration fields
        configs = [
            ('discord_bot_token', 'Discord Bot Token', True),
            ('discord_shop_channel_id', 'Discord Shop Channel ID', False),
            ('discord_log_channel_id', 'Discord Log Channel ID', False),
            ('tip4serv_secret', 'Tip4Serv Secret', True),
            ('tip4serv_token', 'Tip4Serv Token', True),
            ('reward_interval', 'Reward Interval (minutes)', False),
            ('reward_amount', 'Reward Amount (points)', False),
        ]
        
        row = 1
        for config_key, label_text, is_secret in configs:
            # Label
            label = ttk.Label(main_frame, text=f"{label_text}:")
            label.grid(row=row, column=0, sticky='w', padx=(0, 10), pady=5)
            
            # Entry
            if is_secret:
                entry = ttk.Entry(main_frame, width=50, show='*')
            else:
                entry = ttk.Entry(main_frame, width=50)
            
            entry.grid(row=row, column=1, sticky='ew', pady=5)
            self.entries[config_key] = entry
            
            # Show/Hide button for secret fields
            if is_secret:
                show_var = tk.BooleanVar()
                
                def toggle_visibility(e=entry, var=show_var):
                    if var.get():
                        e.config(show='')
                    else:
                        e.config(show='*')
                
                show_btn = ttk.Checkbutton(
                    main_frame,
                    text="Show",
                    variable=show_var,
                    command=toggle_visibility
                )
                show_btn.grid(row=row, column=2, padx=(10, 0), pady=5)
            
            row += 1
        
        # Configure column weights
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        # Save button
        save_btn = ttk.Button(
            button_frame,
            text="Save Configuration",
            command=self.save_config
        )
        save_btn.pack(side='left', padx=(0, 10))
        
        # Load button
        load_btn = ttk.Button(
            button_frame,
            text="Reload Configuration",
            command=self.load_config
        )
        load_btn.pack(side='left', padx=(0, 10))
        
        # Test connection button
        test_btn = ttk.Button(
            button_frame,
            text="Test Connection",
            command=self.test_connection
        )
        test_btn.pack(side='left')
        
        # Help text
        help_text = """
Configuration Help:
• Discord Bot Token: Your bot's token from Discord Developer Portal
• Shop Channel ID: Channel where shop commands will be used (right-click channel → Copy ID)
• Log Channel ID: Channel for bot logs and notifications
• Tip4Serv Secret/Token: For donation integration (optional)
• Reward Interval: How often to give playtime rewards (in minutes)
• Reward Amount: Base points given per reward interval
        """
        
        help_label = ttk.Label(main_frame, text=help_text, font=('Arial', 9), foreground='gray')
        help_label.grid(row=row+1, column=0, columnspan=3, sticky='w', pady=(20, 0))
    
    def load_config(self):
        """Load configuration values into form"""
        try:
            for config_key, entry in self.entries.items():
                value = self.config_manager.get(config_key, '')
                entry.delete(0, tk.END)
                entry.insert(0, str(value))
            
            logging.info("Configuration loaded successfully")
            
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def save_config(self):
        """Save configuration values from form"""
        try:
            config_data = {}
            
            for config_key, entry in self.entries.items():
                value = entry.get().strip()
                
                # Convert numeric fields
                if config_key in ['reward_interval', 'reward_amount']:
                    if value:
                        try:
                            value = int(value)
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid numeric value for {config_key}")
                            return
                    else:
                        value = 60 if config_key == 'reward_interval' else 10
                
                config_data[config_key] = value
            
            # Save to config manager
            for key, value in config_data.items():
                self.config_manager.set(key, value)
            
            self.config_manager.save()
            
            logging.info("Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def test_connection(self):
        """Test bot connection with current settings"""
        try:
            token = self.entries['discord_bot_token'].get().strip()
            if not token:
                messagebox.showerror("Error", "Discord Bot Token is required for testing")
                return
            
            # Simple token validation
            if not token.startswith(('Bot ', 'mfa.', 'MQ')):
                messagebox.showwarning("Warning", "Token format seems incorrect. Make sure to use the bot token, not client secret.")
            
            messagebox.showinfo("Test", "Token format appears valid. Save configuration and start the bot to test connection.")
            
        except Exception as e:
            logging.error(f"Error testing configuration: {e}")
            messagebox.showerror("Error", f"Failed to test configuration: {e}")
