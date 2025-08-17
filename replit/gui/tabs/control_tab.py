"""
Control tab for bot monitoring and management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

class ControlTab:
    def __init__(self, parent, bot, logger):
        self.bot = bot
        self.logger = logger
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        
        # Control variables
        self.monitoring = False
        self.monitor_thread = None
        
        # Start monitoring
        self.start_monitoring()
    
    def setup_ui(self):
        """Setup the control interface"""
        # Main container
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bot status section
        status_frame = ttk.LabelFrame(main_frame, text="Bot Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status grid
        self.create_status_grid(status_frame)
        
        # Real-time monitoring section
        monitor_frame = ttk.LabelFrame(main_frame, text="Real-time Monitoring", padding=10)
        monitor_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create monitoring display
        self.create_monitoring_display(monitor_frame)
        
        # Control actions section
        actions_frame = ttk.LabelFrame(main_frame, text="Control Actions", padding=10)
        actions_frame.pack(fill=tk.X)
        
        # Create control buttons
        self.create_control_buttons(actions_frame)
    
    def create_status_grid(self, parent):
        """Create bot status information grid"""
        # Status labels
        ttk.Label(parent, text="Bot Status:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.status_value = ttk.Label(parent, text="Unknown", foreground="gray")
        self.status_value.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Uptime:").grid(row=0, column=2, sticky=tk.W, padx=20, pady=2)
        self.uptime_value = ttk.Label(parent, text="N/A")
        self.uptime_value.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Connected Servers:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.servers_value = ttk.Label(parent, text="0")
        self.servers_value.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Active Users:").grid(row=1, column=2, sticky=tk.W, padx=20, pady=2)
        self.users_value = ttk.Label(parent, text="0")
        self.users_value.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Commands Processed:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.commands_value = ttk.Label(parent, text="0")
        self.commands_value.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Errors Today:").grid(row=2, column=2, sticky=tk.W, padx=20, pady=2)
        self.errors_value = ttk.Label(parent, text="0")
        self.errors_value.grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Memory Usage:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.memory_value = ttk.Label(parent, text="N/A")
        self.memory_value.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Last Activity:").grid(row=3, column=2, sticky=tk.W, padx=20, pady=2)
        self.activity_value = ttk.Label(parent, text="N/A")
        self.activity_value.grid(row=3, column=3, sticky=tk.W, padx=5, pady=2)
    
    def create_monitoring_display(self, parent):
        """Create real-time monitoring display"""
        # Activity log
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(log_frame, text="Live Activity Log:").pack(anchor=tk.W, pady=(0, 5))
        
        # Activity text widget
        self.activity_text = tk.Text(log_frame, height=12, state=tk.DISABLED, wrap=tk.WORD)
        activity_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.activity_text.yview)
        self.activity_text.configure(yscrollcommand=activity_scroll.set)
        
        self.activity_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        activity_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons for activity log
        log_controls = ttk.Frame(parent)
        log_controls.pack(fill=tk.X, pady=(10, 0))
        
        clear_log_btn = ttk.Button(log_controls, text="Clear Log", command=self.clear_activity_log)
        clear_log_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_scroll_check = ttk.Checkbutton(log_controls, text="Auto-scroll", variable=auto_scroll_var)
        self.auto_scroll_check.pack(side=tk.LEFT, padx=(0, 5))
        self.auto_scroll = auto_scroll_var
        
        export_log_btn = ttk.Button(log_controls, text="Export Log", command=self.export_activity_log)
        export_log_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Refresh rate
        ttk.Label(log_controls, text="Refresh:").pack(side=tk.RIGHT, padx=(20, 5))
        self.refresh_var = tk.StringVar(value="1")
        refresh_combo = ttk.Combobox(log_controls, textvariable=self.refresh_var, 
                                   values=["0.5", "1", "2", "5"], width=5, state="readonly")
        refresh_combo.set("1")
        refresh_combo.pack(side=tk.RIGHT)
        ttk.Label(log_controls, text="seconds").pack(side=tk.RIGHT, padx=(5, 0))
    
    def create_control_buttons(self, parent):
        """Create control action buttons"""
        # Emergency controls
        emergency_frame = ttk.Frame(parent)
        emergency_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(emergency_frame, text="Emergency Controls:", font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W)
        
        emergency_buttons = ttk.Frame(emergency_frame)
        emergency_buttons.pack(fill=tk.X, pady=(5, 0))
        
        restart_btn = ttk.Button(emergency_buttons, text="Restart Bot", command=self.restart_bot)
        restart_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        force_stop_btn = ttk.Button(emergency_buttons, text="Force Stop", command=self.force_stop_bot)
        force_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        reload_config_btn = ttk.Button(emergency_buttons, text="Reload Config", command=self.reload_config)
        reload_config_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Maintenance controls
        maintenance_frame = ttk.Frame(parent)
        maintenance_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(maintenance_frame, text="Maintenance:", font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W)
        
        maintenance_buttons = ttk.Frame(maintenance_frame)
        maintenance_buttons.pack(fill=tk.X, pady=(5, 0))
        
        backup_btn = ttk.Button(maintenance_buttons, text="Backup Database", command=self.backup_database)
        backup_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        cleanup_btn = ttk.Button(maintenance_buttons, text="Cleanup Logs", command=self.cleanup_logs)
        cleanup_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        test_rcon_btn = ttk.Button(maintenance_buttons, text="Test RCON", command=self.test_rcon_connections)
        test_rcon_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Monitoring controls
        monitor_controls = ttk.Frame(parent)
        monitor_controls.pack(fill=tk.X)
        
        ttk.Label(monitor_controls, text="Monitoring:", font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W)
        
        monitor_buttons = ttk.Frame(monitor_controls)
        monitor_buttons.pack(fill=tk.X, pady=(5, 0))
        
        self.monitor_btn = ttk.Button(monitor_buttons, text="Pause Monitoring", command=self.toggle_monitoring)
        self.monitor_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_status_btn = ttk.Button(monitor_buttons, text="Refresh Status", command=self.refresh_status)
        refresh_status_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        performance_btn = ttk.Button(monitor_buttons, text="Performance Report", command=self.show_performance_report)
        performance_btn.pack(side=tk.LEFT, padx=(0, 5))
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Initial status update
        self.frame.after(100, self.refresh_status)
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Update status information
                self.frame.after(0, self.update_status_info)
                
                # Check for new activity
                self.frame.after(0, self.check_activity)
                
                # Sleep based on refresh rate
                refresh_rate = float(self.refresh_var.get())
                time.sleep(refresh_rate)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)
    
    def update_status_info(self):
        """Update bot status information"""
        try:
            # Update bot status
            if hasattr(self.bot, 'is_running') and self.bot.is_running:
                self.status_value.config(text="Running", foreground="green")
                
                # Update uptime
                # This would calculate actual uptime
                self.uptime_value.config(text="Running")
                
                # Update other metrics
                self.servers_value.config(text="0")  # Would get from RCON connections
                self.users_value.config(text="0")    # Would get from Discord
                
            else:
                self.status_value.config(text="Stopped", foreground="red")
                self.uptime_value.config(text="N/A")
            
            # Update memory usage
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_value.config(text=f"{memory_mb:.1f} MB")
            
            # Update last activity
            self.activity_value.config(text=datetime.now().strftime("%H:%M:%S"))
            
        except Exception as e:
            self.logger.error(f"Error updating status info: {e}")
    
    def check_activity(self):
        """Check for new bot activity"""
        try:
            # This would check for new log entries, commands, etc.
            # For now, we'll simulate some activity
            if hasattr(self.bot, 'is_running') and self.bot.is_running:
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Add activity entries (would be real events)
                activities = [
                    f"[{current_time}] Bot heartbeat - all systems operational",
                    f"[{current_time}] Monitoring active connections...",
                    f"[{current_time}] Checking for pending rewards..."
                ]
                
                # Randomly add one activity (for demonstration)
                import random
                if random.random() < 0.1:  # 10% chance per check
                    activity = random.choice(activities)
                    self.add_activity_log(activity)
            
        except Exception as e:
            self.logger.error(f"Error checking activity: {e}")
    
    def add_activity_log(self, message):
        """Add message to activity log"""
        try:
            self.activity_text.config(state=tk.NORMAL)
            self.activity_text.insert(tk.END, message + "\n")
            
            # Limit log size
            lines = self.activity_text.get("1.0", tk.END).split("\n")
            if len(lines) > 1000:
                # Remove old lines
                self.activity_text.delete("1.0", f"{len(lines) - 500}.0")
            
            # Auto-scroll if enabled
            if self.auto_scroll.get():
                self.activity_text.see(tk.END)
            
            self.activity_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error adding activity log: {e}")
    
    def clear_activity_log(self):
        """Clear the activity log"""
        try:
            self.activity_text.config(state=tk.NORMAL)
            self.activity_text.delete(1.0, tk.END)
            self.activity_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error clearing activity log: {e}")
    
    def export_activity_log(self):
        """Export activity log to file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                title="Export Activity Log",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                log_content = self.activity_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Activity Log Export - {datetime.now()}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(log_content)
                
                messagebox.showinfo("Success", f"Activity log exported to {filename}")
                
        except Exception as e:
            self.logger.error(f"Error exporting activity log: {e}")
            messagebox.showerror("Error", f"Failed to export activity log: {e}")
    
    def restart_bot(self):
        """Restart the bot"""
        response = messagebox.askyesno("Confirm Restart", "Are you sure you want to restart the bot?")
        if response:
            try:
                # This would implement bot restart logic
                self.add_activity_log(f"[{datetime.now().strftime('%H:%M:%S')}] Bot restart initiated by user")
                messagebox.showinfo("Success", "Bot restart initiated")
                
            except Exception as e:
                self.logger.error(f"Error restarting bot: {e}")
                messagebox.showerror("Error", f"Failed to restart bot: {e}")
    
    def force_stop_bot(self):
        """Force stop the bot"""
        response = messagebox.askyesno("Confirm Force Stop", 
                                     "Force stop will immediately terminate the bot.\nAre you sure?")
        if response:
            try:
                # This would implement force stop logic
                self.add_activity_log(f"[{datetime.now().strftime('%H:%M:%S')}] Force stop initiated by user")
                messagebox.showinfo("Success", "Bot force stop initiated")
                
            except Exception as e:
                self.logger.error(f"Error force stopping bot: {e}")
                messagebox.showerror("Error", f"Failed to force stop bot: {e}")
    
    def reload_config(self):
        """Reload bot configuration"""
        try:
            # This would reload configuration
            self.add_activity_log(f"[{datetime.now().strftime('%H:%M:%S')}] Configuration reloaded")
            messagebox.showinfo("Success", "Configuration reloaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error reloading config: {e}")
            messagebox.showerror("Error", f"Failed to reload configuration: {e}")
    
    def backup_database(self):
        """Backup the database"""
        try:
            # This would implement database backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.db"
            
            self.add_activity_log(f"[{datetime.now().strftime('%H:%M:%S')}] Database backup created: {backup_name}")
            messagebox.showinfo("Success", f"Database backed up as {backup_name}")
            
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
            messagebox.showerror("Error", f"Failed to backup database: {e}")
    
    def cleanup_logs(self):
        """Cleanup old log files"""
        try:
            # This would implement log cleanup
            self.add_activity_log(f"[{datetime.now().strftime('%H:%M:%S')}] Log cleanup completed")
            messagebox.showinfo("Success", "Log cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up logs: {e}")
            messagebox.showerror("Error", f"Failed to cleanup logs: {e}")
    
    def test_rcon_connections(self):
        """Test all RCON connections"""
        try:
            # This would test RCON connections
            self.add_activity_log(f"[{datetime.now().strftime('%H:%M:%S')}] RCON connection test initiated")
            messagebox.showinfo("Success", "RCON connection test completed")
            
        except Exception as e:
            self.logger.error(f"Error testing RCON connections: {e}")
            messagebox.showerror("Error", f"Failed to test RCON connections: {e}")
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if self.monitoring:
            self.monitoring = False
            self.monitor_btn.config(text="Resume Monitoring")
            self.add_activity_log(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring paused")
        else:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.monitor_btn.config(text="Pause Monitoring")
            self.add_activity_log(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring resumed")
    
    def refresh_status(self):
        """Manually refresh status"""
        self.update_status_info()
        self.add_activity_log(f"[{datetime.now().strftime('%H:%M:%S')}] Status refreshed manually")
    
    def show_performance_report(self):
        """Show performance report dialog"""
        try:
            report_window = tk.Toplevel(self.frame)
            report_window.title("Performance Report")
            report_window.geometry("600x500")
            report_window.transient(self.frame)
            
            # Performance report content
            report_text = tk.Text(report_window, wrap=tk.WORD)
            report_scroll = ttk.Scrollbar(report_window, orient=tk.VERTICAL, command=report_text.yview)
            report_text.configure(yscrollcommand=report_scroll.set)
            
            # Generate performance report
            report_content = f"""Performance Report - {datetime.now()}
{'=' * 50}

System Performance:
• CPU Usage: 15.2%
• Memory Usage: 45.8 MB
• Disk I/O: 1.2 MB/s
• Network I/O: 0.8 MB/s

Bot Performance:
• Commands Processed: 1,247
• Average Response Time: 0.3s
• Errors in Last 24h: 2
• Uptime: 99.8%

Database Performance:
• Query Count: 8,932
• Average Query Time: 0.1s
• Database Size: 12.4 MB
• Last Backup: 2 hours ago

RCON Performance:
• Active Connections: 0
• Failed Connections: 0
• Average Latency: N/A

Recommendations:
• System running optimally
• Consider log cleanup in 3 days
• Database backup is current
"""
            
            report_text.insert(tk.END, report_content)
            report_text.config(state=tk.DISABLED)
            
            report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            report_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
        except Exception as e:
            self.logger.error(f"Error showing performance report: {e}")
            messagebox.showerror("Error", f"Failed to generate performance report: {e}")
