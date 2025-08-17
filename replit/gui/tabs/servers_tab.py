"""
RCON Servers management tab
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.rcon import RCONManager

class ServersTab:
    def __init__(self, parent, config, logger):
        self.config = config
        self.logger = logger
        self.rcon_manager = RCONManager()
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_servers()
    
    def setup_ui(self):
        """Setup the servers interface"""
        # Main container
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Server list section
        list_frame = ttk.LabelFrame(main_frame, text="Configured Servers", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for server list
        columns = ("Name", "Host", "Port", "Status")
        self.server_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.server_tree.heading("Name", text="Server Name")
        self.server_tree.heading("Host", text="Host")
        self.server_tree.heading("Port", text="Port")
        self.server_tree.heading("Status", text="Status")
        
        self.server_tree.column("Name", width=200)
        self.server_tree.column("Host", width=150)
        self.server_tree.column("Port", width=80)
        self.server_tree.column("Status", width=100)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.server_tree.yview)
        self.server_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.server_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Server management buttons
        add_btn = ttk.Button(button_frame, text="Add Server", command=self.add_server)
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_btn = ttk.Button(button_frame, text="Edit Server", command=self.edit_server)
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = ttk.Button(button_frame, text="Remove Server", command=self.remove_server)
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        test_btn = ttk.Button(button_frame, text="Test Connection", command=self.test_connection)
        test_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_btn = ttk.Button(button_frame, text="Refresh", command=self.refresh_servers)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Server details section
        details_frame = ttk.LabelFrame(main_frame, text="Server Details", padding=10)
        details_frame.pack(fill=tk.X)
        
        # Details display
        self.details_text = tk.Text(details_frame, height=6, state=tk.DISABLED)
        details_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.server_tree.bind("<<TreeviewSelect>>", self.on_server_select)
    
    def load_servers(self):
        """Load servers from configuration"""
        try:
            servers = self.config.get('rcon_servers', [])
            
            # Clear existing items
            for item in self.server_tree.get_children():
                self.server_tree.delete(item)
            
            # Add servers to tree
            for server in servers:
                status = "Unknown"
                # Test connection status would be implemented here
                
                self.server_tree.insert("", tk.END, values=(
                    server.get('name', ''),
                    server.get('host', ''),
                    server.get('port', ''),
                    status
                ))
                
        except Exception as e:
            self.logger.error(f"Error loading servers: {e}")
            messagebox.showerror("Error", f"Failed to load servers: {e}")
    
    def add_server(self):
        """Add new server"""
        self.show_server_dialog()
    
    def edit_server(self):
        """Edit selected server"""
        selection = self.server_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a server to edit")
            return
        
        # Get selected server data
        item = self.server_tree.item(selection[0])
        values = item['values']
        
        server_data = {
            'name': values[0],
            'host': values[1],
            'port': values[2]
        }
        
        # Get password from config
        servers = self.config.get('rcon_servers', [])
        for server in servers:
            if (server.get('name') == server_data['name'] and 
                server.get('host') == server_data['host']):
                server_data['password'] = server.get('password', '')
                break
        
        self.show_server_dialog(server_data)
    
    def remove_server(self):
        """Remove selected server"""
        selection = self.server_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a server to remove")
            return
        
        # Confirm removal
        item = self.server_tree.item(selection[0])
        server_name = item['values'][0]
        
        response = messagebox.askyesno("Confirm Removal", f"Remove server '{server_name}'?")
        if not response:
            return
        
        try:
            # Remove from config
            servers = self.config.get('rcon_servers', [])
            servers = [s for s in servers if s.get('name') != server_name]
            self.config.set('rcon_servers', servers)
            self.config.save()
            
            # Refresh display
            self.load_servers()
            
            messagebox.showinfo("Success", "Server removed successfully")
            
        except Exception as e:
            self.logger.error(f"Error removing server: {e}")
            messagebox.showerror("Error", f"Failed to remove server: {e}")
    
    def show_server_dialog(self, server_data=None):
        """Show server add/edit dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Add Server" if server_data is None else "Edit Server")
        dialog.geometry("400x300")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # Form fields
        ttk.Label(dialog, text="Server Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=server_data.get('name', '') if server_data else '')
        ttk.Entry(dialog, textvariable=name_var, width=30).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Host/IP:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        host_var = tk.StringVar(value=server_data.get('host', '') if server_data else '')
        ttk.Entry(dialog, textvariable=host_var, width=30).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="RCON Port:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        port_var = tk.StringVar(value=server_data.get('port', '27020') if server_data else '27020')
        ttk.Entry(dialog, textvariable=port_var, width=30).grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="RCON Password:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        password_var = tk.StringVar(value=server_data.get('password', '') if server_data else '')
        password_entry = ttk.Entry(dialog, textvariable=password_var, width=30, show="*")
        password_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Show/Hide password button
        def toggle_password():
            if password_entry.cget('show') == '*':
                password_entry.config(show='')
                show_pass_btn.config(text='Hide')
            else:
                password_entry.config(show='*')
                show_pass_btn.config(text='Show')
        
        show_pass_btn = ttk.Button(dialog, text="Show", command=toggle_password)
        show_pass_btn.grid(row=3, column=2, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        def save_server():
            try:
                # Validate inputs
                if not all([name_var.get().strip(), host_var.get().strip(), 
                           port_var.get().strip(), password_var.get().strip()]):
                    messagebox.showerror("Error", "All fields are required")
                    return
                
                try:
                    port = int(port_var.get())
                except ValueError:
                    messagebox.showerror("Error", "Port must be a valid number")
                    return
                
                # Create server config
                new_server = {
                    'name': name_var.get().strip(),
                    'host': host_var.get().strip(),
                    'port': port,
                    'password': password_var.get().strip()
                }
                
                # Get existing servers
                servers = self.config.get('rcon_servers', [])
                
                if server_data:  # Editing existing server
                    # Find and replace
                    for i, server in enumerate(servers):
                        if (server.get('name') == server_data.get('name') and
                            server.get('host') == server_data.get('host')):
                            servers[i] = new_server
                            break
                else:  # Adding new server
                    # Check for duplicates
                    for server in servers:
                        if (server.get('name') == new_server['name'] or
                            (server.get('host') == new_server['host'] and 
                             server.get('port') == new_server['port'])):
                            messagebox.showerror("Error", "Server with same name or host/port already exists")
                            return
                    
                    servers.append(new_server)
                
                # Save configuration
                self.config.set('rcon_servers', servers)
                self.config.save()
                
                # Refresh display
                self.load_servers()
                
                messagebox.showinfo("Success", "Server saved successfully")
                dialog.destroy()
                
            except Exception as e:
                self.logger.error(f"Error saving server: {e}")
                messagebox.showerror("Error", f"Failed to save server: {e}")
        
        save_btn = ttk.Button(button_frame, text="Save", command=save_server)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def test_connection(self):
        """Test connection to selected server"""
        selection = self.server_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a server to test")
            return
        
        item = self.server_tree.item(selection[0])
        server_name = item['values'][0]
        
        try:
            # Find server in config
            servers = self.config.get('rcon_servers', [])
            server_config = None
            
            for server in servers:
                if server.get('name') == server_name:
                    server_config = server
                    break
            
            if not server_config:
                messagebox.showerror("Error", "Server configuration not found")
                return
            
            # Test connection
            result = self.rcon_manager.test_connection(
                server_config['host'],
                server_config['port'],
                server_config['password']
            )
            
            if result:
                messagebox.showinfo("Success", f"Connection to '{server_name}' successful!")
                # Update status in tree
                self.server_tree.item(selection[0], values=(
                    item['values'][0], item['values'][1], item['values'][2], "Connected"
                ))
            else:
                messagebox.showerror("Error", f"Connection to '{server_name}' failed!")
                
        except Exception as e:
            self.logger.error(f"Error testing connection: {e}")
            messagebox.showerror("Error", f"Connection test failed: {e}")
    
    def refresh_servers(self):
        """Refresh server list and status"""
        self.load_servers()
        
        # Test all connections in background
        # This would be implemented with threading for better UX
        
    def on_server_select(self, event):
        """Handle server selection"""
        selection = self.server_tree.selection()
        if not selection:
            return
        
        item = self.server_tree.item(selection[0])
        values = item['values']
        
        # Display server details
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        details = f"""Server Name: {values[0]}
Host: {values[1]}
Port: {values[2]}
Status: {values[3]}

RCON Password: [Hidden for security]

Last Connection Test: Not tested
"""
        
        self.details_text.insert(tk.END, details)
        self.details_text.config(state=tk.DISABLED)
