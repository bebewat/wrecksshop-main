"""
Shop Items Tab Module
Manages shop items, pricing, and availability
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, List

class ShopTab:
    """Shop items management tab"""
    
    def __init__(self, parent, config_manager, db_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.db_manager = db_manager
        
        self.create_widgets()
        self.refresh_shop_items()
    
    def create_widgets(self):
        """Create shop management widgets"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Shop Items Management", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Shop items frame
        items_frame = ttk.LabelFrame(main_frame, text="Shop Items")
        items_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Treeview for shop items
        columns = ('ID', 'Name', 'Price', 'Category', 'Stock', 'Status')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        column_widths = {'ID': 80, 'Name': 200, 'Price': 80, 'Category': 100, 'Stock': 80, 'Status': 80}
        for col in columns:
            self.items_tree.heading(col, text=col)
            self.items_tree.column(col, width=column_widths[col])
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(items_frame, orient='vertical', command=self.items_tree.yview)
        h_scrollbar = ttk.Scrollbar(items_frame, orient='horizontal', command=self.items_tree.xview)
        self.items_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.items_tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        v_scrollbar.grid(row=0, column=1, sticky='ns', pady=5)
        h_scrollbar.grid(row=1, column=0, sticky='ew', padx=5)
        
        # Configure grid weights
        items_frame.grid_rowconfigure(0, weight=1)
        items_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        
        # Add item button
        add_btn = ttk.Button(
            button_frame,
            text="Add Item",
            command=self.add_item_dialog
        )
        add_btn.pack(side='left', padx=(0, 10))
        
        # Edit item button
        edit_btn = ttk.Button(
            button_frame,
            text="Edit Item",
            command=self.edit_item_dialog
        )
        edit_btn.pack(side='left', padx=(0, 10))
        
        # Remove item button
        remove_btn = ttk.Button(
            button_frame,
            text="Remove Item",
            command=self.remove_item
        )
        remove_btn.pack(side='left', padx=(0, 10))
        
        # Toggle status button
        toggle_btn = ttk.Button(
            button_frame,
            text="Toggle Status",
            command=self.toggle_item_status
        )
        toggle_btn.pack(side='left', padx=(0, 10))
        
        # Import from library button
        import_btn = ttk.Button(
            button_frame,
            text="Import from Library",
            command=self.import_from_library
        )
        import_btn.pack(side='left', padx=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_shop_items
        )
        refresh_btn.pack(side='right')
        
        # Item details frame
        details_frame = ttk.LabelFrame(main_frame, text="Item Details")
        details_frame.pack(fill='x', pady=(10, 0))
        
        # Details text widget
        self.details_text = tk.Text(details_frame, height=6, wrap='word')
        details_scrollbar = ttk.Scrollbar(details_frame, orient='vertical', command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        details_scrollbar.pack(side='right', fill='y', pady=5)
        
        # Bind selection event
        self.items_tree.bind('<<TreeviewSelect>>', self.on_item_select)
        self.items_tree.bind('<Double-1>', lambda e: self.edit_item_dialog())
    
    def refresh_shop_items(self):
        """Refresh shop items display"""
        try:
            # Clear existing items
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            # Get items from database
            items = self.db_manager.get_shop_items()
            
            # Add items to tree
            for item in items:
                status = "Active" if item.get('is_active', True) else "Inactive"
                stock = item.get('stock', 'Unlimited')
                if isinstance(stock, int) and stock < 0:
                    stock = 'Unlimited'
                
                self.items_tree.insert('', 'end', values=(
                    item['id'],
                    item['name'],
                    f"{item['price']} pts",
                    item.get('category', 'General'),
                    stock,
                    status
                ))
            
            logging.info(f"Loaded {len(items)} shop items")
            
        except Exception as e:
            logging.error(f"Error refreshing shop items: {e}")
            messagebox.showerror("Error", f"Failed to load shop items: {e}")
    
    def add_item_dialog(self):
        """Show dialog to add new item"""
        dialog = ShopItemDialog(self.parent, "Add Shop Item")
        if dialog.result:
            try:
                # Add item to database
                self.db_manager.add_shop_item(dialog.result)
                self.refresh_shop_items()
                logging.info(f"Added shop item: {dialog.result['name']}")
                messagebox.showinfo("Success", "Item added successfully!")
                
            except Exception as e:
                logging.error(f"Error adding shop item: {e}")
                messagebox.showerror("Error", f"Failed to add item: {e}")
    
    def edit_item_dialog(self):
        """Show dialog to edit selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        try:
            item_values = self.items_tree.item(selection[0])['values']
            item_id = item_values[0]
            
            # Get full item data from database
            item_data = self.db_manager.get_shop_item(item_id)
            if not item_data:
                messagebox.showerror("Error", "Item not found")
                return
            
            dialog = ShopItemDialog(self.parent, "Edit Shop Item", item_data)
            if dialog.result:
                # Update item in database
                self.db_manager.update_shop_item(item_id, dialog.result)
                self.refresh_shop_items()
                logging.info(f"Updated shop item: {dialog.result['name']}")
                messagebox.showinfo("Success", "Item updated successfully!")
                
        except Exception as e:
            logging.error(f"Error editing shop item: {e}")
            messagebox.showerror("Error", f"Failed to edit item: {e}")
    
    def remove_item(self):
        """Remove selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        try:
            item_values = self.items_tree.item(selection[0])['values']
            item_id = item_values[0]
            item_name = item_values[1]
            
            if messagebox.askyesno("Confirm", f"Remove item '{item_name}' from shop?"):
                self.db_manager.remove_shop_item(item_id)
                self.refresh_shop_items()
                logging.info(f"Removed shop item: {item_name}")
                messagebox.showinfo("Success", "Item removed successfully!")
                
        except Exception as e:
            logging.error(f"Error removing shop item: {e}")
            messagebox.showerror("Error", f"Failed to remove item: {e}")
    
    def toggle_item_status(self):
        """Toggle active status of selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to toggle")
            return
        
        try:
            item_values = self.items_tree.item(selection[0])['values']
            item_id = item_values[0]
            item_name = item_values[1]
            current_status = item_values[5]
            
            new_status = current_status != "Active"
            self.db_manager.update_shop_item_status(item_id, new_status)
            self.refresh_shop_items()
            
            status_text = "activated" if new_status else "deactivated"
            logging.info(f"Item {item_name} {status_text}")
            messagebox.showinfo("Success", f"Item {status_text} successfully!")
            
        except Exception as e:
            logging.error(f"Error toggling item status: {e}")
            messagebox.showerror("Error", f"Failed to toggle item status: {e}")
    
    def import_from_library(self):
        """Open item library for importing items"""
        try:
            from data.item_library import get_item_categories, get_items_by_category
            
            # Create import dialog
            dialog = LibraryImportDialog(self.parent, get_item_categories, get_items_by_category)
            if dialog.selected_items:
                # Add selected items to shop
                added_count = 0
                for item_data in dialog.selected_items:
                    try:
                        # Set default shop properties
                        item_data['price'] = item_data.get('price', 10)
                        item_data['stock'] = -1  # Unlimited
                        item_data['is_active'] = True
                        
                        self.db_manager.add_shop_item(item_data)
                        added_count += 1
                        
                    except Exception as e:
                        logging.error(f"Error adding item {item_data['name']}: {e}")
                
                self.refresh_shop_items()
                messagebox.showinfo("Success", f"Added {added_count} items to shop!")
                
        except Exception as e:
            logging.error(f"Error importing from library: {e}")
            messagebox.showerror("Error", f"Failed to import items: {e}")
    
    def on_item_select(self, event):
        """Handle item selection to show details"""
        selection = self.items_tree.selection()
        if not selection:
            self.details_text.delete(1.0, tk.END)
            return
        
        try:
            item_values = self.items_tree.item(selection[0])['values']
            item_id = item_values[0]
            
            # Get full item data
            item_data = self.db_manager.get_shop_item(item_id)
            if item_data:
                details = f"Item ID: {item_data['id']}\n"
                details += f"Name: {item_data['name']}\n"
                details += f"Price: {item_data['price']} points\n"
                details += f"Category: {item_data.get('category', 'General')}\n"
                details += f"Stock: {item_data.get('stock', 'Unlimited')}\n"
                details += f"RCON Command: {item_data.get('rcon_command', 'N/A')}\n"
                details += f"Description: {item_data.get('description', 'No description')}\n"
                
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(1.0, details)
            
        except Exception as e:
            logging.error(f"Error showing item details: {e}")

class ShopItemDialog:
    """Dialog for adding/editing shop items"""
    
    def __init__(self, parent, title, item_data=None):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+{}+{}".format(
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.create_widgets(item_data)
        self.dialog.wait_window()
    
    def create_widgets(self, item_data):
        """Create dialog widgets"""
        # Create scrollable frame
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        row = 0
        
        # Item name
        ttk.Label(main_frame, text="Item Name:").grid(row=row, column=0, sticky='w', pady=5)
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))
        row += 1
        
        # Item ID/Blueprint
        ttk.Label(main_frame, text="Item ID/Blueprint:").grid(row=row, column=0, sticky='w', pady=5)
        self.id_entry = ttk.Entry(main_frame, width=40)
        self.id_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))
        row += 1
        
        # Category
        ttk.Label(main_frame, text="Category:").grid(row=row, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar(value='General')
        category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, 
                                    values=['General', 'Weapons', 'Armor', 'Tools', 'Resources', 'Consumables', 'Structures'], 
                                    width=38)
        category_combo.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))
        row += 1
        
        # Price
        ttk.Label(main_frame# thoughts
I need to create a comprehensive Python desktop application that manages a Discord bot for Ark Survival: Ascended item shops. The application requires a GUI with multiple tabs (Config, Servers, SQL Databases, Shop, Library, Admin Roles, Discounts, Control) and persistent bottom menu controls. The bot needs RCON integration for Ark servers, point-based economy system, and Discord integration. I'll use tkinter for the GUI, discord.py for bot functionality, python-valve for RCON, and SQLite for data persistence.

The structure will include:
- Main GUI application with tabbed interface
- Discord bot module with command handling
- RCON management for Ark servers
- Database management for points, items, and user data
- Configuration management system
- Logging system
- Item library with Ark items

# useful_guidelines_from_blueprints


# directory_structure
```json
[
    {"path": "main.py", "status": "new"},
    {"path": "gui/main_window.py", "status": "new"},
    {"path": "gui/tabs/config_tab.py", "status": "new"},
    {"path": "gui/tabs/servers_tab.py", "status": "new"},
    {"path": "gui/tabs/database_tab.py", "status": "new"},
    {"path": "gui/tabs/shop_tab.py", "status": "new"},
    {"path": "gui/tabs/library_tab.py", "status": "new"},
    {"path": "gui/tabs/admin_tab.py", "status": "new"},
    {"path": "gui/tabs/discounts_tab.py", "status": "new"},
    {"path": "gui/tabs/control_tab.py", "status": "new"},
    {"path": "bot/discord_bot.py", "status": "new"},
    {"path": "bot/commands.py", "status": "new"},
    {"path": "core/config_manager.py", "status": "new"},
    {"path": "core/database.py", "status": "new"},
    {"path": "core/rcon_manager.py", "status": "new"},
    {"path": "core/point_system.py", "status": "new"},
    {"path": "core/item_library.py", "status": "new"},
    {"path": "core/logger.py", "status": "new"},
    {"path": "utils/tip4serv.py", "status": "new"},
    {"path": "utils/helpers.py", "status": "new"}
]
