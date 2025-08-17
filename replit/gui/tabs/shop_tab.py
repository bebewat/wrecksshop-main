"""
Shop management tab for creating and editing shop items
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from data.item_library import ITEM_LIBRARY

class ShopTab:
    def __init__(self, parent, bot, logger):
        self.bot = bot
        self.logger = logger
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_shop_items()
    
    def setup_ui(self):
        """Setup the shop interface"""
        # Main paned window
        paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Shop items list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=2)
        
        # Shop items section
        items_frame = ttk.LabelFrame(left_frame, text="Current Shop Items", padding=10)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for shop items
        columns = ("ID", "Name", "Price", "Category", "Status")
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.items_tree.heading("ID", text="ID")
        self.items_tree.heading("Name", text="Item Name")
        self.items_tree.heading("Price", text="Price")
        self.items_tree.heading("Category", text="Category")
        self.items_tree.heading("Status", text="Status")
        
        self.items_tree.column("ID", width=50)
        self.items_tree.column("Name", width=200)
        self.items_tree.column("Price", width=80)
        self.items_tree.column("Category", width=100)
        self.items_tree.column("Status", width=80)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons for shop management
        shop_buttons = ttk.Frame(left_frame)
        shop_buttons.pack(fill=tk.X)
        
        add_item_btn = ttk.Button(shop_buttons, text="Add Item", command=self.add_item)
        add_item_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_item_btn = ttk.Button(shop_buttons, text="Edit Item", command=self.edit_item)
        edit_item_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_item_btn = ttk.Button(shop_buttons, text="Remove Item", command=self.remove_item)
        remove_item_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        toggle_btn = ttk.Button(shop_buttons, text="Enable/Disable", command=self.toggle_item)
        toggle_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_btn = ttk.Button(shop_buttons, text="Refresh", command=self.load_shop_items)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Right panel - Item details and editor
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        # Item editor section
        editor_frame = ttk.LabelFrame(right_frame, text="Item Editor", padding=10)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        ttk.Label(editor_frame, text="Item Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(editor_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(editor_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.desc_var = tk.StringVar()
        ttk.Entry(editor_frame, textvariable=self.desc_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(editor_frame, text="Price (Points):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.price_var = tk.StringVar()
        ttk.Entry(editor_frame, textvariable=self.price_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(editor_frame, text="Category:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(editor_frame, textvariable=self.category_var, width=27)
        category_combo['values'] = ("Weapons", "Armor", "Resources", "Tools", "Consumables", "Structures", "Other")
        category_combo.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(editor_frame, text="Ark Command:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.command_var = tk.StringVar()
        command_entry = tk.Text(editor_frame, width=35, height=3)
        command_entry.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        self.command_entry = command_entry
        
        # Help text
        help_text = tk.Text(editor_frame, width=40, height=4, state=tk.DISABLED)
        help_text.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        help_text.config(state=tk.NORMAL)
        help_text.insert(tk.END, "Command Format Help:\n")
        help_text.insert(tk.END, "Use {steam_id} for player Steam ID\n")
        help_text.insert(tk.END, "Use {quantity} for item quantity\n")
        help_text.insert(tk.END, "Example: GiveItemToPlayer {steam_id} \"Blueprint'/Game/Items/Item.Item'\" {quantity} 1 0")
        help_text.config(state=tk.DISABLED)
        
        # Editor buttons
        editor_buttons = ttk.Frame(editor_frame)
        editor_buttons.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        save_btn = ttk.Button(editor_buttons, text="Save Item", command=self.save_item)
        save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = ttk.Button(editor_buttons, text="Clear Form", command=self.clear_form)
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        from_library_btn = ttk.Button(editor_buttons, text="From Library", command=self.show_library)
        from_library_btn.pack(side=tk.LEFT)
        
        # Bind selection event
        self.items_tree.bind("<<TreeviewSelect>>", self.on_item_select)
        
        # Store current item ID for editing
        self.current_item_id = None
    
    def load_shop_items(self):
        """Load shop items from database"""
        try:
            # Clear existing items
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            # This would load from database
            # For now, show placeholder
            self.items_tree.insert("", tk.END, values=(
                "1", "Example Item", "100", "Weapons", "Enabled"
            ))
            
        except Exception as e:
            self.logger.error(f"Error loading shop items: {e}")
            messagebox.showerror("Error", f"Failed to load shop items: {e}")
    
    def add_item(self):
        """Add new item mode"""
        self.current_item_id = None
        self.clear_form()
    
    def edit_item(self):
        """Edit selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item = self.items_tree.item(selection[0])
        values = item['values']
        
        # Load item data into form
        self.current_item_id = values[0]
        self.name_var.set(values[1])
        self.price_var.set(values[2])
        self.category_var.set(values[3])
        
        # Load full item data from database
        # This would fetch description and command from database
        self.desc_var.set("Example description")
        self.command_entry.delete(1.0, tk.END)
        self.command_entry.insert(tk.END, "GiveItemToPlayer {steam_id} \"Blueprint'/Game/Items/Example.Example'\" {quantity} 1 0")
    
    def remove_item(self):
        """Remove selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        item = self.items_tree.item(selection[0])
        item_name = item['values'][1]
        
        response = messagebox.askyesno("Confirm Removal", f"Remove item '{item_name}' from shop?")
        if not response:
            return
        
        try:
            # Remove from database
            item_id = item['values'][0]
            # await self.bot.shop.delete_shop_item(item_id)
            
            # Refresh display
            self.load_shop_items()
            self.clear_form()
            
            messagebox.showinfo("Success", "Item removed successfully")
            
        except Exception as e:
            self.logger.error(f"Error removing item: {e}")
            messagebox.showerror("Error", f"Failed to remove item: {e}")
    
    def toggle_item(self):
        """Toggle item enabled/disabled status"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to toggle")
            return
        
        try:
            item = self.items_tree.item(selection[0])
            item_id = item['values'][0]
            current_status = item['values'][4]
            
            new_status = "Disabled" if current_status == "Enabled" else "Enabled"
            enabled = new_status == "Enabled"
            
            # Update in database
            # await self.bot.shop.update_shop_item(item_id, enabled=enabled)
            
            # Update tree display
            self.items_tree.item(selection[0], values=(
                item['values'][0], item['values'][1], item['values'][2], 
                item['values'][3], new_status
            ))
            
            messagebox.showinfo("Success", f"Item {new_status.lower()} successfully")
            
        except Exception as e:
            self.logger.error(f"Error toggling item: {e}")
            messagebox.showerror("Error", f"Failed to toggle item: {e}")
    
    def save_item(self):
        """Save current item"""
        try:
            # Validate form
            if not all([self.name_var.get().strip(), self.price_var.get().strip(), 
                       self.category_var.get().strip()]):
                messagebox.showerror("Error", "Name, price, and category are required")
                return
            
            try:
                price = int(self.price_var.get())
                if price <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Price must be a positive number")
                return
            
            command = self.command_entry.get(1.0, tk.END).strip()
            if not command:
                messagebox.showerror("Error", "Ark command is required")
                return
            
            # Prepare item data
            item_data = {
                'name': self.name_var.get().strip(),
                'description': self.desc_var.get().strip(),
                'price': price,
                'ark_command': command,
                'category': self.category_var.get().strip()
            }
            
            # Save to database
            if self.current_item_id:
                # Update existing item
                # await self.bot.shop.update_shop_item(self.current_item_id, **item_data)
                messagebox.showinfo("Success", "Item updated successfully")
            else:
                # Add new item
                # await self.bot.shop.add_shop_item(**item_data)
                messagebox.showinfo("Success", "Item added successfully")
            
            # Refresh display
            self.load_shop_items()
            self.clear_form()
            
        except Exception as e:
            self.logger.error(f"Error saving item: {e}")
            messagebox.showerror("Error", f"Failed to save item: {e}")
    
    def clear_form(self):
        """Clear the form"""
        self.current_item_id = None
        self.name_var.set('')
        self.desc_var.set('')
        self.price_var.set('')
        self.category_var.set('')
        self.command_entry.delete(1.0, tk.END)
    
    def show_library(self):
        """Show item library selection dialog"""
        library_dialog = tk.Toplevel(self.frame)
        library_dialog.title("Item Library")
        library_dialog.geometry("600x500")
        library_dialog.transient(self.frame)
        library_dialog.grab_set()
        
        # Center the dialog
        library_dialog.update_idletasks()
        x = (library_dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (library_dialog.winfo_screenheight() // 2) - (500 // 2)
        library_dialog.geometry(f"600x500+{x}+{y}")
        
        # Search frame
        search_frame = ttk.Frame(library_dialog)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Category filter
        ttk.Label(search_frame, text="Category:").pack(side=tk.LEFT, padx=(20, 5))
        filter_var = tk.StringVar()
        filter_combo = ttk.Combobox(search_frame, textvariable=filter_var, width=15)
        filter_combo['values'] = ("All", "Weapons", "Armor", "Resources", "Tools", "Consumables", "Structures")
        filter_combo.set("All")
        filter_combo.pack(side=tk.LEFT)
        
        # Library items list
        list_frame = ttk.Frame(library_dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("Name", "Category", "Description")
        library_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        library_tree.heading("Name", text="Item Name")
        library_tree.heading("Category", text="Category")
        library_tree.heading("Description", text="Description")
        
        library_tree.column("Name", width=200)
        library_tree.column("Category", width=100)
        library_tree.column("Description", width=250)
        
        lib_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=library_tree.yview)
        library_tree.configure(yscrollcommand=lib_scroll.set)
        
        library_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lib_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load library items
        def load_library_items():
            for item in library_tree.get_children():
                library_tree.delete(item)
            
            search_term = search_var.get().lower()
            category_filter = filter_var.get()
            
            for item in ITEM_LIBRARY:
                # Apply filters
                if search_term and search_term not in item['name'].lower():
                    continue
                
                if category_filter != "All" and item['category'] != category_filter:
                    continue
                
                library_tree.insert("", tk.END, values=(
                    item['name'], item['category'], item['description']
                ))
        
        # Bind search events
        search_var.trace('w', lambda *args: load_library_items())
        filter_var.trace('w', lambda *args: load_library_items())
        
        # Initial load
        load_library_items()
        
        # Buttons
        button_frame = ttk.Frame(library_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def select_item():
            selection = library_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an item")
                return
            
            item_data = library_tree.item(selection[0])
            item_name = item_data['values'][0]
            
            # Find full item data
            selected_item = None
            for item in ITEM_LIBRARY:
                if item['name'] == item_name:
                    selected_item = item
                    break
            
            if selected_item:
                # Fill form with selected item
                self.name_var.set(selected_item['name'])
                self.desc_var.set(selected_item['description'])
                self.category_var.set(selected_item['category'])
                self.price_var.set(str(selected_item.get('default_price', 100)))
                
                self.command_entry.delete(1.0, tk.END)
                self.command_entry.insert(tk.END, selected_item['command'])
                
                library_dialog.destroy()
        
        select_btn = ttk.Button(button_frame, text="Select Item", command=select_item)
        select_btn.pack(side=tk.LEFT)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=library_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT)
    
    def on_item_select(self, event):
        """Handle item selection in tree"""
        selection = self.items_tree.selection()
        if not selection:
            return
        
        # This could show additional item details or preview
        pass
