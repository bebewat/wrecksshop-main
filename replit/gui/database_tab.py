"""
Database Tab Module
Manages SQL database connections and configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import threading
import logging
from typing import List, Dict

class DatabaseTab:
    """SQL database management tab"""
    
    def __init__(self, parent, config_manager, db_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.db_manager = db_manager
        self.databases = self.load_databases()
        
        self.create_widgets()
        self.refresh_database_list()
    
    def create_widgets(self):
        """Create database management widgets"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="SQL Databases", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Database list frame
        list_frame = ttk.LabelFrame(main_frame, text="Database Connections")
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Treeview for database list
        columns = ('Name', 'Type', 'Host', 'Database', 'Status')
        self.db_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.db_tree.heading(col, text=col)
            self.db_tree.column(col, width=120)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.db_tree.yview)
        self.db_tree.configure(yscrollcommand=scrollbar.set)
        
        self.db_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        
        # Add database button
        add_btn = ttk.Button(
            button_frame,
            text="Add Database",
            command=self.add_database_dialog
        )
        add_btn.pack(side='left', padx=(0, 10))
        
        # Edit database button
        edit_btn = ttk.Button(
            button_frame,
            text="Edit Database",
            command=self.edit_database_dialog
        )
        edit_btn.pack(side='left', padx=(0, 10))
        
        # Remove database button
        remove_btn = ttk.Button(
            button_frame,
            text="Remove Database",
            command=self.remove_database
        )
        remove_btn.pack(side='left', padx=(0, 10))
        
        # Test connection button
        test_btn = ttk.Button(
            button_frame,
            text="Test Connection",
            command=self.test_connection
        )
        test_btn.pack(side='left', padx=(0, 10))
        
        # Initialize database button
        init_btn = ttk.Button(
            button_frame,
            text="Initialize Tables",
            command=self.initialize_tables
        )
        init_btn.pack(side='left', padx=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_database_list
        )
        refresh_btn.pack(side='right')
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Database Status")
        status_frame.pack(fill='x', pady=(10, 0))
        
        self.status_text = tk.Text(status_frame, height=6, wrap='word')
        status_scrollbar = ttk.Scrollbar(status_frame, orient='vertical', command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        status_scrollbar.pack(side='right', fill='y', pady=5)
        
        # Bind double-click to edit
        self.db_tree.bind('<Double-1>', lambda e: self.edit_database_dialog())
        
        # Add default SQLite database if none exist
        if not self.databases:
            default_db = {
                'name': 'Default SQLite',
                'type': 'sqlite',
                'host': '',
                'port': '',
                'database': 'ark_shop.db',
                'username': '',
                'password': '',
                'status': 'Not Tested'
            }
            self.databases.append(default_db)
            self.save_databases()
    
    def load_databases(self) -> List[Dict]:
        """Load databases from configuration"""
        return self.config_manager.get('databases', [])
    
    def save_databases(self):
        """Save databases to configuration"""
        self.config_manager.set('databases', self.databases)
        self.config_manager.save()
    
    def refresh_database_list(self):
        """Refresh the database list display"""
        # Clear existing items
        for item in self.db_tree.get_children():
            self.db_tree.delete(item)
        
        # Add databases to tree
        for i, db in enumerate(self.databases):
            self.db_tree.insert('', 'end', iid=i, values=(
                db['name'],
                db['type'].upper(),
                db.get('host', 'Local'),
                db['database'],
                db.get('status', 'Unknown')
            ))
    
    def add_database_dialog(self):
        """Show dialog to add new database"""
        dialog = DatabaseDialog(self.parent, "Add Database")
        if dialog.result:
            db_data = dialog.result
            db_data['status'] = 'Not Tested'
            self.databases.append(db_data)
            self.save_databases()
            self.refresh_database_list()
            self.log_status(f"Added database: {db_data['name']}")
    
    def edit_database_dialog(self):
        """Show dialog to edit selected database"""
        selection = self.db_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a database to edit")
            return
        
        db_index = int(selection[0])
        db_data = self.databases[db_index].copy()
        
        dialog = DatabaseDialog(self.parent, "Edit Database", db_data)
        if dialog.result:
            self.databases[db_index] = dialog.result
            self.databases[db_index]['status'] = 'Modified'
            self.save_databases()
            self.refresh_database_list()
            self.log_status(f"Updated database: {dialog.result['name']}")
    
    def remove_database(self):
        """Remove selected database"""
        selection = self.db_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a database to remove")
            return
        
        db_index = int(selection[0])
        db_name = self.databases[db_index]['name']
        
        if messagebox.askyesno("Confirm", f"Remove database '{db_name}'?"):
            del self.databases[db_index]
            self.save_databases()
            self.refresh_database_list()
            self.log_status(f"Removed database: {db_name}")
    
    def test_connection(self):
        """Test connection to selected database"""
        selection = self.db_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a database to test")
            return
        
        db_index = int(selection[0])
        db_data = self.databases[db_index]
        
        self.log_status(f"Testing connection to {db_data['name']}...")
        
        def test_thread():
            try:
                success = self.test_database_connection(db_data)
                
                if success:
                    self.databases[db_index]['status'] = 'Connected'
                    self.log_status(f"✅ Successfully connected to {db_data['name']}")
                else:
                    self.databases[db_index]['status'] = 'Failed'
                    self.log_status(f"❌ Failed to connect to {db_data['name']}")
                
                # Update UI from main thread
                self.parent.after(0, self.refresh_database_list)
                
            except Exception as e:
                self.databases[db_index]['status'] = 'Error'
                self.log_status(f"❌ Error testing {db_data['name']}: {e}")
                self.parent.after(0, self.refresh_database_list)
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def test_database_connection(self, db_data: Dict) -> bool:
        """Test database connection"""
        try:
            if db_data['type'] == 'sqlite':
                # Test SQLite connection
                conn = sqlite3.connect(db_data['database'])
                conn.execute('SELECT 1')
                conn.close()
                return True
            else:
                # For other database types (MySQL, PostgreSQL, etc.)
                # This would need appropriate drivers and connection logic
                self.log_status(f"Database type {db_data['type']} not implemented yet")
                return False
                
        except Exception as e:
            logging.error(f"Database connection test failed: {e}")
            return False
    
    def initialize_tables(self):
        """Initialize database tables for selected database"""
        selection = self.db_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a database to initialize")
            return
        
        db_index = int(selection[0])
        db_data = self.databases[db_index]
        
        if messagebox.askyesno("Confirm", f"Initialize tables in '{db_data['name']}'?\nThis will create required tables for the bot."):
            self.log_status(f"Initializing tables in {db_data['name']}...")
            
            def init_thread():
                try:
                    success = self.db_manager.initialize_database(db_data)
                    
                    if success:
                        self.databases[db_index]['status'] = 'Initialized'
                        self.log_status(f"✅ Successfully initialized {db_data['name']}")
                    else:
                        self.databases[db_index]['status'] = 'Init Failed'
                        self.log_status(f"❌ Failed to initialize {db_data['name']}")
                    
                    self.parent.after(0, self.refresh_database_list)
                    
                except Exception as e:
                    self.databases[db_index]['status'] = 'Error'
                    self.log_status(f"❌ Error initializing {db_data['name']}: {e}")
                    self.parent.after(0, self.refresh_database_list)
            
            threading.Thread(target=init_thread, daemon=True).start()
    
    def log_status(self, message: str):
        """Log status message"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        logging.info(f"Database Tab: {message}")

class DatabaseDialog:
    """Dialog for adding/editing database information"""
    
    def __init__(self, parent, title, db_data=None):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+{}+{}".format(
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.create_widgets(db_data)
        self.dialog.wait_window()
    
    def create_widgets(self, db_data):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Database name
        ttk.Label(main_frame, text="Database Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Database type
        ttk.Label(main_frame, text="Database Type:").grid(row=1, column=0, sticky='w', pady=5)
        self.type_var = tk.StringVar(value='sqlite')
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, values=['sqlite', 'mysql', 'postgresql'], width=28, state='readonly')
        type_combo.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        type_combo.bind('<<ComboboxSelected>>', self.on_type_change)
        
        # Host (disabled for SQLite)
        ttk.Label(main_frame, text="Host:").grid(row=2, column=0, sticky='w', pady=5)
        self.host_entry = ttk.Entry(main_frame, width=30)
        self.host_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Port (disabled for SQLite)
        ttk.Label(main_frame, text="Port:").grid(row=3, column=0, sticky='w', pady=5)
        self.port_entry = ttk.Entry(main_frame, width=30)
        self.port_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Database name/file
        ttk.Label(main_frame, text="Database/File:").grid(row=4, column=0, sticky='w', pady=5)
        self.database_entry = ttk.Entry(main_frame, width=30)
        self.database_entry.grid(row=4, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Username (disabled for SQLite)
        ttk.Label(main_frame, text="Username:").grid(row=5, column=0, sticky='w', pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=5, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Password (disabled for SQLite)
        ttk.Label(main_frame, text="Password:").grid(row=6, column=0, sticky='w', pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show='*')
        self.password_entry.grid(row=6, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Show password checkbox
        self.show_password_var = tk.BooleanVar()
        show_check = ttk.Checkbutton(
            main_frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        )
        show_check.grid(row=7, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Configure column weight
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side='left')
        
        # Load existing data if editing
        if db_data:
            self.name_entry.insert(0, db_data.get('name', ''))
            self.type_var.set(db_data.get('type', 'sqlite'))
            self.host_entry.insert(0, db_data.get('host', ''))
            self.port_entry.insert(0, str(db_data.get('port', '')))
            self.database_entry.insert(0, db_data.get('database', ''))
            self.username_entry.insert(0, db_data.get('username', ''))
            self.password_entry.insert(0, db_data.get('password', ''))
        else:
            self.database_entry.insert(0, 'ark_shop.db')
        
        # Update field states based on database type
        self.on_type_change()
    
    def on_type_change(self, event=None):
        """Handle database type change"""
        db_type = self.type_var.get()
        
        if db_type == 'sqlite':
            # Disable network-related fields for SQLite
            self.host_entry.config(state='disabled')
            self.port_entry.config(state='disabled')
            self.username_entry.config(state='disabled')
            self.password_entry.config(state='disabled')
        else:
            # Enable all fields for network databases
            self.host_entry.config(state='normal')
            self.port_entry.config(state='normal')
            self.username_entry.config(state='normal')
            self.password_entry.config(state='normal')
            
            # Set default ports
            if not self.port_entry.get():
                if db_type == 'mysql':
                    self.port_entry.delete(0, tk.END)
                    self.port_entry.insert(0, '3306')
                elif db_type == 'postgresql':
                    self.port_entry.delete(0, tk.END)
                    self.port_entry.insert(0, '5432')
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')
    
    def ok_clicked(self):
        """Handle OK button click"""
        name = self.name_entry.get().strip()
        db_type = self.type_var.get()
        database = self.database_entry.get().strip()
        
        # Basic validation
        if not all([name, database]):
            messagebox.showerror("Error", "Name and Database fields are required")
            return
        
        # Additional validation for network databases
        if db_type != 'sqlite':
            host = self.host_entry.get().strip()
            port = self.port_entry.get().strip()
            username = self.username_entry.get().strip()
            
            if not all([host, port, username]):
                messagebox.showerror("Error", "Host, Port, and Username are required for network databases")
                return
            
            try:
                port = int(port)
                if not (1 <= port <= 65535):
                    raise ValueError("Port out of range")
            except ValueError:
                messagebox.showerror("Error", "Port must be a valid number between 1 and 65535")
                return
        else:
            host = ''
            port = ''
            username = ''
        
        password = self.password_entry.get()
        
        self.result = {
            'name': name,
            'type': db_type,
            'host': host,
            'port': port,
            'database': database,
            'username': username,
            'password': password
        }
        
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()
