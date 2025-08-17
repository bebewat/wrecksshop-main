"""
Item Library tab for browsing and managing Ark items
"""

import tkinter as tk
from tkinter import ttk, messagebox
from data.item_library import ITEM_LIBRARY
import json
import os

class LibraryTab:
    def __init__(self, parent, logger):
        self.logger = logger
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_library()
    
    def setup_ui(self):
        """Setup the library interface"""
        # Main paned window
        paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Library browser
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=2)
        
        # Search and filter section
        search_frame = ttk.LabelFrame(left_frame, text="Search & Filter", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search bar
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        search_entry.bind('<KeyRelease>', self.on_search)
        
        # Category filter
        ttk.Label(search_frame, text="Category:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5), pady=2)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var, width=15, state="readonly")
        self.category_combo.grid(row=0, column=3, sticky=tk.W, pady=2)
        self.category_combo.bind('<<ComboboxSelected>>', self.on_filter)
        
        # Sort options
        ttk.Label(search_frame, text="Sort by:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.sort_var = tk.StringVar()
        sort_combo = ttk.Combobox(search_frame, textvariable=self.sort_var, 
                                 values=["Name", "Category", "Default Price"], width=15, state="readonly")
        sort_combo.set("Name")
        sort_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        sort_combo.bind('<<ComboboxSelected>>', self.on_sort)
        
        # Clear button
        clear_btn = ttk.Button(search_frame, text="Clear Filters", command=self.clear_filters)
        clear_btn.grid(row=1, column=3, sticky=tk.E, pady=2)
        
        # Library items section
        items_frame = ttk.LabelFrame(left_frame, text="Item Library", padding=10)
        items_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for library items
        columns = ("Name", "Category", "Price", "Description")
        self.library_tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.library_tree.heading("Name", text="Item Name")
        self.library_tree.heading("Category", text="Category")
        self.library_tree.heading("Price", text="Default Price")
        self.library_tree.heading("Description", text="Description")
        
        self.library_tree.column("Name", width=200)
        self.library_tree.column("Category", width=120)
        self.library_tree.column("Price", width=100)
        self.library_tree.column("Description", width=300)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.library_tree.yview)
        self.library_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.library_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right panel - Item details
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        # Item details section
        details_frame = ttk.LabelFrame(right_frame, text="Item Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Item name
        self.item_name_label = ttk.Label(details_frame, text="Select an item to view details", 
                                        font=("TkDefaultFont", 12, "bold"))
        self.item_name_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Details text
        self.details_text = tk.Text(details_frame, wrap=tk.WORD, height=20, state=tk.DISABLED)
        details_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Library management section
        management_frame = ttk.LabelFrame(right_frame, text="Library Management", padding=10)
        management_frame.pack(fill=tk.X)
        
        # Management buttons
        add_custom_btn = ttk.Button(management_frame, text="Add Custom Item", command=self.add_custom_item)
        add_custom_btn.pack(fill=tk.X, pady=2)
        
        edit_btn = ttk.Button(management_frame, text="Edit Selected", command=self.edit_item)
        edit_btn.pack(fill=tk.X, pady=2)
        
        remove_btn = ttk.Button(management_frame, text="Remove Custom", command=self.remove_custom_item)
        remove_btn.pack(fill=tk.X, pady=2)
        
        export_btn = ttk.Button(management_frame, text="Export Library", command=self.export_library)
        export_btn.pack(fill=tk.X, pady=2)
        
        import_btn = ttk.Button(management_frame, text="Import Items", command=self.import_items)
        import_btn.pack(fill=tk.X, pady=2)
        
        refresh_btn = ttk.Button(management_frame, text="Refresh Library", command=self.load_library)
        refresh_btn.pack(fill=tk.X, pady=2)
        
        # Bind selection event
        self.library_tree.bind("<<TreeviewSelect>>", self.on_item_select)
        
        # Store current library data
        self.current_library = []
        self.filtered_library = []
    
    def load_library(self):
        """Load item library"""
        try:
            self.current_library = list(ITEM_LIBRARY)
            
            # Load custom items if they exist
            custom_file = "data/custom_items.json"
            if os.path.exists(custom_file):
                with open(custom_file, 'r', encoding='utf-8') as f:
                    custom_items = json.load(f)
                    self.current_library.extend(custom_items)
            
            # Get unique categories
            categories = sorted(set(item['category'] for item in self.current_library))
            self.category_combo['values'] = ["All"] + categories
            self.category_combo.set("All")
            
            # Apply current filters
            self.apply_filters()
            
        except Exception as e:
            self.logger.error(f"Error loading library: {e}")
            messagebox.showerror("Error", f"Failed to load library: {e}")
    
    def apply_filters(self):
        """Apply current search and filter settings"""
        try:
            search_term = self.search_var.get().lower()
            category_filter = self.category_var.get()
            sort_by = self.sort_var.get()
            
            # Filter items
            filtered_items = []
            for item in self.current_library:
                # Apply search filter
                if search_term and search_term not in item['name'].lower():
                    continue
                
                # Apply category filter
                if category_filter and category_filter != "All" and item['category'] != category_filter:
                    continue
                
                filtered_items.append(item)
            
            # Sort items
            if sort_by == "Name":
                filtered_items.sort(key=lambda x: x['name'])
            elif sort_by == "Category":
                filtered_items.sort(key=lambda x: (x['category'], x['name']))
            elif sort_by == "Default Price":
                filtered_items.sort(key=lambda x: x.get('default_price', 0))
            
            self.filtered_library = filtered_items
            self.update_tree()
            
        except Exception as e:
            self.logger.error(f"Error applying filters: {e}")
    
    def update_tree(self):
        """Update the tree view with filtered items"""
        try:
            # Clear existing items
            for item in self.library_tree.get_children():
                self.library_tree.delete(item)
            
            # Add filtered items
            for item in self.filtered_library:
                self.library_tree.insert("", tk.END, values=(
                    item['name'],
                    item['category'],
                    item.get('default_price', 'N/A'),
                    item.get('description', '')[:50] + "..." if len(item.get('description', '')) > 50 else item.get('description', '')
                ))
                
        except Exception as e:
            self.logger.error(f"Error updating tree: {e}")
    
    def on_search(self, event):
        """Handle search input"""
        self.apply_filters()
    
    def on_filter(self, event):
        """Handle category filter change"""
        self.apply_filters()
    
    def on_sort(self, event):
        """Handle sort change"""
        self.apply_filters()
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_var.set("")
        self.category_var.set("All")
        self.sort_var.set("Name")
        self.apply_filters()
    
    def on_item_select(self, event):
        """Handle item selection"""
        selection = self.library_tree.selection()
        if not selection:
            return
        
        try:
            item_data = self.library_tree.item(selection[0])
            item_name = item_data['values'][0]
            
            # Find full item data
            selected_item = None
            for item in self.filtered_library:
                if item['name'] == item_name:
                    selected_item = item
                    break
            
            if selected_item:
                self.show_item_details(selected_item)
                
        except Exception as e:
            self.logger.error(f"Error selecting item: {e}")
    
    def show_item_details(self, item):
        """Show detailed information about selected item"""
        try:
            # Update item name label
            self.item_name_label.config(text=item['name'])
            
            # Build details text
            details = f"""Category: {item['category']}

Description:
{item.get('description', 'No description available')}

Default Price: {item.get('default_price', 'Not set')} points

Ark Command:
{item['command']}

Blueprint Path:
{item.get('blueprint_path', 'Not available')}

Item ID: {item.get('item_id', 'Not available')}

Quality: {item.get('quality', 'Normal')}

Stackable: {'Yes' if item.get('stackable', True) else 'No'}

Custom Item: {'Yes' if item.get('custom', False) else 'No'}

Notes:
{item.get('notes', 'No additional notes')}
"""
            
            # Update details text
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, details)
            self.details_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error showing item details: {e}")
    
    def add_custom_item(self):
        """Add a new custom item to the library"""
        self.show_item_editor()
    
    def edit_item(self):
        """Edit selected item"""
        selection = self.library_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item_data = self.library_tree.item(selection[0])
        item_name = item_data['values'][0]
        
        # Find item in library
        selected_item = None
        for item in self.filtered_library:
            if item['name'] == item_name:
                selected_item = item
                break
        
        if selected_item and not selected_item.get('custom', False):
            messagebox.showwarning("Warning", "Cannot edit built-in items. You can only edit custom items.")
            return
        
        if selected_item:
            self.show_item_editor(selected_item)
    
    def show_item_editor(self, item_data=None):
        """Show item editor dialog"""
        editor = tk.Toplevel(self.frame)
        editor.title("Add Custom Item" if item_data is None else "Edit Custom Item")
        editor.geometry("600x700")
        editor.transient(self.frame)
        editor.grab_set()
        
        # Center the dialog
        editor.update_idletasks()
        x = (editor.winfo_screenwidth() // 2) - (600 // 2)
        y = (editor.winfo_screenheight() // 2) - (700 // 2)
        editor.geometry(f"600x700+{x}+{y}")
        
        # Create scrollable frame
        canvas = tk.Canvas(editor)
        scrollbar = ttk.Scrollbar(editor, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form fields
        ttk.Label(scrollable_frame, text="Item Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=item_data.get('name', '') if item_data else '')
        ttk.Entry(scrollable_frame, textvariable=name_var, width=50).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(scrollable_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        category_var = tk.StringVar(value=item_data.get('category', '') if item_data else '')
        category_combo = ttk.Combobox(scrollable_frame, textvariable=category_var, width=47)
        category_combo['values'] = ("Weapons", "Armor", "Resources", "Tools", "Consumables", "Structures", "Saddles", "Other")
        category_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(scrollable_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        desc_text = tk.Text(scrollable_frame, width=50, height=4)
        desc_text.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        if item_data:
            desc_text.insert(tk.END, item_data.get('description', ''))
        
        ttk.Label(scrollable_frame, text="Default Price:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        price_var = tk.StringVar(value=str(item_data.get('default_price', 100)) if item_data else '100')
        ttk.Entry(scrollable_frame, textvariable=price_var, width=50).grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(scrollable_frame, text="Ark Command:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        command_text = tk.Text(scrollable_frame, width=50, height=4)
        command_text.grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)
        if item_data:
            command_text.insert(tk.END, item_data.get('command', ''))
        
        ttk.Label(scrollable_frame, text="Blueprint Path:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        blueprint_var = tk.StringVar(value=item_data.get('blueprint_path', '') if item_data else '')
        ttk.Entry(scrollable_frame, textvariable=blueprint_var, width=50).grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(scrollable_frame, text="Item ID:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        item_id_var = tk.StringVar(value=item_data.get('item_id', '') if item_data else '')
        ttk.Entry(scrollable_frame, textvariable=item_id_var, width=50).grid(row=6, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(scrollable_frame, text="Quality:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
        quality_var = tk.StringVar(value=item_data.get('quality', 'Normal') if item_data else 'Normal')
        quality_combo = ttk.Combobox(scrollable_frame, textvariable=quality_var, width=47)
        quality_combo['values'] = ("Primitive", "Ramshackle", "Apprentice", "Journeyman", "Mastercraft", "Ascendant", "Normal")
        quality_combo.grid(row=7, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(scrollable_frame, text="Stackable:").grid(row=8, column=0, sticky=tk.W, padx=10, pady=5)
        stackable_var = tk.BooleanVar(value=item_data.get('stackable', True) if item_data else True)
        ttk.Checkbutton(scrollable_frame, variable=stackable_var).grid(row=8, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(scrollable_frame, text="Notes:").grid(row=9, column=0, sticky=tk.W, padx=10, pady=5)
        notes_text = tk.Text(scrollable_frame, width=50, height=3)
        notes_text.grid(row=9, column=1, sticky=tk.W, padx=10, pady=5)
        if item_data:
            notes_text.insert(tk.END, item_data.get('notes', ''))
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)
        
        def save_item():
            try:
                # Validate inputs
                if not all([name_var.get().strip(), category_var.get().strip()]):
                    messagebox.showerror("Error", "Name and category are required")
                    return
                
                try:
                    price = int(price_var.get())
                except ValueError:
                    messagebox.showerror("Error", "Price must be a valid number")
                    return
                
                command = command_text.get(1.0, tk.END).strip()
                if not command:
                    messagebox.showerror("Error", "Ark command is required")
                    return
                
                # Create item data
                new_item = {
                    'name': name_var.get().strip(),
                    'category': category_var.get().strip(),
                    'description': desc_text.get(1.0, tk.END).strip(),
                    'default_price': price,
                    'command': command,
                    'blueprint_path': blueprint_var.get().strip(),
                    'item_id': item_id_var.get().strip(),
                    'quality': quality_var.get(),
                    'stackable': stackable_var.get(),
                    'notes': notes_text.get(1.0, tk.END).strip(),
                    'custom': True
                }
                
                # Save to custom items file
                custom_file = "data/custom_items.json"
                os.makedirs("data", exist_ok=True)
                
                custom_items = []
                if os.path.exists(custom_file):
                    with open(custom_file, 'r', encoding='utf-8') as f:
                        custom_items = json.load(f)
                
                if item_data:
                    # Update existing item
                    for i, item in enumerate(custom_items):
                        if item.get('name') == item_data.get('name'):
                            custom_items[i] = new_item
                            break
                else:
                    # Add new item
                    # Check for duplicates
                    for item in custom_items:
                        if item.get('name') == new_item['name']:
                            messagebox.showerror("Error", "Item with same name already exists")
                            return
                    
                    custom_items.append(new_item)
                
                # Save file
                with open(custom_file, 'w', encoding='utf-8') as f:
                    json.dump(custom_items, f, indent=2, ensure_ascii=False)
                
                # Refresh library
                self.load_library()
                
                messagebox.showinfo("Success", "Item saved successfully")
                editor.destroy()
                
            except Exception as e:
                self.logger.error(f"Error saving item: {e}")
                messagebox.showerror("Error", f"Failed to save item: {e}")
        
        save_btn = ttk.Button(button_frame, text="Save", command=save_item)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=editor.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def remove_custom_item(self):
        """Remove selected custom item"""
        selection = self.library_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        item_data = self.library_tree.item(selection[0])
        item_name = item_data['values'][0]
        
        # Find item in library
        selected_item = None
        for item in self.filtered_library:
            if item['name'] == item_name:
                selected_item = item
                break
        
        if not selected_item or not selected_item.get('custom', False):
            messagebox.showwarning("Warning", "Can only remove custom items")
            return
        
        response = messagebox.askyesno("Confirm Removal", f"Remove custom item '{item_name}'?")
        if not response:
            return
        
        try:
            # Remove from custom items file
            custom_file = "data/custom_items.json"
            if os.path.exists(custom_file):
                with open(custom_file, 'r', encoding='utf-8') as f:
                    custom_items = json.load(f)
                
                custom_items = [item for item in custom_items if item.get('name') != item_name]
                
                with open(custom_file, 'w', encoding='utf-8') as f:
                    json.dump(custom_items, f, indent=2, ensure_ascii=False)
            
            # Refresh library
            self.load_library()
            
            messagebox.showinfo("Success", "Custom item removed successfully")
            
        except Exception as e:
            self.logger.error(f"Error removing item: {e}")
            messagebox.showerror("Error", f"Failed to remove item: {e}")
    
    def export_library(self):
        """Export library to file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                title="Export Library",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_library, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Library exported to {filename}")
                
        except Exception as e:
            self.logger.error(f"Error exporting library: {e}")
            messagebox.showerror("Error", f"Failed to export library: {e}")
    
    def import_items(self):
        """Import items from file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.askopenfilename(
                title="Import Items",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    imported_items = json.load(f)
                
                # Validate imported items
                if not isinstance(imported_items, list):
                    messagebox.showerror("Error", "Invalid file format. Expected list of items.")
                    return
                
                # Add to custom items
                custom_file = "data/custom_items.json"
                os.makedirs("data", exist_ok=True)
                
                custom_items = []
                if os.path.exists(custom_file):
                    with open(custom_file, 'r', encoding='utf-8') as f:
                        custom_items = json.load(f)
                
                added_count = 0
                for item in imported_items:
                    if isinstance(item, dict) and 'name' in item:
                        # Mark as custom and check for duplicates
                        item['custom'] = True
                        
                        # Check if item already exists
                        exists = any(existing['name'] == item['name'] for existing in custom_items)
                        if not exists:
                            custom_items.append(item)
                            added_count += 1
                
                # Save updated custom items
                with open(custom_file, 'w', encoding='utf-8') as f:
                    json.dump(custom_items, f, indent=2, ensure_ascii=False)
                
                # Refresh library
                self.load_library()
                
                messagebox.showinfo("Success", f"Imported {added_count} new items")
                
        except Exception as e:
            self.logger.error(f"Error importing items: {e}")
            messagebox.showerror("Error", f"Failed to import items: {e}")
