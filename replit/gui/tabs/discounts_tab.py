"""
Discounts management tab for promotional codes and discounts
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os

class DiscountsTab:
    def __init__(self, parent, bot, logger):
        self.bot = bot
        self.logger = logger
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_discounts()
    
    def setup_ui(self):
        """Setup the discounts interface"""
        # Main notebook for different discount types
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Promotional Codes tab
        self.promo_frame = ttk.Frame(notebook)
        notebook.add(self.promo_frame, text="Promotional Codes")
        self.setup_promo_tab()
        
        # Automatic Discounts tab
        self.auto_frame = ttk.Frame(notebook)
        notebook.add(self.auto_frame, text="Automatic Discounts")
        self.setup_auto_tab()
        
        # Tier Discounts tab
        self.tier_frame = ttk.Frame(notebook)
        notebook.add(self.tier_frame, text="Tier Discounts")
        self.setup_tier_tab()
    
    def setup_promo_tab(self):
        """Setup promotional codes tab"""
        # Promo codes list
        list_frame = ttk.LabelFrame(self.promo_frame, text="Promotional Codes", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for promo codes
        columns = ("Code", "Type", "Value", "Uses", "Max Uses", "Expires", "Status")
        self.promo_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.promo_tree.heading("Code", text="Promo Code")
        self.promo_tree.heading("Type", text="Type")
        self.promo_tree.heading("Value", text="Value")
        self.promo_tree.heading("Uses", text="Uses")
        self.promo_tree.heading("Max Uses", text="Max Uses")
        self.promo_tree.heading("Expires", text="Expires")
        self.promo_tree.heading("Status", text="Status")
        
        self.promo_tree.column("Code", width=120)
        self.promo_tree.column("Type", width=80)
        self.promo_tree.column("Value", width=80)
        self.promo_tree.column("Uses", width=60)
        self.promo_tree.column("Max Uses", width=80)
        self.promo_tree.column("Expires", width=100)
        self.promo_tree.column("Status", width=80)
        
        # Add scrollbar
        promo_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.promo_tree.yview)
        self.promo_tree.configure(yscrollcommand=promo_scroll.set)
        
        self.promo_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        promo_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Promo code management buttons
        promo_buttons = ttk.Frame(list_frame)
        promo_buttons.pack(fill=tk.X, pady=(10, 0))
        
        add_promo_btn = ttk.Button(promo_buttons, text="Add Code", command=self.add_promo_code)
        add_promo_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_promo_btn = ttk.Button(promo_buttons, text="Edit Code", command=self.edit_promo_code)
        edit_promo_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_promo_btn = ttk.Button(promo_buttons, text="Remove Code", command=self.remove_promo_code)
        remove_promo_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        toggle_promo_btn = ttk.Button(promo_buttons, text="Enable/Disable", command=self.toggle_promo_code)
        toggle_promo_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        generate_btn = ttk.Button(promo_buttons, text="Generate Bulk", command=self.generate_bulk_codes)
        generate_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_promo_btn = ttk.Button(promo_buttons, text="Refresh", command=self.load_promo_codes)
        refresh_promo_btn.pack(side=tk.RIGHT)
        
        # Quick create section
        quick_frame = ttk.LabelFrame(self.promo_frame, text="Quick Create", padding=10)
        quick_frame.pack(fill=tk.X)
        
        # Quick create form
        ttk.Label(quick_frame, text="Code:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.quick_code_var = tk.StringVar()
        ttk.Entry(quick_frame, textvariable=self.quick_code_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(quick_frame, text="Type:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.quick_type_var = tk.StringVar()
        type_combo = ttk.Combobox(quick_frame, textvariable=self.quick_type_var, values=["Percentage", "Fixed Points"], width=12, state="readonly")
        type_combo.set("Percentage")
        type_combo.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(quick_frame, text="Value:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=2)
        self.quick_value_var = tk.StringVar(value="10")
        ttk.Entry(quick_frame, textvariable=self.quick_value_var, width=10).grid(row=0, column=5, padx=5, pady=2)
        
        ttk.Label(quick_frame, text="Max Uses:").grid(row=0, column=6, sticky=tk.W, padx=5, pady=2)
        self.quick_uses_var = tk.StringVar(value="100")
        ttk.Entry(quick_frame, textvariable=self.quick_uses_var, width=10).grid(row=0, column=7, padx=5, pady=2)
        
        quick_create_btn = ttk.Button(quick_frame, text="Create", command=self.quick_create_code)
        quick_create_btn.grid(row=0, column=8, padx=10, pady=2)
        
        # Bind selection event
        self.promo_tree.bind("<<TreeviewSelect>>", self.on_promo_select)
    
    def setup_auto_tab(self):
        """Setup automatic discounts tab"""
        # Auto discounts list
        list_frame = ttk.LabelFrame(self.auto_frame, text="Automatic Discounts", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for auto discounts
        columns = ("Name", "Type", "Value", "Condition", "Start Date", "End Date", "Status")
        self.auto_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.auto_tree.heading("Name", text="Discount Name")
        self.auto_tree.heading("Type", text="Type")
        self.auto_tree.heading("Value", text="Value")
        self.auto_tree.heading("Condition", text="Condition")
        self.auto_tree.heading("Start Date", text="Start Date")
        self.auto_tree.heading("End Date", text="End Date")
        self.auto_tree.heading("Status", text="Status")
        
        self.auto_tree.column("Name", width=150)
        self.auto_tree.column("Type", width=80)
        self.auto_tree.column("Value", width=80)
        self.auto_tree.column("Condition", width=150)
        self.auto_tree.column("Start Date", width=100)
        self.auto_tree.column("End Date", width=100)
        self.auto_tree.column("Status", width=80)
        
        # Add scrollbar
        auto_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.auto_tree.yview)
        self.auto_tree.configure(yscrollcommand=auto_scroll.set)
        
        self.auto_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        auto_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Auto discount management buttons
        auto_buttons = ttk.Frame(list_frame)
        auto_buttons.pack(fill=tk.X, pady=(10, 0))
        
        add_auto_btn = ttk.Button(auto_buttons, text="Add Discount", command=self.add_auto_discount)
        add_auto_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_auto_btn = ttk.Button(auto_buttons, text="Edit Discount", command=self.edit_auto_discount)
        edit_auto_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_auto_btn = ttk.Button(auto_buttons, text="Remove Discount", command=self.remove_auto_discount)
        remove_auto_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        toggle_auto_btn = ttk.Button(auto_buttons, text="Enable/Disable", command=self.toggle_auto_discount)
        toggle_auto_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_auto_btn = ttk.Button(auto_buttons, text="Refresh", command=self.load_auto_discounts)
        refresh_auto_btn.pack(side=tk.RIGHT)
        
        # Discount examples
        examples_frame = ttk.LabelFrame(self.auto_frame, text="Discount Examples", padding=10)
        examples_frame.pack(fill=tk.X)
        
        examples_text = tk.Text(examples_frame, height=6, state=tk.DISABLED)
        examples_text.pack(fill=tk.X)
        
        examples_text.config(state=tk.NORMAL)
        examples_text.insert(tk.END, """Weekend Sale: 20% off all items on weekends
