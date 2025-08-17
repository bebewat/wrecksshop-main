"""
Configuration tab for Discord bot settings
"""

import tkinter as tk
from tkinter import ttk, messagebox

class ConfigTab:
    def __init__(self, parent, config, logger):
        self.config = config
        self.logger = logger
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the configuration interface"""
        # Main container with scrollbar
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Discord Configuration Section
        discord_frame = ttk.LabelFrame(scrollable_frame, text="Discord Configuration", padding=10)
        discord_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Discord Bot Token
        ttk.Label(discord_frame, text="Discord Bot Token:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.token_var = tk.StringVar(value=self.config.get('discord_bot_token', ''))
        token_entry = ttk.Entry(discord_frame, textvariable=self.token_var, width=50, show="*")
        token_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Show/Hide Token Button
        self.show_token_btn = ttk.Button(discord_frame, text="Show", command=self.toggle_token_visibility)
        self.show_token_btn.grid(row=0, column=2, padx=(5, 0), pady=2)
        self.token_entry = token_entry
        
        # Discord Shop Channel ID
        ttk.Label(discord_frame, text="Shop Channel ID:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.shop_channel_var = tk.StringVar(value=self.config.get('discord_shop_channel_id', ''))
        ttk.Entry(discord_frame, textvariable=self.shop_channel_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Discord Log Channel ID
        ttk.Label(discord_frame, text="Log Channel ID:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.log_channel_var = tk.StringVar(value=self.config.get('discord_log_channel_id', ''))
        ttk.Entry(discord_frame, textvariable=self.log_channel_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Tip4Serv Configuration Section
        tip4serv_frame = ttk.LabelFrame(scrollable_frame, text="Tip4Serv Configuration", padding=10)
        tip4serv_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Tip4Serv Secret
        ttk.Label(tip4serv_frame, text="Tip4Serv Secret:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.tip4serv_secret_var = tk.StringVar(value=self.config.get('tip4serv_secret', ''))
        secret_entry = ttk.Entry(tip4serv_frame, textvariable=self.tip4serv_secret_var, width=50, show="*")
        secret_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Show/Hide Secret Button
        self.show_secret_btn = ttk.Button(tip4serv_frame, text="Show", command=self.toggle_secret_visibility)
        self.show_secret_btn.grid(row=0, column=2, padx=(5, 0), pady=2)
        self.secret_entry = secret_entry
        
        # Tip4Serv Token
        ttk.Label(tip4serv_frame, text="Tip4Serv Token:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.tip4serv_token_var = tk.StringVar(value=self.config.get('tip4serv_token', ''))
        token_t4s_entry = ttk.Entry(tip4serv_frame, textvariable=self.tip4serv_token_var, width=50, show="*")
        token_t4s_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Show/Hide Token Button
        self.show_token_t4s_btn = ttk.Button(tip4serv_frame, text="Show", command=self.toggle_token_t4s_visibility)
        self.show_token_t4s_btn.grid(row=1, column=2, padx=(5, 0), pady=2)
        self.token_t4s_entry = token_t4s_entry
        
        # Reward Configuration Section
        reward_frame = ttk.LabelFrame(scrollable_frame, text="Reward Configuration", padding=10)
        reward_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Reward Interval
        ttk.Label(reward_frame, text="Reward Interval (minutes):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.reward_interval_var = tk.StringVar(value=str(self.config.get('reward_interval', 60)))
        ttk.Entry(reward_frame, textvariable=self.reward_interval_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Reward Amount
        ttk.Label(reward_frame, text="Reward Amount (points):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.reward_amount_var = tk.StringVar(value=str(self.config.get('reward_amount', 10)))
        ttk.Entry(reward_frame, textvariable=self.reward_amount_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Player Tiers Section
        tiers_frame = ttk.LabelFrame(scrollable_frame, text="Player Reward Tiers", padding=10)
        tiers_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Tier configuration
        self.setup_tier_config(tiers_frame)
        
        # Buttons Section
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Save Button
        save_btn = ttk.Button(button_frame, text="Save Configuration", command=self.save_config)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Reset Button
        reset_btn = ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_config)
        reset_btn.pack(side=tk.LEFT)
        
        # Test Connection Button
        test_btn = ttk.Button(button_frame, text="Test Discord Connection", command=self.test_connection)
        test_btn.pack(side=tk.RIGHT)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_tier_config(self, parent):
        """Setup player tier configuration"""
        # Headers
        ttk.Label(parent, text="Tier Name").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(parent, text="Multiplier").grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(parent, text="Requirements").grid(row=0, column=2, padx=5, pady=2)
        
        # Default tiers
        tiers = self.config.get('player_tiers', {
            'default': {'multiplier': 1.0, 'requirements': 'None'},
            'donor': {'multiplier': 1.5, 'requirements': 'Donation'},
            'vip': {'multiplier': 2.0, 'requirements': 'VIP Status'},
            'admin': {'multiplier': 3.0, 'requirements': 'Admin Role'}
        })
        
        self.tier_vars = {}
        for i, (tier_name, tier_data) in enumerate(tiers.items(), 1):
            # Tier name
            tier_name_var = tk.StringVar(value=tier_name)
            ttk.Entry(parent, textvariable=tier_name_var, width=15).grid(row=i, column=0, padx=5, pady=2)
            
            # Multiplier
            multiplier_var = tk.StringVar(value=str(tier_data['multiplier']))
            ttk.Entry(parent, textvariable=multiplier_var, width=10).grid(row=i, column=1, padx=5, pady=2)
            
            # Requirements
            requirements_var = tk.StringVar(value=tier_data['requirements'])
            ttk.Entry(parent, textvariable=requirements_var, width=20).grid(row=i, column=2, padx=5, pady=2)
            
            self.tier_vars[tier_name] = {
                'name': tier_name_var,
                'multiplier': multiplier_var,
                'requirements': requirements_var
            }
    
    def toggle_token_visibility(self):
        """Toggle Discord token visibility"""
        if self.token_entry.cget('show') == '*':
            self.token_entry.config(show='')
            self.show_token_btn.config(text='Hide')
        else:
            self.token_entry.config(show='*')
            self.show_token_btn.config(text='Show')
    
    def toggle_secret_visibility(self):
        """Toggle Tip4Serv secret visibility"""
        if self.secret_entry.cget('show') == '*':
            self.secret_entry.config(show='')
            self.show_secret_btn.config(text='Hide')
        else:
            self.secret_entry.config(show='*')
            self.show_secret_btn.config(text='Show')
    
    def toggle_token_t4s_visibility(self):
        """Toggle Tip4Serv token visibility"""
        if self.token_t4s_entry.cget('show') == '*':
            self.token_t4s_entry.config(show='')
            self.show_token_t4s_btn.config(text='Hide')
        else:
            self.token_t4s_entry.config(show='*')
            self.show_token_t4s_btn.config(text='Show')
    
    def save_config(self):
        """Save configuration to file"""
        try:
            # Validate inputs
            if not self.token_var.get().strip():
                messagebox.showerror("Error", "Discord Bot Token is required")
                return
            
            try:
                reward_interval = int(self.reward_interval_var.get())
                reward_amount = int(self.reward_amount_var.get())
            except ValueError:
                messagebox.showerror("Error", "Reward interval and amount must be valid numbers")
                return
            
            # Collect tier configuration
            tiers = {}
            for tier_name, tier_vars in self.tier_vars.items():
                name = tier_vars['name'].get().strip()
                try:
                    multiplier = float(tier_vars['multiplier'].get())
                except ValueError:
                    multiplier = 1.0
                
                requirements = tier_vars['requirements'].get().strip()
                
                if name:
                    tiers[name] = {
                        'multiplier': multiplier,
                        'requirements': requirements
                    }
            
            # Save configuration
            config_data = {
                'discord_bot_token': self.token_var.get().strip(),
                'discord_shop_channel_id': self.shop_channel_var.get().strip(),
                'discord_log_channel_id': self.log_channel_var.get().strip(),
                'tip4serv_secret': self.tip4serv_secret_var.get().strip(),
                'tip4serv_token': self.tip4serv_token_var.get().strip(),
                'reward_interval': reward_interval,
                'reward_amount': reward_amount,
                'player_tiers': tiers
            }
            
            self.config.update(config_data)
            self.config.save()
            
            messagebox.showinfo("Success", "Configuration saved successfully")
            self.logger.info("Configuration saved")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def reset_config(self):
        """Reset configuration to defaults"""
        response = messagebox.askyesno("Confirm Reset", "Reset all configuration to defaults?")
        if response:
            # Reset all variables
            self.token_var.set('')
            self.shop_channel_var.set('')
            self.log_channel_var.set('')
            self.tip4serv_secret_var.set('')
            self.tip4serv_token_var.set('')
            self.reward_interval_var.set('60')
            self.reward_amount_var.set('10')
            
            messagebox.showinfo("Success", "Configuration reset to defaults")
    
    def test_connection(self):
        """Test Discord bot connection"""
        try:
            token = self.token_var.get().strip()
            if not token:
                messagebox.showerror("Error", "Please enter a Discord bot token first")
                return
            
            # This would implement actual connection testing
            # For now, just show a placeholder message
            messagebox.showinfo("Test Connection", "Connection test would be implemented here")
            
        except Exception as e:
            self.logger.error(f"Error testing connection: {e}")
            messagebox.showerror("Error", f"Connection test failed: {e}")
