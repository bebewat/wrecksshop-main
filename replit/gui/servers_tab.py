"""
RCON Servers Tab Module
Manages Ark server connections for RCON communication
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging
import threading
from typing import Dict, List

from core.rcon_manager import RCONManager

class ServersTab:
    """RCON servers management tab"""
    
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.servers = self.load_servers()
        self.rcon_manager = RCONManager()
        
        self.create_widgets()
        self.refresh_server_list()
    
    def create_widgets(self):
        """Create server management widgets"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="RCON Servers", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Server list frame
        list_frame = ttk.LabelFrame(main_frame, text="Server List")
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Treeview for server list
        columns = ('Name', 'Host', 'Port', 'Status')
        self.server_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.server_tree.heading(col, text=col)
            self.server_tree.column(col, width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.server_tree.yview)
        self.server_tree.configure(yscrollcommand=scrollbar.set)
        
        self.server_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        
        # Add server button
        add_btn = ttk.Button(
            button_frame,
            text="Add Server",
            command=self.add_server_dialog
        )
        add_btn.pack(side='left', padx=(0, 10))
        
        # Edit server button
        edit_btn = ttk.Button(
            button_frame,
            text="Edit Server",
            command=self.edit_server_dialog
        )
        edit_btn.pack(side='left', padx=(0, 10))
        
        # Remove server button
        remove_btn = ttk.Button(
            button_frame,
            text="Remove Server",
            command=self.remove_server
        )
        remove_btn.pack(side='left', padx=(0, 10))
        
        # Test connection button
        test_btn = ttk.Button(
            button_frame,
            text="Test Connection",
            command=self.test_connection
        )
        test_btn.pack(side='left', padx=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_server_list
        )
        refresh_btn.pack(side='right')
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Connection Status")
        status_frame.pack(fill='x', pady=(10, 0))
        
        self.status_text = tk.Text(status_frame, height=6, wrap='word')
        status_scrollbar = ttk.Scrollbar(status_frame, orient='vertical', command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        status_scrollbar.pack(side='right', fill='y', pady=5)
        
        # Bind double-click to edit
        self.server_tree.bind('<Double-1>', lambda e: self.edit_server_dialog())
    
    def load_servers(self) -> List[Dict]:
        """Load servers from configuration"""
        return self.config_manager.get('rcon_servers', [])
    
    def save_servers(self):
        """Save servers to configuration"""
        self.config_manager.set('rcon_servers', self.servers)
        self.config_manager.save()
    
    def refresh_server_list(self):
        """Refresh the server list display"""
        # Clear existing items
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)
        
        # Add servers to tree
        for i, server in enumerate(self.servers):
            status = server.get('status', 'Unknown')
            self.server_tree.insert('', 'end', iid=i, values=(
                server['name'],
                server['host'],
                server['port'],
                status
            ))
    
    def add_server_dialog(self):
        """Show dialog to add new server"""
        dialog = ServerDialog(self.parent, "Add Server")
        if dialog.result:
            server_data = dialog.result
            server_data['status'] = 'Not Tested'
            self.servers.append(server_data)
            self.save_servers()
            self.refresh_server_list()
            self.log_status(f"Added server: {server_data['name']}")
    
    def edit_server_dialog(self):
        """Show dialog to edit selected server"""
        selection = self.server_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a server to edit")
            return
        
        server_index = int(selection[0])
        server_data = self.servers[server_index].copy()
        
        dialog = ServerDialog(self.parent, "Edit Server", server_data)
        if dialog.result:
            self.servers[server_index] = dialog.result
            self.servers[server_index]['status'] = 'Modified'
            self.save_servers()
            self.refresh_server_list()
            self.log_status(f"Updated server: {dialog.result['name']}")
    
    def remove_server(self):
        """Remove selected server"""
        selection = self.server_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a server to remove")
            return
        
        server_index = int(selection[0])
        server_name = self.servers[server_index]['name']
        
        if messagebox.askyesno("Confirm", f"Remove server '{server_name}'?"):
            del self.servers[server_index]
            self.save_servers()
            self.refresh_server_list()
            self.log_status(f"Removed server: {server_name}")
    
    def test_connection(self):
        """Test connection to selected server"""
        selection = self.server_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a server to test")
            return
        
        server_index = int(selection[0])
        server_data = self.servers[server_index]
        
        self.log_status(f"Testing connection to {server_data['name']}...")
        
        def test_thread():
            try:
                success = self.rcon_manager.test_connection(
                    server_data['host'],
                    int(server_data['port']),
                    server_data['password']
                )
                
                if success:
                    self.servers[server_index]['status'] = 'Connected'
                    self.log_status(f"✅ Successfully connected to {server_data['name']}")
                else:
                    self.servers[server_index]['status'] = 'Failed'
                    self.log_status(f"❌ Failed to connect to {server_data['name']}")
                
                # Update UI from main thread
                self.parent.after(0, self.refresh_server_list)
                
            except Exception as e:
                self.servers[server_index]['status'] = 'Error'
                self.log_status(f"❌ Error testing {server_data['name']}: {e}")
                self.parent.after(0, self.refresh_server_list)
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def log_status(self, message: str):
        """Log status message"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        logging.info(f"Server Tab: {message}")

class ServerDialog:
    """Dialog for adding/editing server information"""
    
    def __init__(self, parent, title, server_data=None):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+{}+{}".format(
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.create_widgets(server_data)
        self.dialog.wait_window()
    
    def create_widgets(self, server_data):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Server name
        ttk.Label(main_frame, text="Server Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Host
        ttk.Label(main_frame, text="Host:").grid(row=1, column=0, sticky='w', pady=5)
        self.host_entry = ttk.Entry(main_frame, width=30)
        self.host_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Port
        ttk.Label(main_frame, text="Port:").grid(row=2, column=0, sticky='w', pady=5)
        self.port_entry = ttk.Entry(main_frame, width=30)
        self.port_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(main_frame, text="RCON Password:").grid(row=3, column=0, sticky='w', pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show='*')
        self.password_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Show password checkbox
        self.show_password_var = tk.BooleanVar()
        show_check = ttk.Checkbutton(
            main_frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        )
        show_check.grid(row=4, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Configure column weight
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side='left')
        
        # Load existing data if editing
        if server_data:
            self.name_entry.insert(0, server_data.get('name', ''))
            self.host_entry.insert(0, server_data.get('host', ''))
            self.port_entry.insert(0, str(server_data.get('port', 27015)))
            self.password_entry.insert(0, server_data.get('password', ''))
        else:
            self.port_entry.insert(0, '27015')  # Default Ark RCON port
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')
    
    def ok_clicked(self):
        """Handle OK button click"""
        name = self.name_entry.get().strip()
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        password = self.password_entry.get()
        
        # Validation
        if not all([name, host, port, password]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            port = int(port)
            if not (1 <= port <= 65535):
                raise ValueError("Port out of range")
        except ValueError:
            messagebox.showerror("Error", "Port must be a valid number between 1 and 65535")
            return
        
        self.result = {
            'name': name,
            'host': host,
            'port': port,
            'password': password
        }
        
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()
