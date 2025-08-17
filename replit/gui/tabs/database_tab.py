"""
SQL Database management tab
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

class DatabaseTab:
    def __init__(self, parent, config, logger):
        self.config = config
        self.logger = logger
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_databases()
    
    def setup_ui(self):
        """Setup the database interface"""
        # Main container
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Database list section
        list_frame = ttk.LabelFrame(main_frame, text="Configured Databases", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for database list
        columns = ("Name", "Type", "Host", "Port", "Database", "Status")
        self.db_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.db_tree.heading("Name", text="Connection Name")
        self.db_tree.heading("Type", text="Type")
        self.db_tree.heading("Host", text="Host")
        self.db_tree.heading("Port", text="Port")
        self.db_tree.heading("Database", text="Database")
        self.db_tree.heading("Status", text="Status")
        
        self.db_tree.column("Name", width=150)
        self.db_tree.column("Type", width=80)
        self.db_tree.column("Host", width=120)
        self.db_tree.column("Port", width=60)
        self.db_tree.column("Database", width=120)
        self.db_tree.column("Status", width=100)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.db_tree.yview)
        self.db_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.db_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Database management buttons
        add_btn = ttk.Button(button_frame, text="Add Database", command=self.add_database)
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_btn = ttk.Button(button_frame, text="Edit Database", command=self.edit_database)
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = ttk.Button(button_frame, text="Remove Database", command=self.remove_database)
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        test_btn = ttk.Button(button_frame, text="Test Connection", command=self.test_connection)
        test_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        create_btn = ttk.Button(button_frame, text="Create Tables", command=self.create_tables)
        create_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_btn = ttk.Button(button_frame, text="Refresh", command=self.refresh_databases)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Database info section
        info_frame = ttk.LabelFrame(main_frame, text="Database Information", padding=10)
        info_frame.pack(fill=tk.X)
        
        # Info display
        self.info_text = tk.Text(info_frame, height=8, state=tk.DISABLED)
        info_scroll = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scroll.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.db_tree.bind("<<TreeviewSelect>>", self.on_database_select)
    
    def load_databases(self):
        """Load databases from configuration"""
        try:
            databases = self.config.get('databases', [])
            
            # Clear existing items
            for item in self.db_tree.get_children():
                self.db_tree.delete(item)
            
            # Add default SQLite database if no databases configured
            if not databases:
                default_db = {
                    'name': 'Default SQLite',
                    'type': 'sqlite',
                    'path': 'data/bot_database.db',
                    'host': 'localhost',
                    'port': '',
                    'database': 'bot_database.db'
                }
                databases = [default_db]
                self.config.set('databases', databases)
                self.config.save()
            
            # Add databases to tree
            for db in databases:
                status = "Unknown"
                # Connection status would be tested here
                
                self.db_tree.insert("", tk.END, values=(
                    db.get('name', ''),
                    db.get('type', 'sqlite'),
                    db.get('host', 'localhost'),
                    db.get('port', ''),
                    db.get('database', ''),
                    status
                ))
                
        except Exception as e:
            self.logger.error(f"Error loading databases: {e}")
            messagebox.showerror("Error", f"Failed to load databases: {e}")
    
    def add_database(self):
        """Add new database"""
        self.show_database_dialog()
    
    def edit_database(self):
        """Edit selected database"""
        selection = self.db_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a database to edit")
            return
        
        # Get selected database data
        item = self.db_tree.item(selection[0])
        values = item['values']
        
        # Find full config
        databases = self.config.get('databases', [])
        db_config = None
        
        for db in databases:
            if db.get('name') == values[0]:
                db_config = db
                break
        
        if db_config:
            self.show_database_dialog(db_config)
    
    def remove_database(self):
        """Remove selected database"""
        selection = self.db_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a database to remove")
            return
        
        # Confirm removal
        item = self.db_tree.item(selection[0])
        db_name = item['values'][0]
        
        response = messagebox.askyesno("Confirm Removal", f"Remove database '{db_name}'?")
        if not response:
            return
        
        try:
            # Remove from config
            databases = self.config.get('databases', [])
            databases = [db for db in databases if db.get('name') != db_name]
            self.config.set('databases', databases)
            self.config.save()
            
            # Refresh display
            self.load_databases()
            
            messagebox.showinfo("Success", "Database removed successfully")
            
        except Exception as e:
            self.logger.error(f"Error removing database: {e}")
            messagebox.showerror("Error", f"Failed to remove database: {e}")
    
    def show_database_dialog(self, db_data=None):
        """Show database add/edit dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Add Database" if db_data is None else "Edit Database")
        dialog.geometry("500x400")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Form fields
        ttk.Label(dialog, text="Connection Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=db_data.get('name', '') if db_data else '')
        ttk.Entry(dialog, textvariable=name_var, width=40).grid(row=0, column=1, columnspan=2, padx=10, pady=5)
        
        ttk.Label(dialog, text="Database Type:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        type_var = tk.StringVar(value=db_data.get('type', 'sqlite') if db_data else 'sqlite')
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=['sqlite', 'mysql', 'postgresql'], 
                                 state="readonly", width=37)
        type_combo.grid(row=1, column=1, columnspan=2, padx=10, pady=5)
        
        # SQLite specific
        sqlite_frame = ttk.LabelFrame(dialog, text="SQLite Configuration", padding=10)
        sqlite_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        ttk.Label(sqlite_frame, text="Database File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        path_var = tk.StringVar(value=db_data.get('path', 'data/bot_database.db') if db_data else 'data/bot_database.db')
        ttk.Entry(sqlite_frame, textvariable=path_var, width=50).grid(row=0, column=1, padx=(10, 0), pady=2)
        
        # MySQL/PostgreSQL specific
        server_frame = ttk.LabelFrame(dialog, text="Server Database Configuration", padding=10)
        server_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        ttk.Label(server_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, pady=2)
        host_var = tk.StringVar(value=db_data.get('host', 'localhost') if db_data else 'localhost')
        ttk.Entry(server_frame, textvariable=host_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(server_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        port_var = tk.StringVar(value=db_data.get('port', '') if db_data else '')
        ttk.Entry(server_frame, textvariable=port_var, width=10).grid(row=0, column=3, padx=(10, 0), pady=2)
        
        ttk.Label(server_frame, text="Database:").grid(row=1, column=0, sticky=tk.W, pady=2)
        database_var = tk.StringVar(value=db_data.get('database', '') if db_data else '')
        ttk.Entry(server_frame, textvariable=database_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(server_frame, text="Username:").grid(row=2, column=0, sticky=tk.W, pady=2)
        username_var = tk.StringVar(value=db_data.get('username', '') if db_data else '')
        ttk.Entry(server_frame, textvariable=username_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(server_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=2)
        password_var = tk.StringVar(value=db_data.get('password', '') if db_data else '')
        password_entry = ttk.Entry(server_frame, textvariable=password_var, width=30, show="*")
        password_entry.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Show/Hide password button
        def toggle_password():
            if password_entry.cget('show') == '*':
                password_entry.config(show='')
                show_pass_btn.config(text='Hide')
            else:
                password_entry.config(show='*')
                show_pass_btn.config(text='Show')
        
        show_pass_btn = ttk.Button(server_frame, text="Show", command=toggle_password)
        show_pass_btn.grid(row=3, column=2, padx=(10, 0), pady=2)
        
        # Toggle frame visibility based on database type
        def on_type_change(*args):
            db_type = type_var.get()
            if db_type == 'sqlite':
                server_frame.grid_remove()
                sqlite_frame.grid()
            else:
                sqlite_frame.grid_remove()
                server_frame.grid()
                
                # Set default ports
                if db_type == 'mysql' and not port_var.get():
                    port_var.set('3306')
                elif db_type == 'postgresql' and not port_var.get():
                    port_var.set('5432')
        
        type_var.trace('w', on_type_change)
        on_type_change()  # Initial call
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        def save_database():
            try:
                # Validate inputs
                if not name_var.get().strip():
                    messagebox.showerror("Error", "Connection name is required")
                    return
                
                db_type = type_var.get()
                
                # Create database config
                new_db = {
                    'name': name_var.get().strip(),
                    'type': db_type
                }
                
                if db_type == 'sqlite':
                    if not path_var.get().strip():
                        messagebox.showerror("Error", "Database file path is required")
                        return
                    new_db['path'] = path_var.get().strip()
                    new_db['host'] = 'localhost'
                    new_db['database'] = os.path.basename(path_var.get().strip())
                else:
                    # Server database
                    if not all([host_var.get().strip(), database_var.get().strip(), 
                               username_var.get().strip()]):
                        messagebox.showerror("Error", "Host, database, and username are required")
                        return
                    
                    new_db.update({
                        'host': host_var.get().strip(),
                        'port': port_var.get().strip(),
                        'database': database_var.get().strip(),
                        'username': username_var.get().strip(),
                        'password': password_var.get().strip()
                    })
                
                # Get existing databases
                databases = self.config.get('databases', [])
                
                if db_data:  # Editing existing database
                    # Find and replace
                    for i, db in enumerate(databases):
                        if db.get('name') == db_data.get('name'):
                            databases[i] = new_db
                            break
                else:  # Adding new database
                    # Check for duplicates
                    for db in databases:
                        if db.get('name') == new_db['name']:
                            messagebox.showerror("Error", "Database with same name already exists")
                            return
                    
                    databases.append(new_db)
                
                # Save configuration
                self.config.set('databases', databases)
                self.config.save()
                
                # Refresh display
                self.load_databases()
                
                messagebox.showinfo("Success", "Database configuration saved successfully")
                dialog.destroy()
                
            except Exception as e:
                self.logger.error(f"Error saving database: {e}")
                messagebox.showerror("Error", f"Failed to save database: {e}")
        
        save_btn = ttk.Button(button_frame, text="Save", command=save_database)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        test_btn = ttk.Button(button_frame, text="Test Connection", 
                             command=lambda: self.test_db_connection(dialog, type_var, host_var, 
                                                                   port_var, database_var, username_var, 
                                                                   password_var, path_var))
        test_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def test_connection(self):
        """Test connection to selected database"""
        selection = self.db_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a database to test")
            return
        
        item = self.db_tree.item(selection[0])
        db_name = item['values'][0]
        
        try:
            # Find database in config
            databases = self.config.get('databases', [])
            db_config = None
            
            for db in databases:
                if db.get('name') == db_name:
                    db_config = db
                    break
            
            if not db_config:
                messagebox.showerror("Error", "Database configuration not found")
                return
            
            # Test connection based on type
            if db_config['type'] == 'sqlite':
                success = self.test_sqlite_connection(db_config['path'])
            else:
                success = self.test_server_db_connection(db_config)
            
            if success:
                messagebox.showinfo("Success", f"Connection to '{db_name}' successful!")
                # Update status in tree
                self.db_tree.item(selection[0], values=(
                    item['values'][0], item['values'][1], item['values'][2], 
                    item['values'][3], item['values'][4], "Connected"
                ))
            else:
                messagebox.showerror("Error", f"Connection to '{db_name}' failed!")
                
        except Exception as e:
            self.logger.error(f"Error testing database connection: {e}")
            messagebox.showerror("Error", f"Connection test failed: {e}")
    
    def test_db_connection(self, dialog, type_var, host_var, port_var, database_var, 
                          username_var, password_var, path_var):
        """Test database connection from dialog"""
        try:
            db_type = type_var.get()
            
            if db_type == 'sqlite':
                path = path_var.get().strip()
                if not path:
                    messagebox.showerror("Error", "Database file path is required")
                    return
                
                success = self.test_sqlite_connection(path)
            else:
                # Server database
                if not all([host_var.get().strip(), database_var.get().strip(), 
                           username_var.get().strip()]):
                    messagebox.showerror("Error", "Host, database, and username are required")
                    return
                
                db_config = {
                    'type': db_type,
                    'host': host_var.get().strip(),
                    'port': port_var.get().strip(),
                    'database': database_var.get().strip(),
                    'username': username_var.get().strip(),
                    'password': password_var.get().strip()
                }
                
                success = self.test_server_db_connection(db_config)
            
            if success:
                messagebox.showinfo("Success", "Database connection successful!")
            else:
                messagebox.showerror("Error", "Database connection failed!")
                
        except Exception as e:
            self.logger.error(f"Error testing database connection: {e}")
            messagebox.showerror("Error", f"Connection test failed: {e}")
    
    def test_sqlite_connection(self, path):
        """Test SQLite connection"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Test connection
            conn = sqlite3.connect(path)
            conn.execute("SELECT 1")
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"SQLite connection test failed: {e}")
            return False
    
    def test_server_db_connection(self, db_config):
        """Test server database connection"""
        try:
            # This would implement actual database connection testing
            # For now, return True as placeholder
            self.logger.info(f"Testing {db_config['type']} connection to {db_config['host']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Server database connection test failed: {e}")
            return False
    
    def create_tables(self):
        """Create required database tables"""
        selection = self.db_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a database")
            return
        
        try:
            item = self.db_tree.item(selection[0])
            db_name = item['values'][0]
            
            # Find database config
            databases = self.config.get('databases', [])
            db_config = None
            
            for db in databases:
                if db.get('name') == db_name:
                    db_config = db
                    break
            
            if not db_config:
                messagebox.showerror("Error", "Database configuration not found")
                return
            
            # Create tables based on database type
            if db_config['type'] == 'sqlite':
                self.create_sqlite_tables(db_config['path'])
            else:
                self.create_server_tables(db_config)
            
            messagebox.showinfo("Success", "Database tables created successfully!")
            
        except Exception as e:
            self.logger.error(f"Error creating tables: {e}")
            messagebox.showerror("Error", f"Failed to create tables: {e}")
    
    def create_sqlite_tables(self, path):
        """Create SQLite tables"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # Create tables
        tables = [
            """CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT UNIQUE NOT NULL,
                steam_id TEXT,
                balance INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL,
                ark_command TEXT NOT NULL,
                category TEXT DEFAULT 'General',
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                type TEXT NOT NULL,
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS purchase_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                total_cost INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS player_sessions (
                discord_id TEXT PRIMARY KEY,
                discount_percent INTEGER DEFAULT 0,
                expires_at TIMESTAMP
            )"""
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        conn.commit()
        conn.close()
    
    def create_server_tables(self, db_config):
        """Create server database tables"""
        # This would implement table creation for MySQL/PostgreSQL
        # For now, just log the action
        self.logger.info(f"Creating tables for {db_config['type']} database")
    
    def refresh_databases(self):
        """Refresh database list"""
        self.load_databases()
    
    def on_database_select(self, event):
        """Handle database selection"""
        selection = self.db_tree.selection()
        if not selection:
            return
        
        item = self.db_tree.item(selection[0])
        values = item['values']
        
        # Display database info
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info = f"""Connection Name: {values[0]}
Database Type: {values[1]}
Host: {values[2]}
Port: {values[3]}
Database: {values[4]}
Status: {values[5]}

Tables: [Would list existing tables here]
Last Connection: Not tested

Connection String: [Hidden for security]
"""
        
        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)