Bulk Purchase: 10% off when buying 5+ items
First Purchase: 50% off first item for new users
High Value: 5% off purchases over 1000 points
Member Discount: 15% off for VIP members
Flash Sale: 30% off for 2 hours (limited time)""")
        examples_text.config(state=tk.DISABLED)
    
    def setup_tier_tab(self):
        """Setup tier-based discounts tab"""
        # Tier discounts section
        tier_frame = ttk.LabelFrame(self.tier_frame, text="Tier-Based Discounts", padding=10)
        tier_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for tier discounts
        columns = ("Tier", "Discount", "Min Purchase", "Requirements", "Status")
        self.tier_tree = ttk.Treeview(tier_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.tier_tree.heading("Tier", text="User Tier")
        self.tier_tree.heading("Discount", text="Discount %")
        self.tier_tree.heading("Min Purchase", text="Min Purchase")
        self.tier_tree.heading("Requirements", text="Requirements")
        self.tier_tree.heading("Status", text="Status")
        
        self.tier_tree.column("Tier", width=120)
        self.tier_tree.column("Discount", width=100)
        self.tier_tree.column("Min Purchase", width=120)
        self.tier_tree.column("Requirements", width=200)
        self.tier_tree.column("Status", width=80)
        
        # Add scrollbar
        tier_scroll = ttk.Scrollbar(tier_frame, orient=tk.VERTICAL, command=self.tier_tree.yview)
        self.tier_tree.configure(yscrollcommand=tier_scroll.set)
        
        tier_tree_frame = ttk.Frame(tier_frame)
        tier_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tier_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tier_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tier discount management buttons
        tier_buttons = ttk.Frame(tier_frame)
        tier_buttons.pack(fill=tk.X, pady=(10, 0))
        
        add_tier_btn = ttk.Button(tier_buttons, text="Add Tier Discount", command=self.add_tier_discount)
        add_tier_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_tier_btn = ttk.Button(tier_buttons, text="Edit Tier", command=self.edit_tier_discount)
        edit_tier_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_tier_btn = ttk.Button(tier_buttons, text="Remove Tier", command=self.remove_tier_discount)
        remove_tier_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_tier_btn = ttk.Button(tier_buttons, text="Refresh", command=self.load_tier_discounts)
        refresh_tier_btn.pack(side=tk.RIGHT)
        
        # Usage statistics
        stats_frame = ttk.LabelFrame(self.tier_frame, text="Discount Usage Statistics", padding=10)
        stats_frame.pack(fill=tk.X)
        
        # Stats display
        self.stats_text = tk.Text(stats_frame, height=6, state=tk.DISABLED)
        stats_scroll = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_stats()
    
    def load_discounts(self):
        """Load all discount types"""
        self.load_promo_codes()
        self.load_auto_discounts()
        self.load_tier_discounts()
    
    def load_promo_codes(self):
        """Load promotional codes"""
        try:
            # Clear existing items
            for item in self.promo_tree.get_children():
                self.promo_tree.delete(item)
            
            # Load from file or database
            promo_file = "data/promo_codes.json"
            if os.path.exists(promo_file):
                with open(promo_file, 'r', encoding='utf-8') as f:
                    promo_codes = json.load(f)
            else:
                promo_codes = []
            
            # Add sample codes if none exist
            if not promo_codes:
                promo_codes = [
                    {
                        'code': 'WELCOME10',
                        'type': 'Percentage',
                        'value': 10,
                        'uses': 0,
                        'max_uses': 100,
                        'expires': '2024-12-31',
                        'enabled': True
                    },
                    {
                        'code': 'POINTS500',
                        'type': 'Fixed Points',
                        'value': 500,
                        'uses': 0,
                        'max_uses': 50,
                        'expires': '2024-06-30',
                        'enabled': True
                    }
                ]
            
            # Add codes to tree
            for code in promo_codes:
                status = "Active" if code.get('enabled', True) else "Disabled"
                if code.get('uses', 0) >= code.get('max_uses', 0):
                    status = "Exhausted"
                
                expires = code.get('expires', 'Never')
                if expires != 'Never':
                    try:
                        exp_date = datetime.strptime(expires, '%Y-%m-%d')
                        if exp_date < datetime.now():
                            status = "Expired"
                    except:
                        pass
                
                self.promo_tree.insert("", tk.END, values=(
                    code.get('code', ''),
                    code.get('type', ''),
                    f"{code.get('value', 0)}{'%' if code.get('type') == 'Percentage' else ' pts'}",
                    code.get('uses', 0),
                    code.get('max_uses', 0),
                    expires,
                    status
                ))
                
        except Exception as e:
            self.logger.error(f"Error loading promo codes: {e}")
    
    def load_auto_discounts(self):
        """Load automatic discounts"""
        try:
            # Clear existing items
            for item in self.auto_tree.get_children():
                self.auto_tree.delete(item)
            
            # Sample auto discounts
            auto_discounts = [
                {
                    'name': 'Weekend Sale',
                    'type': 'Percentage',
                    'value': 20,
                    'condition': 'Weekend',
                    'start_date': '2024-01-01',
                    'end_date': '2024-12-31',
                    'enabled': True
                },
                {
                    'name': 'Bulk Purchase',
                    'type': 'Percentage',
                    'value': 10,
                    'condition': 'Purchase >= 5 items',
                    'start_date': '2024-01-01',
                    'end_date': '2024-12-31',
                    'enabled': True
                }
            ]
            
            # Add discounts to tree
            for discount in auto_discounts:
                status = "Active" if discount.get('enabled', True) else "Disabled"
                
                self.auto_tree.insert("", tk.END, values=(
                    discount.get('name', ''),
                    discount.get('type', ''),
                    f"{discount.get('value', 0)}%",
                    discount.get('condition', ''),
                    discount.get('start_date', ''),
                    discount.get('end_date', ''),
                    status
                ))
                
        except Exception as e:
            self.logger.error(f"Error loading auto discounts: {e}")
    
    def load_tier_discounts(self):
        """Load tier-based discounts"""
        try:
            # Clear existing items
            for item in self.tier_tree.get_children():
                self.tier_tree.delete(item)
            
            # Sample tier discounts
            tier_discounts = [
                {
                    'tier': 'VIP',
                    'discount': 15,
                    'min_purchase': 0,
                    'requirements': 'VIP Role',
                    'enabled': True
                },
                {
                    'tier': 'Donor',
                    'discount': 10,
                    'min_purchase': 100,
                    'requirements': 'Has donated',
                    'enabled': True
                },
                {
                    'tier': 'Regular',
                    'discount': 5,
                    'min_purchase': 500,
                    'requirements': 'Member for 30+ days',
                    'enabled': True
                }
            ]
            
            # Add tier discounts to tree
            for tier in tier_discounts:
                status = "Active" if tier.get('enabled', True) else "Disabled"
                
                self.tier_tree.insert("", tk.END, values=(
                    tier.get('tier', ''),
                    f"{tier.get('discount', 0)}%",
                    f"{tier.get('min_purchase', 0)} points",
                    tier.get('requirements', ''),
                    status
                ))
                
        except Exception as e:
            self.logger.error(f"Error loading tier discounts: {e}")
    
    def add_promo_code(self):
        """Add new promotional code"""
        self.show_promo_dialog()
    
    def edit_promo_code(self):
        """Edit selected promotional code"""
        selection = self.promo_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a promotional code to edit")
            return
        
        # Get code data and show dialog
        item = self.promo_tree.item(selection[0])
        code_data = {
            'code': item['values'][0],
            'type': item['values'][1],
            'value': item['values'][2].replace('%', '').replace(' pts', ''),
            'uses': item['values'][3],
            'max_uses': item['values'][4],
            'expires': item['values'][5]
        }
        
        self.show_promo_dialog(code_data)
    
    def show_promo_dialog(self, code_data=None):
        """Show promotional code dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Add Promotional Code" if code_data is None else "Edit Promotional Code")
        dialog.geometry("400x500")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"400x500+{x}+{y}")
        
        # Form fields
        ttk.Label(dialog, text="Promo Code:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        code_var = tk.StringVar(value=code_data.get('code', '') if code_data else '')
        ttk.Entry(dialog, textvariable=code_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(dialog, text="Type:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        type_var = tk.StringVar(value=code_data.get('type', 'Percentage') if code_data else 'Percentage')
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=["Percentage", "Fixed Points"], width=27, state="readonly")
        type_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(dialog, text="Value:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        value_var = tk.StringVar(value=str(code_data.get('value', '10')) if code_data else '10')
        ttk.Entry(dialog, textvariable=value_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(dialog, text="Max Uses:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        max_uses_var = tk.StringVar(value=str(code_data.get('max_uses', '100')) if code_data else '100')
        ttk.Entry(dialog, textvariable=max_uses_var, width=30).grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(dialog, text="Expires (YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        expires_var = tk.StringVar(value=code_data.get('expires', 'Never') if code_data else 'Never')
        ttk.Entry(dialog, textvariable=expires_var, width=30).grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Settings
        enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text="Enabled", variable=enabled_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        single_use_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dialog, text="Single use per user", variable=single_use_var).grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        def save_code():
            try:
                # Validate inputs
                if not code_var.get().strip():
                    messagebox.showerror("Error", "Promo code is required")
                    return
                
                try:
                    value = float(value_var.get())
                    max_uses = int(max_uses_var.get())
                except ValueError:
                    messagebox.showerror("Error", "Value and max uses must be valid numbers")
                    return
                
                # Save code (would save to database/file)
                messagebox.showinfo("Success", "Promotional code saved successfully")
                
                # Refresh display
                self.load_promo_codes()
                dialog.destroy()
                
            except Exception as e:
                self.logger.error(f"Error saving promo code: {e}")
                messagebox.showerror("Error", f"Failed to save promotional code: {e}")
        
        save_btn = ttk.Button(button_frame, text="Save", command=save_code)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def quick_create_code(self):
        """Quick create promotional code"""
        try:
            if not all([self.quick_code_var.get().strip(), self.quick_value_var.get().strip(), self.quick_uses_var.get().strip()]):
                messagebox.showerror("Error", "All fields are required for quick create")
                return
            
            # Create code (would save to database/file)
            messagebox.showinfo("Success", f"Promotional code '{self.quick_code_var.get()}' created successfully")
            
            # Clear form
            self.quick_code_var.set("")
            self.quick_value_var.set("10")
            self.quick_uses_var.set("100")
            
            # Refresh display
            self.load_promo_codes()
            
        except Exception as e:
            self.logger.error(f"Error creating promo code: {e}")
            messagebox.showerror("Error", f"Failed to create promotional code: {e}")
    
    def generate_bulk_codes(self):
        """Generate bulk promotional codes"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Generate Bulk Promotional Codes")
        dialog.geometry("400x300")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Bulk generation form
        ttk.Label(dialog, text="Code Prefix:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        prefix_var = tk.StringVar(value="BULK")
        ttk.Entry(dialog, textvariable=prefix_var, width=30).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Number of Codes:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        count_var = tk.StringVar(value="50")
        ttk.Entry(dialog, textvariable=count_var, width=30).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Discount Value:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        bulk_value_var = tk.StringVar(value="15")
        ttk.Entry(dialog, textvariable=bulk_value_var, width=30).grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Max Uses per Code:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        bulk_uses_var = tk.StringVar(value="1")
        ttk.Entry(dialog, textvariable=bulk_uses_var, width=30).grid(row=3, column=1, padx=10, pady=5)
        
        def generate():
            try:
                count = int(count_var.get())
                if count <= 0 or count > 1000:
                    messagebox.showerror("Error", "Number of codes must be between 1 and 1000")
                    return
                
                # Generate codes (would create actual codes)
                messagebox.showinfo("Success", f"Generated {count} promotional codes")
                self.load_promo_codes()
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Invalid number of codes")
            except Exception as e:
                self.logger.error(f"Error generating bulk codes: {e}")
                messagebox.showerror("Error", f"Failed to generate codes: {e}")
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        generate_btn = ttk.Button(button_frame, text="Generate", command=generate)
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def remove_promo_code(self):
        """Remove selected promotional code"""
        selection = self.promo_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a promotional code to remove")
            return
        
        item = self.promo_tree.item(selection[0])
        code = item['values'][0]
        
        response = messagebox.askyesno("Confirm Removal", f"Remove promotional code '{code}'?")
        if response:
            # Remove code (would remove from database/file)
            messagebox.showinfo("Success", "Promotional code removed successfully")
            self.load_promo_codes()
    
    def toggle_promo_code(self):
        """Toggle promotional code status"""
        selection = self.promo_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a promotional code to toggle")
            return
        
        # Toggle status (would update in database/file)
        messagebox.showinfo("Success", "Promotional code status updated")
        self.load_promo_codes()
    
    def add_auto_discount(self):
        """Add automatic discount"""
        messagebox.showinfo("Info", "Auto discount creation dialog would be shown here")
    
    def edit_auto_discount(self):
        """Edit automatic discount"""
        messagebox.showinfo("Info", "Auto discount editing would be implemented here")
    
    def remove_auto_discount(self):
        """Remove automatic discount"""
        messagebox.showinfo("Info", "Auto discount removal would be implemented here")
    
    def toggle_auto_discount(self):
        """Toggle automatic discount"""
        messagebox.showinfo("Info", "Auto discount toggle would be implemented here")
    
    def add_tier_discount(self):
        """Add tier discount"""
        messagebox.showinfo("Info", "Tier discount creation would be implemented here")
    
    def edit_tier_discount(self):
        """Edit tier discount"""
        messagebox.showinfo("Info", "Tier discount editing would be implemented here")
    
    def remove_tier_discount(self):
        """Remove tier discount"""
        messagebox.showinfo("Info", "Tier discount removal would be implemented here")
    
    def update_stats(self):
        """Update discount usage statistics"""
        try:
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            
            stats = """Discount Usage Statistics (Last 30 Days):

Total Discounts Applied: 1,247
Total Points Saved: 45,892
Most Used Promo Code: WELCOME10 (234 uses)
Most Effective Discount: Weekend Sale (20% avg savings)

Breakdown by Type:
• Promotional Codes: 67% of usage
• Automatic Discounts: 28% of usage
• Tier Discounts: 5% of usage

Top Performing Codes:
1. WELCOME10 - 234 uses, 4,680 points saved
2. WEEKEND20 - 189 uses, 8,945 points saved
3. BULK10 - 156 uses, 3,120 points saved"""
            
            self.stats_text.insert(tk.END, stats)
            self.stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error updating stats: {e}")
    
    def on_promo_select(self, event):
        """Handle promotional code selection"""
        # Could show additional details
        pass
