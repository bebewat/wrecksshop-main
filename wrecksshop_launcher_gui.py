import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import Canvas, filedialog, messagebox, simpledialog, ttk
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
from PIL import Image, ImageTk
from arklib_loader import load_ark_lib, ArkItem
from arkdata_updater import update_base_library, update_full_library
import command_builders

# Paths and data files
ENV_PATH = '.env'
SHOP_ITEMS_PATH = 'shop_items.json'
ADMIN_ROLES_PATH = 'admin_roles.json'
DISCOUNTS_PATH = 'discounts.json'
ASSETS_DIR = 'assets'
LOGO_PATH = os.path.join(ASSETS_DIR, 'logo.png')
ICON_PATH = os.path.join(ASSETS_DIR, 'icon.png')
# CSV data library path (robust lookup)
base_dir = Path(__file__).parent
csv_path = base_dir / 'data' / 'CleanArkData.csv'
if not csv_path.is_file():
    csv_path = base_dir / 'CleanArkData.csv'
if not csv_path.is_file():
    tk.Tk().withdraw()
    messagebox.showerror('Error', f'CleanArkData.csv not found at {csv_path}')
    sys.exit(1)
ARK_DATA = load_ark_lib(csv_path)

# Config keys for .env
CONFIG_KEYS = [
    ('DISCORD_TOKEN', 'Discord Bot Token'),
    ('SHOP_CHANNEL', 'Discord Shop Channel'),
    ('SHOP_LOG_CHANNEL_ID', 'Discord Log Channel ID'),
    ('TIP4SERV_SECRET', 'Tip4Serv Secret (optional)'),
    ('TIP4SERV_TOKEN', 'Tip4Serv Token (optional)'),
    ('REWARD_INTERVAL_MINUTES', 'Reward Interval (Minutes)'),
    ('REWARD_POINTS', 'Reward Amount (Points)')
]

def load_modded_library(mods_path: Path):
    """Scan JSON files in mods_path and merge entries on top of base."""
    mod_lib = {'dinos': {}, 'items': {}}
    for f in Path(mods_path).glob('*.json'):
        data = json.load(f.open('r', encoding='utf-8'))
        key = 'dinos' if 'Dino' in f.name else 'items'
        for e in data:
            idn = e.get('name') or e.get('internalName')
            mod_lib[key][idn] = e
    return mod_lib

class WrecksShopLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('WrecksShop Launcher')
        self.geometry('1024x768')
        self.configure(bg='#ffffff')
        # Icon & header
        try:
            self.iconphoto(False, tk.PhotoImage(file=ICON_PATH))
        except:
            pass
        # Load assets
        self._load_assets()
        # Build UI
        self._build_main_menu()
        self._build_notebook()
        # Load data
        self._load_env()
        self.library = update_base_library()
        # Initial loads
        self._load_servers()
        self._load_databases()
        self._refresh_shop_items()
        self._load_admin_roles()
        self._load_discounts()
        self._populate_library_types()
        # Bot process handle
        self.process = None

    def _load_assets(self):
        if os.path.exists(LOGO_PATH):
            img = Image.open(LOGO_PATH).resize((64,64), Image.ANTIALIAS)
            self.logo_img = ImageTk.PhotoImage(img)
        else:
            self.logo_img = None

    def _build_main_menu(self):
        c = Canvas(self, highlightthickness=0)
        c.place(relwidth=1, relheight=1)
        # Gradient
        for i, color in enumerate(['#8F2EFF', '#64C7FF']):
            c.create_rectangle(0, i*384, 1024, (i+1)*384, fill=color, outline='')
        c.create_text(20, 20, anchor='nw', text='WrecksShop', fill='white', font=('Montserrat',24,'bold'))
        if self.logo_img:
            c.create_image(980, 20, anchor='ne', image=self.logo_img)
        labels = ['CONFIG','SERVERS','SQL DATABASES','SHOP','LIBRARY','ADMIN ROLES','DISCOUNTS','CONTROL']
        for idx, lbl in enumerate(labels):
            col = idx % 4
            row = idx // 4
            x = 50 + col*240
            y = 150 + row*250
            btn = ttk.Button(self, text=lbl, command=lambda L=lbl: self._show_tab(L))
            btn.place(x=x, y=y, width=200, height=100)
        bottom = ['START/STOP','LOGS','GITHUB','DISCORD']
        for i, lbl in enumerate(bottom):
            x = 50 + i*240
            btn = ttk.Button(self, text=lbl, command=lambda L=lbl: self._bottom_action(L))
            btn.place(x=x, y=680, width=200, height=60)
        self.menu_canvas = c

    def _build_notebook(self):
        self.nb = ttk.Notebook(self)
        self.pages = {}
        page_names = ['Configuration','RCON Servers','SQL Databases','Shop Items',
                      'Data Library','Admin Roles','Discounts','Control','Logs']
        for name in page_names:
            frame = ttk.Frame(self.nb)
            self.nb.add(frame, text=name)
            self.pages[name] = frame
        self.nb.place_forget()
        # Build pages
        self._build_config_page()
        self._build_servers_page()
        self._build_databases_page()
        self._build_shop_page()
        self._build_library_page()
        self._build_admins_page()
        self._build_discounts_page()
        self._build_control_page()
        self._build_logs_page()

    def _show_tab(self, label):
        self.menu_canvas.place_forget()
        self.nb.place(x=0, y=0, relwidth=1, relheight=1)
        mapping = {'CONFIG':'Configuration','SERVERS':'RCON Servers',
                   'SQL DATABASES':'SQL Databases','SHOP':'Shop Items',
                   'LIBRARY':'Data Library','ADMIN ROLES':'Admin Roles',
                   'DISCOUNTS':'Discounts','CONTROL':'Control','LOGS':'Logs'}
        page = mapping.get(label)
        if page:
            self.nb.select(self.pages[page])

    def _bottom_action(self, label):
        if label == 'START/STOP':
            if self.process: self.stop_bot()
            else: self.start_bot()
        elif label == 'LOGS':
            self._show_tab('Logs')
        elif label == 'GITHUB':
            import webbrowser; webbrowser.open('https://github.com')
        elif label == 'DISCORD':
            import webbrowser; webbrowser.open('https://discord.gg')

    # Configuration Page
    def _build_config_page(self):
        f = self.pages['Configuration']
        self.config_entries = {}
        for i, (k, l) in enumerate(CONFIG_KEYS):
            ttk.Label(f, text=l).grid(row=i, column=0, sticky='w', pady=4)
            e = ttk.Entry(f, width=40)
            e.grid(row=i, column=1, pady=4)
            self.config_entries[k] = e
        ttk.Button(f, text='Save Settings', command=self._save_env).grid(row=len(CONFIG_KEYS), column=0, columnspan=2, pady=10)

    def _load_env(self):
        if os.path.exists(ENV_PATH):
            data = dict(line.strip().split('=',1) for line in open(ENV_PATH) if '=' in line)
            for k, e in self.config_entries.items():
                e.delete(0,'end'); e.insert(0, data.get(k, ''))
            self.servers = json.loads(data.get('RCON_SERVERS','[]'))
            self.databases = json.loads(data.get('SQL_DATABASES','[]'))
            if os.path.exists(SHOP_ITEMS_PATH):
                shop = json.load(open(SHOP_ITEMS_PATH)); self.categories = list(shop.keys())

    def _save_env(self):
        out = {k: e.get() for k, e in self.config_entries.items()}
        out['RCON_SERVERS'] = self.servers; out['SQL_DATABASES'] = self.databases
        with open(ENV_PATH,'w') as f:
            for k, v in out.items():
                f.write(f"{k}={json.dumps(v) if isinstance(v,list) else v}\n")
        messagebox.showinfo('Saved','Configuration saved')
        self._log('Configuration saved')

    # RCON Servers Page
    def _build_servers_page(self):
        f = self.pages['RCON Servers']
        cols = ('Name','Host','Port','Password')
        self.srv_tv = ttk.Treeview(f, columns=cols, show='headings')
        for c in cols: self.srv_tv.heading(c, text=c)
        self.srv_tv.pack(expand=True, fill='both', pady=5)
        btnf = ttk.Frame(f); btnf.pack()
        ttk.Button(btnf, text='Add Server', command=self._add_server).pack(side='left', padx=5)
        ttk.Button(btnf, text='Remove Server', command=self._remove_server).pack(side='left', padx=5)

    def _load_servers(self):
        for s in getattr(self,'servers', []):
            self.srv_tv.insert('', 'end', values=(s['name'], s['host'], s['port'], '*'*len(s['password'])) )

    def _add_server(self):
        name = simpledialog.askstring('Server Name','Enter unique server name:')
        if not name: return
        host = simpledialog.askstring('Host','Enter RCON host/IP:')
        port = simpledialog.askinteger('Port','Enter RCON port:')
        pwd = simpledialog.askstring('Password','Enter RCON password:',show='*')
        srv = {'name':name,'host':host,'port':port,'password':pwd}
        self.servers.append(srv)
        self.srv_tv.insert('', 'end', values=(name,host,port,'*'*len(pwd)))
        self._log(f"Added server {name}")

    def _remove_server(self):
        sel = self.srv_tv.selection()
        if sel:
            idx = self.srv_tv.index(sel)
            name = self.servers.pop(idx)['name']
            self.srv_tv.delete(sel)
            self._log(f"Removed server {name}")

    # SQL Databases Page
    def _build_databases_page(self):
        f = self.pages['SQL Databases']
        cols = ('Name','Host','Port','User','DB')
        self.db_tv = ttk.Treeview(f, columns=cols, show='headings')
        for c in cols: self.db_tv.heading(c,text=c)
        self.db_tv.pack(expand=True, fill='both', pady=5)
        btnf = ttk.Frame(f); btnf.pack()
        ttk.Button(btnf,text='Add Database',command=self._add_database).pack(side='left',padx=5)
        ttk.Button(btnf,text='Remove Database',command=self._remove_database).pack(side='left',padx=5)

    def _load_databases(self):
        for db in getattr(self,'databases',[]):
            self.db_tv.insert('', 'end', values=(db['name'],db['host'],db['port'],db['user'],db['database']))

    def _add_database(self):
        name = simpledialog.askstring('DB Name','Enter unique DB name:')
        if not name: return
        host = simpledialog.askstring('Host','Enter DB host/IP:')
        port = simpledialog.askinteger('Port','Enter DB port:')
        user = simpledialog.askstring('User','Enter DB user:')
        pwd = simpledialog.askstring('Password','Enter DB password:',show='*')
        dbname = simpledialog.askstring('Database','Enter database name:')
        db = {'name':name,'host':host,'port':port,'user':user,'password':pwd,'database':dbname}
        self.databases.append(db)
        self.db_tv.insert('', 'end', values=(name,host,port,user,dbname))
        self._log(f"Added database {name}")

    def _remove_database(self):
        sel = self.db_tv.selection()
        if sel:
            idx = self.db_tv.index(sel)
            name = self.databases.pop(idx)['name']
            self.db_tv.delete(sel)
            self._log(f"Removed database {name}")

    # Shop Items Page
    def _build_shop_page(self):
        f = self.pages['Shop Items']
        ttk.Label(f,text='Category').pack(anchor='w',pady=5)
        self.cat_combo = ttk.Combobox(f, values=self.categories, state='readonly')
        self.cat_combo.pack(fill='x', padx=5)
        self.cat_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_shop_items())
        btnf = ttk.Frame(f); btnf.pack(pady=5)
        ttk.Button(btnf,text='Add Category',command=self._add_category).pack(side='left',padx=5)
        ttk.Button(btnf,text='Toggle Category Enabled',command=self._toggle_category_enabled).pack(side='left',padx=5)
        cols = ('Name','Command','Price','Limit','Roles','Enabled','Description')
        self.item_tv = ttk.Treeview(f,columns=cols,show='headings')
        for c in cols: self.item_tv.heading(c,text=c)
        self.item_tv.pack(expand=True,fill='both',pady=5)
        form = ttk.Frame(f); form.pack(fill='x',pady=5)
        # inputs for Name, Command, Price, Roles, Limit, Description
        labels = ['Name','Command','Price','Roles']
        for i,l in enumerate(labels): ttk.Label(form,text=l).grid(row=0,column=i,padx=4)
        ttk.Label(form,text='Description').grid(row=0,column=5,padx=4)
        self.name_entry = ttk.Entry(form,width=18); self.name_entry.grid(row=1,column=0,padx=4)
        self.command_entry = ttk.Entry(form,width=18); self.command_entry.grid(row=1,column=1,padx=4)
        self.price_entry = ttk.Entry(form,width=8); self.price_entry.grid(row=1,column=2,padx=4)
        self.roles_entry = ttk.Entry(form,width=12); self.roles_entry.grid(row=1,column=3,padx=4)
        self.limit_var=tk.BooleanVar(); ttk.Checkbutton(form,text='Limit',variable=self.limit_var).grid(row=1,column=4,padx=4)
        self.desc_entry = ttk.Entry(form,width=25); self.desc_entry.grid(row=1,column=5,padx=4)
        btnf2 = ttk.Frame(f); btnf2.pack(pady=5)
        ttk.Button(btnf2,text='Add Item',command=self._on_add_item).pack(side='left',padx=5)
        ttk.Button(btnf2,text='Toggle Item Enabled',command=self._toggle_item_enabled).pack(side='left',padx=5)

    def _refresh_shop_items(self):
        self.item_tv.delete(*self.item_tv.get_children())
        if os.path.exists(SHOP_ITEMS_PATH):
            store = json.load(open(SHOP_ITEMS_PATH,'r'))
            for itm in store.get(self.cat_combo.get().strip(),[]):
                roles = 'all' if itm.get('roles')=='all' else ','.join(itm.get('roles',[]))
                enabled = 'Yes' if itm.get('enabled',True) else 'No'
                desc = itm.get('description','')
                self.item_tv.insert('', 'end', values=(itm['name'],itm['command'],itm['price'],itm['limit'],roles,enabled,desc))

    def _add_category(self):
        name = simpledialog.askstring('Category','Enter category name:')
        if name and name not in self.categories:
            self.categories.append(name)
            self.cat_combo['values']=self.categories
            self._log(f"Added category {name}")

    def _toggle_category_enabled(self):
        cat = self.cat_combo.get().strip()
        store=json.load(open(SHOP_ITEMS_PATH,'r'))
        items=store.get(cat,[])
        any_on=any(itm.get('enabled',True) for itm in items)
        for itm in items: itm['enabled']=not any_on
        json.dump(store,open(SHOP_ITEMS_PATH,'w'),indent=2)
        self._refresh_shop_items()
        self._log(f"Category {cat} {'disabled' if any_on else 'enabled'}")

    def _on_add_item(self):
        cat=self.cat_combo.get().strip()
        if not cat: messagebox.showerror('Error','Select a category'); return
        name=self.name_entry.get().strip(); cmd=self.command_entry.get().strip()
        price=self.price_entry.get().strip(); roles=self.roles_entry.get().strip()
        desc=self.desc_entry.get().strip(); limit=self.limit_var.get()
        try: price_val=int(price)
        except: messagebox.showerror('Error','Price must be integer'); return
        roles_val='all' if roles=='all' else [r.strip() for r in roles.split(',')]
        itm={'name':name,'command':cmd,'price':price_val,'limit':limit,'roles':roles_val,'enabled':True,'description':desc}
        store=json.load(open(SHOP_ITEMS_PATH,'r')) if os.path.exists(SHOP_ITEMS_PATH) else {}
        store.setdefault(cat,[]).append(itm)
        json.dump(store,open(SHOP_ITEMS_PATH,'w'),indent=2)
        self._refresh_shop_items(); self._log(f"Added item {name}")

    def _toggle_item_enabled(self):
        sel=self.item_tv.selection();
        if not sel: return
        idx=self.item_tv.index(sel); cat=self.cat_combo.get().strip()
        store=json.load(open(SHOP_ITEMS_PATH,'r'))
        items=store.get(cat,[])
        items[idx]['enabled']=not items[idx].get('enabled',True)
        json.dump(store,open(SHOP_ITEMS_PATH,'w'),indent=2)
        self._refresh_shop_items()
        state='enabled' if items[idx]['enabled'] else 'disabled'
        self._log(f"Item {items[idx]['name']} {state}")

    # Data Library Page
    def _build_library_page(self):
        f=self.pages['Data Library']
        ttk.Label(f,text='Category').pack(anchor='w',pady=5)
        self.lib_type_var=tk.StringVar()
        self.lib_combo=ttk.Combobox(f,textvariable=self.lib_type_var,state='readonly')
        self.lib_combo.pack(fill='x',padx=5)
        self.lib_combo.bind('<<ComboboxSelected>>',lambda e:self._on_type_select())
        btnf=ttk.Frame(f); btnf.pack(pady=5)
        ttk.Button(btnf,text='Refresh Base Data',command=self._refresh_base_library).pack(side='left',padx=5)
        ttk.Button(btnf,text='Import Mods…',command=self._import_mods).pack(side='left',padx=5)
        cols=('Name','Blueprint','Mod')
        self.lib_tv=ttk.Treeview(f,columns=cols,show='headings')
        for c in cols: self.lib_tv.heading(c,text=c)
        self.lib_tv.pack(expand=True,fill='both',pady=5)
        ttk.Button(f,text='Import Selection',command=self._on_lib_import).pack(pady=5)

    def _refresh_base_library(self):
        self.library=update_base_library(); self._populate_library_types(); self._log('Base data refreshed')

    def _import_mods(self):
        d=filedialog.askdirectory(title='Select Mods Folder')
        if not d: return
        self.library=update_full_library(Path(d)); self._populate_library_types(); self._log('Mod data imported')

    def _populate_library_types(self):
        types=sorted(self.library.keys())
        self.lib_combo['values']=types
        if types:
            self.lib_combo.current(0); self._on_type_select()

    def _on_type_select(self):
        sec=self.lib_type_var.get(); self.lib_tv.delete(*self.lib_tv.get_children())
        for name,entry in self.library.get(sec,{}).items():
            bp=entry.get('blueprint',''); mod=entry.get('mod','');
            self.lib_tv.insert('', 'end', values=(name,bp,mod))

    def _on_lib_import(self):
        sel=self.lib_tv.selection();
        if not sel: return
        name,bp,mod=self.lib_tv.item(sel,'values')
        self.name_entry.delete(0,'end'); self.name_entry.insert(0,name)
        try: ark_item=ArkItem(sec=self.lib_type_var.get(),name=name,blueprint=bp,mod=mod)
        except: ark_item=ArkItem(sec='',name=name,blueprint=bp,mod=mod)
        if self.lib_type_var.get().lower().startswith('dino'):
            cmd=command_builders.build_spawn_dino_command(eos_id='{eos}',item=ark_item,level=1,breedable=False)
        else:
            cmd=command_builders.build_giveitem_command(player_id='{player}',item=ark_item,qty=1,quality=1,is_bp=False)
        self.command_entry.delete(0,'end'); self.command_entry.insert(0,cmd)
        self._log(f"Imported {name}")

    # Admin Roles Page
    def _build_admins_page(self):
        f=self.pages['Admin Roles']
        cols=('ID','Name','Desc')
        self.admin_tv=ttk.Treeview(f,columns=cols,show='headings')
        for c in cols: self.admin_tv.heading(c,text=c)
        self.admin_tv.pack(expand=True,fill='both',pady=5)
        bf=ttk.Frame(f); bf.pack()
        ttk.Button(bf,text='Add',command=self._add_admin_role).pack(side='left',padx=5)
        ttk.Button(bf,text='Remove',command=self._remove_admin_role).pack(side='left',padx=5)

    def _load_admin_roles(self):
        self.admin_roles=json.load(open(ADMIN_ROLES_PATH)) if os.path.exists(ADMIN_ROLES_PATH) else []
        self.admin_tv.delete(*self.admin_tv.get_children())
        for r in self.admin_roles: self.admin_tv.insert('', 'end', values=(r['id'],r['name'],r['desc']))

    def _save_admin_roles(self): json.dump(self.admin_roles,open(ADMIN_ROLES_PATH,'w'),indent=2)

    def _add_admin_role(self):
        rid=simpledialog.askstring('Role ID','Discord Role ID:')
        name=simpledialog.askstring('Name','Role name:')
        if rid and name:
            role={'id':rid,'name':name,'desc':name}
            self.admin_roles.append(role); self._save_admin_roles(); self._load_admin_roles(); self._log(f"Added admin {name}")

    def _remove_admin_role(self):
        sel=self.admin_tv.selection();
        if sel:
            idx=self.admin_tv.index(sel); name=self.admin_roles.pop(idx)['name']; self._save_admin_roles(); self._load_admin_roles(); self._log(f"Removed admin {name}")

    # Discounts Page
    def _build_discounts_page(self):
        f=self.pages['Discounts']
        cols=('Name','Type','Target','Amount')
        self.disc_tv=ttk.Treeview(f,columns=cols,show='headings')
        for c in cols: self.disc_tv.heading(c,text=c)
        self.disc_tv.pack(expand=True,fill='both',pady=5)
        bf=ttk.Frame(f); bf.pack()
        ttk.Button(bf,text='Add',command=self._add_discount).pack(side='left',padx=5)
        ttk.Button(bf,text='Remove',command=self._remove_discount).pack(side='left',padx=5)

    def _load_discounts(self):
        self.discounts=json.load(open(DISCOUNTS_PATH)) if os.path.exists(DISCOUNTS_PATH) else []
        self.disc_tv.delete(*self.disc_tv.get_children())
        for d in self.discounts: self.disc_tv.insert('', 'end', values=(d['name'],d['type'],d['target'],d['amount']))

    def _save_discounts(self): json.dump(self.discounts,open(DISCOUNTS_PATH,'w'),indent=2)

    def _add_discount(self):
        name=simpledialog.askstring('Name','Discount name:')
        dtype=simpledialog.askstring('Type','"role" or "event":')
        target=simpledialog.askstring('Target','Role ID or Event name:')
        amt=simpledialog.askfloat('Amount','Percent:')
        if name and dtype and target and amt is not None:
            d={'name':name,'type':dtype,'target':target,'amount':amt}
            self.discounts.append(d); self._save_discounts(); self._load_discounts(); self._log(f"Added discount {name}")

    def _remove_discount(self):
        sel=self.disc_tv.selection();
        if sel:
            idx=self.disc_tv.index(sel); name=self.discounts.pop(idx)['name']; self._save_discounts(); self._load_discounts(); self._log(f"Removed discount {name}")

    # Control Page
    def _build_control_page(self):
        f=self.pages['Control']
        self.status_var=tk.StringVar(value='Stopped')
        sf=ttk.Frame(f); sf.pack(padx=10,pady=10)
        ttk.Label(sf,text='Bot Status:').pack(side='left')
        self.status_lbl=ttk.Label(sf,textvariable=self.status_var,foreground='red'); self.status_lbl.pack(side='left',padx=5)
        btnf=ttk.Frame(f); btnf.pack(pady=10)
        self.start_btn=ttk.Button(btnf,text='Start Bot',command=self.start_bot); self.start_btn.pack(side='left',padx=5)
        self.stop_btn=ttk.Button(btnf,text='Stop Bot',command=self.stop_bot,state='disabled'); self.stop_btn.pack(side='left',padx=5)

    def start_bot(self):
        if self.process: return
        self.process=subprocess.Popen(['python','Discord_Shop_System.py'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        self.start_btn.config(state='disabled'); self.stop_btn.config(state='normal'); self.status_var.set('Running'); self.status_lbl.config(foreground='green')
        self._log('Bot started'); self._read_output()

    def stop_bot(self):
        if not self.process: return
        self.process.terminate(); self.process.wait(5); self.process=None
        self.start_btn.config(state='normal'); self.stop_btn.config(state='disabled'); self.status_var.set('Stopped'); self.status_lbl.config(foreground='red')
        self._log('Bot stopped')

    def _read_output(self):
        if self.process and self.process.poll() is None:
            line=self.process.stdout.readline()
            if line: self._log(line.strip())
            self.after(100,self._read_output)

    # Logs Page
    def _build_logs_page(self):
        f=self.pages['Logs']
        self.log_box=ScrolledText(f,state='disabled',font=('Consolas',10))
        self.log_box.pack(expand=True,fill='both',pady=5)
        ttk.Button(f,text='Save Log',command=self._save_log).pack(pady=5)

    def _log(self,msg):
        self.log_box.config(state='normal'); self.log_box.insert('end',msg+"\n"); self.log_box.config(state='disabled')

    def _save_log(self):
        path=filedialog.asksaveasfilename(defaultextension='.txt')
        if path:
            open(path,'w').write(self.log_box.get('1.0','end'))
            messagebox.showinfo('Saved',f'Log saved to {path}')

if __name__=='__main__':
    app=WrecksShopLauncher(); app.mainloop()
