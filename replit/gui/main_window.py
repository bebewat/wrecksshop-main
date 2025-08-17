"""
Main GUI window for the Ark Discord Bot Management Application
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import asyncio
from bot.discord_bot import ArkBot
from utils.config import Config
from utils.logger import Logger

# Import all tab modules
from gui.tabs.config_tab import ConfigTab
from gui.tabs.servers_tab import ServersTab
from gui.tabs.database_tab import DatabaseTab
from gui.tabs.shop_tab import ShopTab
from gui.tabs.library_tab import LibraryTab
from gui.tabs.admin_tab import AdminTab
from gui.tabs.discounts_tab import DiscountsTab
from gui.tabs.control_tab import ControlTab

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Ark Survival: Ascended Discord Bot Manager")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Initialize components
        self.config = Config()
        self.logger = Logger()
        self.bot = ArkBot()
        self.bot_thread = None
        self.bot_running = False
        
        # Setup GUI
        self.setup_ui()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Initialize tabs
        self.setup_tabs()
        
        # Create persistent bottom menu
        self.setup_bottom_menu(main_frame)
    
    def setup_tabs(self):
        """Setup all application tabs"""
        # Config Tab
        self.config_tab = ConfigTab(self.notebook, self.config, self.logger)
        self.notebook.add(self.config_tab.frame, text="Config")
        
        # Servers Tab
        self.servers_tab = ServersTab(self.notebook, self.config, self.logger)
        self.notebook.add(self.servers_tab.frame, text="Servers")
        
        # Database Tab
        self.database_tab = DatabaseTab(self.notebook, self.config, self.logger)
        self.notebook.add(self.database_tab.frame, text="SQL Databases")
        
        # Shop Tab
        self.shop_tab = ShopTab(self.notebook, self.bot, self.logger)
        self.notebook.add(self.shop_tab.frame, text="Shop")
        
        # Library Tab
        self.library_tab = LibraryTab(self.notebook, self.logger)
        self.notebook.add(self.library_tab.frame, text="Library")
        
        # Admin Roles Tab
        self.admin_tab = AdminTab(self.notebook, self.config, self.logger)
        self.notebook.add(self.admin_tab.frame, text="Admin Roles")
        
        # Discounts Tab
        self.discounts_tab = DiscountsTab(self.notebook, self.bot, self.logger)
        self.notebook.add(self.discounts_tab.frame, text="Discounts")
        
        # Control Tab
        self.control_tab = ControlTab(self.notebook, self.bot, self.logger)
        self.notebook.add(self.control_tab.frame, text="Control")
    
    def setup_bottom_menu(self, parent):
        """Setup persistent bottom menu"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Start/Stop Button
        self.start_stop_btn = ttk.Button(
            bottom_frame, 
            text="Start Bot", 
            command=self.toggle_bot
        )
        self.start_stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Logs Button
        logs_btn = ttk.Button(
            bottom_frame, 
            text="View Logs", 
            command=self.show_logs
        )
        logs_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # GitHub Button
        github_btn = ttk.Button(
            bottom_frame, 
            text="GitHub", 
            command=self.open_github
        )
        github_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Discord Button
        discord_btn = ttk.Button(
            bottom_frame, 
            text="Support Discord", 
            command=self.open_discord
        )
        discord_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status Label
        self.status_label = ttk.Label(
            bottom_frame, 
            text="Bot Status: Stopped", 
            foreground="red"
        )
        self.status_label.pack(side=tk.RIGHT)
    
    def toggle_bot(self):
        """Start or stop the Discord bot"""
        if not self.bot_running:
            self.start_bot()
        else:
            self.stop_bot()
    
    def start_bot(self):
        """Start the Discord bot"""
        try:
            # Validate configuration
            token = self.config.get('discord_bot_token')
            if not token:
                messagebox.showerror("Error", "Discord bot token not configured. Please check the Config tab.")
                return
            
            # Start bot in separate thread
            self.bot_thread = threading.Thread(target=self.run_bot_async, daemon=True)
            self.bot_thread.start()
            
            # Update UI
            self.start_stop_btn.config(text="Stop Bot")
            self.status_label.config(text="Bot Status: Starting...", foreground="orange")
            self.bot_running = True
            
            self.logger.info("Bot start initiated")
            
        except Exception as e:
            self.logger.error(f"Error starting bot: {e}")
            messagebox.showerror("Error", f"Failed to start bot: {e}")
    
    def stop_bot(self):
        """Stop the Discord bot"""
        try:
            if self.bot_thread and self.bot_thread.is_alive():
                # Stop the bot
                asyncio.run_coroutine_threadsafe(self.bot.stop_bot(), self.bot.loop)
            
            # Update UI
            self.start_stop_btn.config(text="Start Bot")
            self.status_label.config(text="Bot Status: Stopped", foreground="red")
            self.bot_running = False
            
            self.logger.info("Bot stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping bot: {e}")
            messagebox.showerror("Error", f"Failed to stop bot: {e}")
    
    def run_bot_async(self):
        """Run the bot in async context"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.bot.loop = loop
            
            # Start the bot
            loop.run_until_complete(self.bot.start_bot())
            
        except Exception as e:
            self.logger.error(f"Bot crashed: {e}")
            
            # Update UI from main thread
            self.root.after(0, lambda: self.on_bot_crashed(e))
    
    def on_bot_crashed(self, error):
        """Handle bot crash"""
        self.start_stop_btn.config(text="Start Bot")
        self.status_label.config(text="Bot Status: Crashed", foreground="red")
        self.bot_running = False
        
        messagebox.showerror("Bot Error", f"Bot crashed: {error}")
    
    def show_logs(self):
        """Show logs window"""
        try:
            # Create logs window
            logs_window = tk.Toplevel(self.root)
            logs_window.title("Bot Logs")
            logs_window.geometry("800x600")
            
            # Create text widget with scrollbar
            text_frame = ttk.Frame(logs_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            logs_text = tk.Text(text_frame, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=logs_text.yview)
            logs_text.configure(yscrollcommand=scrollbar.set)
            
            logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Load and display logs
            log_content = self.logger.get_logs()
            logs_text.insert(tk.END, log_content)
            logs_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show logs: {e}")
    
    def open_github(self):
        """Open GitHub repository"""
        import webbrowser
        # This would open the actual repository URL
        webbrowser.open("https://github.com/your-repo/ark-discord-bot")
    
    def open_discord(self):
        """Open support Discord"""
        import webbrowser
        # This would open your Discord server
        webbrowser.open("https://discord.gg/your-invite")
    
    def on_closing(self):
        """Handle application closing"""
        try:
            if self.bot_running:
                response = messagebox.askyesno(
                    "Confirm Exit", 
                    "Bot is currently running. Stop bot and exit?"
                )
                if response:
                    self.stop_bot()
                    self.root.after(1000, self.root.destroy)  # Give time for bot to stop
                return
            
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            self.root.destroy()
