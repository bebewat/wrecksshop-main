"""
Admin Roles management tab
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class AdminTab:
    def __init__(self, parent, config, logger):
        self.config = config
        self.logger = logger
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_roles()
    
    def setup_ui(self):
        """Setup the admin roles interface"""
        # Main container
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Roles list section
        roles_frame = ttk.LabelFrame(main_frame, text="Admin Roles", padding=10)
        roles_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for roles
        columns = ("Role Name", "Discord Role ID", "Permissions", "Point Multiplier", "Status")
        self.roles_tree = ttk.Treeview(roles_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.roles_tree.heading("Role Name", text="Role Name")
        self.roles_tree.heading("Discord Role ID", text="Discord Role ID")
        self.roles_tree.heading("Permissions", text="Permissions")
        self.roles_tree.heading("Point Multiplier", text="Point Multiplier")
        self.roles_tree.heading("Status", text="Status")
        
        self.roles_tree.column("Role Name", width=150)
        self.roles_tree.column("Discord Role ID", width=150)
        self.roles_tree.column("Permissions", width=200)
        self.roles_tree.column("Point Multiplier", width=120)
        self.roles_tree.column("Status", width=100)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(roles_frame, orient=tk.VERTICAL, command=self.roles_tree.yview)
        self.roles_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.roles_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        button_frame = ttk.Frame(roles_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Role management buttons
        add_btn = ttk.Button(button_frame, text="Add Role", command=self.add_role)
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_btn = ttk.Button(button_frame, text="Edit Role", command=self.edit_role)
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = ttk.Button(button_frame, text="Remove Role", command=self.remove_role)
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        toggle_btn = ttk.Button(button_frame, text="Enable/Disable", command=self.toggle_role)
        toggle_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_btn = ttk.Button(button_frame, text="Refresh", command=self.load_roles)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Users with roles section
        users_frame = ttk.LabelFrame(main_frame, text="Users with Admin Roles", padding=10)
        users_frame.pack(fill=tk.X)
        
        # Users treeview
        user_columns = ("Username", "Discord ID", "Roles", "Last Seen")
        self.users_tree = ttk.Treeview(users_frame, columns=user_columns, show="headings", height=8)
        
        # Configure user columns
        self.users_tree.heading("Username", text="Username")
        self.users_tree.heading("Discord ID", text="Discord ID")
        self.users_tree.heading("Roles", text="Admin Roles")
        self.users_tree.heading("Last Seen", text="Last Seen")
        
        self.users_tree.column("Username", width=150)
        self.users_tree.column("Discord ID", width=150)
        self.users_tree.column("Roles", width=200)
        self.users_tree.column("Last Seen", width=150)
        
        # Add scrollbar for users
        users_scroll = ttk.Scrollbar(users_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scroll.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        users_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # User management buttons
        user_button_frame = ttk.Frame(users_frame)
        user_button_frame.pack(fill=tk.X, pady=(10, 0))
        
        assign_role_btn = ttk.Button(user_button_frame, text="Assign Role", command=self.assign_role)
        assign_role_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_role_btn = ttk.Button(user_button_frame, text="Remove Role", command=self.remove_user_role)
        remove_role_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        view_perms_btn = ttk.Button(user_button_frame, text="View Permissions", command=self.view_user_permissions)
        view_perms_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_users_btn = ttk.Button(user_button_frame, text="Refresh Users", command=self.load_users)
        refresh_users_btn.pack(side=tk.RIGHT)
        
        # Bind selection events
        self.roles_tree.bind("<<TreeviewSelect>>", self.on_role_select)
        self.users_tree.bind("<<TreeviewSelect>>", self.on_user_select)
    
    def load_roles(self):
        """Load admin roles from configuration"""
        try:
            roles = self.config.get('admin_roles', [])
            
            # Clear existing items
            for item in self.roles_tree.get_children():
                self.roles_tree.delete(item)
            
            # Add default roles if none exist
            if not roles:
                default_roles = [
                    {
                        'name': 'Owner',
                        'discord_role_id': '',
                        'permissions': ['*'],
                        'point_multiplier': 5.0,
                        'enabled': True
                    },
                    {
                        'name': 'Admin',
                        'discord_role_id': '',
                        'permissions': ['shop.manage', 'users.manage', 'points.give'],
                        'point_multiplier': 3.0,
                        'enabled': True
                    },
                    {
                        'name': 'Moderator',
                        'discord_role_id': '',
                        'permissions': ['shop.view', 'users.view'],
                        'point_multiplier': 2.0,
                        'enabled': True
                    }
                ]
                roles = default_roles
                self.config.set('admin_roles', roles)
                self.config.save()
            
            # Add roles to tree
            for role in roles:
                permissions_str = ', '.join(role.get('permissions', []))
                if len(permissions_str) > 30:
                    permissions_str = permissions_str[:27] + "..."
                
                status = "Enabled" if role.get('enabled', True) else "Disabled"
                
                self.roles_tree.insert("", tk.END, values=(
                    role.get('name', ''),
                    role.get('discord_role_id', 'Not Set'),
                    permissions_str,
                    f"{role.get('point_multiplier', 1.0)}x",
                    status
                ))
            
            # Load users after roles are loaded
            self.load_users()
                
        except Exception as e:
            self.logger.error(f"Error loading admin roles: {e}")
            messagebox.showerror("Error", f"Failed to load admin roles: {e}")
    
    def load_users(self):
        """Load users with admin roles"""
        try:
            # Clear existing items
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            
            # This would load from database
            # For now, show placeholder data
            placeholder_users = [
                ("AdminUser1", "123456789012345678", "Owner, Admin", "2024-01-15 14:30"),
                ("ModUser1", "987654321098765432", "Moderator", "2024-01-14 09:15"),
                ("AdminUser2", "456789123456789123", "Admin", "2024-01-13 16:45")
            ]
            
            for user in placeholder_users:
                self.users_tree.insert("", tk.END, values=user)
                
        except Exception as e:
            self.logger.error(f"Error loading users: {e}")
    
    def add_role(self):
        """Add new admin role"""
        self.show_role_dialog()
    
    def edit_role(self):
        """Edit selected role"""
        selection = self.roles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a role to edit")
            return
        
        # Get selected role data
        item = self.roles_tree.item(selection[0])
        role_name = item['values'][0]
        
        # Find role in config
        roles = self.config.get('admin_roles', [])
        role_data = None
        
        for role in roles:
            if role.get('name') == role_name:
                role_data = role
                break
        
        if role_data:
            self.show_role_dialog(role_data)
    
    def remove_role(self):
        """Remove selected role"""
        selection = self.roles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a role to remove")
            return
        
        item = self.roles_tree.item(selection[0])
        role_name = item['values'][0]
        
        response = messagebox.askyesno("Confirm Removal", f"Remove admin role '{role_name}'?")
        if not response:
            return
        
        try:
            # Remove from config
            roles = self.config.get('admin_roles', [])
            roles = [role for role in roles if role.get('name') != role_name]
            self.config.set('admin_roles', roles)
            self.config.save()
            
            # Refresh display
            self.load_roles()
            
            messagebox.showinfo("Success", "Role removed successfully")
            
        except Exception as e:
            self.logger.error(f"Error removing role: {e}")
            messagebox.showerror("Error", f"Failed to remove role: {e}")
    
    def toggle_role(self):
        """Toggle role enabled/disabled status"""
        selection = self.roles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a role to toggle")
            return
        
        try:
            item = self.roles_tree.item(selection[0])
            role_name = item['values'][0]
            current_status = item['values'][4]
            
            # Find and update role
            roles = self.config.get('admin_roles', [])
            for role in roles:
                if role.get('name') == role_name:
                    role['enabled'] = current_status == "Disabled"
                    break
            
            self.config.set('admin_roles', roles)
            self.config.save()
            
            # Refresh display
            self.load_roles()
            
            new_status = "enabled" if current_status == "Disabled" else "disabled"
            messagebox.showinfo("Success", f"Role {new_status} successfully")
            
        except Exception as e:
            self.logger.error(f"Error toggling role: {e}")
            messagebox.showerror("Error", f"Failed to toggle role: {e}")
    
    def show_role_dialog(self, role_data=None):
        """Show role add/edit dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Add Role" if role_data is None else "Edit Role")
        dialog.geometry("500x600")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"500x600+{x}+{y}")
        
        # Create scrollable frame
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form fields
        ttk.Label(scrollable_frame, text="Role Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=role_data.get('name', '') if role_data else '')
        ttk.Entry(scrollable_frame, textvariable=name_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(scrollable_frame, text="Discord Role ID:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        role_id_var = tk.StringVar(value=role_data.get('discord_role_id', '') if role_data else '')
        ttk.Entry(scrollable_frame, textvariable=role_id_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(scrollable_frame, text="Point Multiplier:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        multiplier_var = tk.StringVar(value=str(role_data.get('point_multiplier', 1.0)) if role_data else '1.0')
        ttk.Entry(scrollable_frame, textvariable=multiplier_var, width=40).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Permissions section
        perms_frame = ttk.LabelFrame(scrollable_frame, text="Permissions", padding=10)
        perms_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Available permissions
        available_permissions = [
            ("*", "All Permissions (Super Admin)"),
            ("shop.manage", "Manage Shop Items"),
            ("shop.view", "View Shop Statistics"),
            ("users.manage", "Manage Users"),
            ("users.view", "View User Information"),
            ("points.give", "Give Points to Users"),
            ("points.take", "Take Points from Users"),
            ("points.view", "View Point Balances"),
            ("server.manage", "Manage RCON Servers"),
            ("database.manage", "Manage Databases"),
            ("logs.view", "View Bot Logs"),
            ("config.manage", "Manage Bot Configuration"),
            ("roles.manage", "Manage Admin Roles"),
            ("discounts.manage", "Manage Discounts")
        ]
        
        # Permission checkboxes
        permission_vars = {}
        current_permissions = role_data.get('permissions', []) if role_data else []
        
        for i, (perm, desc) in enumerate(available_permissions):
            var = tk.BooleanVar(value=perm in current_permissions)
            permission_vars[perm] = var
            
            ttk.Checkbutton(perms_frame, text=f"{perm} - {desc}", variable=var).grid(
                row=i, column=0, sticky=tk.W, pady=2
            )
        
        # Role settings
        settings_frame = ttk.LabelFrame(scrollable_frame, text="Role Settings", padding=10)
        settings_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        enabled_var = tk.BooleanVar(value=role_data.get('enabled', True) if role_data else True)
        ttk.Checkbutton(settings_frame, text="Role Enabled", variable=enabled_var).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        auto_assign_var = tk.BooleanVar(value=role_data.get('auto_assign', False) if role_data else False)
        ttk.Checkbutton(settings_frame, text="Auto-assign to new users", variable=auto_assign_var).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_role():
            try:
                # Validate inputs
                if not name_var.get().strip():
                    messagebox.showerror("Error", "Role name is required")
                    return
                
                try:
                    multiplier = float(multiplier_var.get())
                    if multiplier <= 0:
                        raise ValueError()
                except ValueError:
                    messagebox.showerror("Error", "Point multiplier must be a positive number")
                    return
                
                # Collect selected permissions
                selected_permissions = []
                for perm, var in permission_vars.items():
                    if var.get():
                        selected_permissions.append(perm)
                
                if not selected_permissions:
                    messagebox.showerror("Error", "At least one permission must be selected")
                    return
                
                # Create role config
                new_role = {
                    'name': name_var.get().strip(),
                    'discord_role_id': role_id_var.get().strip(),
                    'permissions': selected_permissions,
                    'point_multiplier': multiplier,
                    'enabled': enabled_var.get(),
                    'auto_assign': auto_assign_var.get()
                }
                
                # Get existing roles
                roles = self.config.get('admin_roles', [])
                
                if role_data:  # Editing existing role
                    # Find and replace
                    for i, role in enumerate(roles):
                        if role.get('name') == role_data.get('name'):
                            roles[i] = new_role
                            break
                else:  # Adding new role
                    # Check for duplicates
                    for role in roles:
                        if role.get('name') == new_role['name']:
                            messagebox.showerror("Error", "Role with same name already exists")
                            return
                    
                    roles.append(new_role)
                
                # Save configuration
                self.config.set('admin_roles', roles)
                self.config.save()
                
                # Refresh display
                self.load_roles()
                
                messagebox.showinfo("Success", "Role saved successfully")
                dialog.destroy()
                
            except Exception as e:
                self.logger.error(f"Error saving role: {e}")
                messagebox.showerror("Error", f"Failed to save role: {e}")
        
        save_btn = ttk.Button(button_frame, text="Save", command=save_role)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def assign_role(self):
        """Assign role to user"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Assign Role to User")
        dialog.geometry("400x300")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # User selection
        ttk.Label(dialog, text="Discord User ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        user_id_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=user_id_var, width=30).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Username (Optional):").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        username_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=username_var, width=30).grid(row=1, column=1, padx=10, pady=5)
        
        # Role selection
        ttk.Label(dialog, text="Select Roles:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        
        roles_frame = ttk.Frame(dialog)
        roles_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Get available roles
        roles = self.config.get('admin_roles', [])
        role_vars = {}
        
        for i, role in enumerate(roles):
            if role.get('enabled', True):
                var = tk.BooleanVar()
                role_vars[role['name']] = var
                ttk.Checkbutton(roles_frame, text=role['name'], variable=var).grid(
                    row=i, column=0, sticky=tk.W, pady=2
                )
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def assign():
            try:
                user_id = user_id_var.get().strip()
                if not user_id:
                    messagebox.showerror("Error", "Discord User ID is required")
                    return
                
                selected_roles = [role for role, var in role_vars.items() if var.get()]
                if not selected_roles:
                    messagebox.showerror("Error", "At least one role must be selected")
                    return
                
                # This would save to database
                # For now, just show success message
                messagebox.showinfo("Success", f"Assigned roles {', '.join(selected_roles)} to user {user_id}")
                
                # Refresh users display
                self.load_users()
                dialog.destroy()
                
            except Exception as e:
                self.logger.error(f"Error assigning role: {e}")
                messagebox.showerror("Error", f"Failed to assign role: {e}")
        
        assign_btn = ttk.Button(button_frame, text="Assign", command=assign)
        assign_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def remove_user_role(self):
        """Remove role from selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        # This would implement role removal from user
        messagebox.showinfo("Info", "Role removal functionality would be implemented here")
    
    def view_user_permissions(self):
        """View permissions for selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        item = self.users_tree.item(selection[0])
        username = item['values'][0]
        user_roles = item['values'][2]
        
        # Create permissions display dialog
        perms_dialog = tk.Toplevel(self.frame)
        perms_dialog.title(f"Permissions for {username}")
        perms_dialog.geometry("500x400")
        perms_dialog.transient(self.frame)
        
        # Display user permissions
        text_widget = tk.Text(perms_dialog, wrap=tk.WORD)
        scroll = ttk.Scrollbar(perms_dialog, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scroll.set)
        
        # Build permissions text
        perms_text = f"User: {username}\nRoles: {user_roles}\n\nEffective Permissions:\n"
        perms_text += "• shop.manage - Manage Shop Items\n"
        perms_text += "• users.manage - Manage Users\n"
        perms_text += "• points.give - Give Points to Users\n"
        perms_text += "• All other admin permissions...\n"
        
        text_widget.insert(tk.END, perms_text)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def on_role_select(self, event):
        """Handle role selection"""
        # This could show additional role details
        pass
    
    def on_user_select(self, event):
        """Handle user selection"""
        # This could show additional user details
        pass
