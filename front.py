import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import requests

API = "http://127.0.0.1:5000/items"

class InventoryApp:
    def __init__(self, root):
        self.root = root
        root.title("Reddy Book Inventory")
        root.geometry("950x600")
        # Theme defaults (start dark)
        self.is_dark = True
        self.bg_color = '#222222'  # dark gray (updated per request)
        self.fg_color = '#f8fafc'  # light text
        self.input_bg = '#374151'  # input background
        self.accent_orange = '#f59e0b'
        root.configure(bg=self.bg_color)

        # Styles
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except Exception:
            pass
        self.style.configure('Accent.TButton', background=self.accent_orange, foreground='white', padding=8)
        self.style.configure('Add.TButton', background='#10b981', foreground='white', padding=6)
        self.style.map('Add.TButton', background=[('active', '#059669')])
        self.style.configure('Delete.TButton', background='#ef4444', foreground='white', padding=6)
        self.style.map('Delete.TButton', background=[('active', '#dc2626')])
        self.style.configure('Reset.TButton', background=self.accent_orange, foreground='white', padding=6)
        self.style.map('Reset.TButton', background=[('active', '#d97706')])
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TEntry', fieldbackground=self.input_bg, foreground=self.fg_color, padding=4)
        # Larger tree rows and font for better readability
        self.style.configure('Treeview', rowheight=36, font=('Segoe UI', 11), background='#222222', fieldbackground='#222222', foreground=self.fg_color)
        self.style.configure('Treeview.Heading', font=('Segoe UI', 12, 'bold'), background='#111827', foreground=self.fg_color)

        title_font = tkfont.Font(family='Segoe UI', size=20, weight='bold')
        # larger fonts for inputs and buttons
        self.big_font = tkfont.Font(family='Segoe UI', size=11)
        self.btn_font = tkfont.Font(family='Segoe UI', size=10, weight='bold')
        self.title = tk.Label(self.root, text="📚 Reddy Book Inventory", font=title_font, bg=self.bg_color, fg=self.fg_color)
        self.title.pack(pady=(14, 6))

        # SEARCH BAR
        # slightly larger search area
        self.search_frame = ttk.Frame(self.root, padding=(18, 14, 18, 14))
        self.search_frame.pack(fill=tk.X, padx=18)

        ttk.Label(self.search_frame, text="Search by Name:").pack(side=tk.LEFT)
        # use tk.Entry for reliable fg/bg control in dark mode
        self.search_entry = tk.Entry(self.search_frame, width=42, bg=self.input_bg, fg=self.fg_color, insertbackground=self.fg_color, font=self.big_font)
        self.search_entry.pack(side=tk.LEFT, padx=12, ipady=6)

        ttk.Label(self.search_frame, text="Type:").pack(side=tk.LEFT, padx=(12, 0))
        self.type_filter = ttk.Combobox(self.search_frame, values=["", "book", "magazine", "film"], width=14, font=self.big_font)
        self.type_filter.pack(side=tk.LEFT, padx=(8, 12))
        self.type_filter.set("")
        # larger buttons
        self.search_btn = tk.Button(self.search_frame, text="Search", command=self.load_items, bg=self.accent_orange, fg='white', activebackground='#d97706', relief='flat', font=self.btn_font)
        self.search_btn.pack(side=tk.LEFT, padx=(0,8), ipadx=8, ipady=4)
        self.reset_search_btn = tk.Button(self.search_frame, text="Reset", command=self.reset_filters, bg='#6b7280', fg='white', activebackground='#4b5563', relief='flat', font=self.btn_font)
        self.reset_search_btn.pack(side=tk.LEFT, padx=(0,12), ipadx=8, ipady=4)
        # Theme toggle button (use orange in both modes)
        self.theme_btn = tk.Button(self.search_frame, text="Light Mode", command=self.toggle_theme, bg=self.accent_orange, fg='white', relief='flat', font=self.btn_font)
        self.theme_btn.pack(side=tk.RIGHT, ipadx=8, ipady=4)

        # placeholder behavior for search entry
        self._placeholder_text = 'Enter title or author...'
        def _add_placeholder():
            if not self.search_entry.get():
                self.search_entry.insert(0, self._placeholder_text)
                self.search_entry.config(fg='#94a3b8')

        def _clear_placeholder(event=None):
            if self.search_entry.get() == self._placeholder_text:
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(fg=self.fg_color)

        self.search_entry.bind('<FocusIn>', _clear_placeholder)
        self.search_entry.bind('<FocusOut>', lambda e: _add_placeholder())
        _add_placeholder()

        # TABLE
        columns = ("id", "type", "title", "author", "year")
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=(8, 6))

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        self.tree.column("id", width=60, anchor='center')
        self.tree.column("type", width=100, anchor='center')
        self.tree.column("title", width=320)
        self.tree.column("author", width=220)
        self.tree.column("year", width=80, anchor='center')

        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.vsb.set)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # FORM FRAME
        self.tree.tag_configure('odd', background='#0b1220', foreground=self.fg_color)
        self.tree.tag_configure('even', background='#0f1724', foreground=self.fg_color)

        self.form = ttk.Frame(self.root, padding=(12, 10, 12, 12))
        self.form.pack(fill=tk.X, padx=18, pady=(4, 12))

        ttk.Label(self.form, text="Type:").grid(row=0, column=0, sticky='w', padx=(0,8), pady=4)
        self.type_box = ttk.Combobox(self.form, values=["book", "magazine", "film"], width=18)
        self.type_box.grid(row=0, column=1, sticky='w')
        self.type_box.set("book")

        ttk.Label(self.form, text="Title:").grid(row=1, column=0, sticky='w', padx=(0,8), pady=6)
        self.title_entry = ttk.Entry(self.form, width=48, font=self.big_font)
        self.title_entry.grid(row=1, column=1, sticky='w', pady=6)

        ttk.Label(self.form, text="Author/Director:").grid(row=2, column=0, sticky='w', padx=(0,8), pady=6)
        self.author_entry = ttk.Entry(self.form, width=48, font=self.big_font)
        self.author_entry.grid(row=2, column=1, sticky='w', pady=6)

        ttk.Label(self.form, text="Year:").grid(row=3, column=0, sticky='w', padx=(0,8), pady=6)
        self.year_entry = ttk.Entry(self.form, width=20, font=self.big_font)
        self.year_entry.grid(row=3, column=1, sticky='w', pady=6)

        # Buttons using tk for reliable background/foreground colors
        self.add_btn = tk.Button(self.form, text="Add Item", command=self.add_item, bg='#10b981', fg='white', activebackground='#059669', relief='flat', font=self.btn_font)
        self.add_btn.grid(row=4, column=0, pady=12, ipadx=8, ipady=4)
        self.delete_btn = tk.Button(self.form, text="Delete Selected", command=self.delete_item, bg='#ef4444', fg='white', activebackground='#dc2626', relief='flat', font=self.btn_font)
        self.delete_btn.grid(row=4, column=1, sticky='w', padx=(8,0), ipadx=8, ipady=4)
        self.reset_form_btn = tk.Button(self.form, text="Reset Form", command=self.reset_form, bg=self.accent_orange, fg='white', activebackground='#d97706', relief='flat', font=self.btn_font)
        self.reset_form_btn.grid(row=4, column=2, sticky='w', padx=8, ipadx=8, ipady=4)

        self.load_items()

    def load_items(self):
        params = {}
        q = self.search_entry.get().strip()
        if q:
            params["q"] = q
        # Include type only when user has selected one (optional)
        if hasattr(self, "type_filter") and self.type_filter.get().strip():
            params["type"] = self.type_filter.get().strip()

        res = requests.get(API, params=params)
        data = res.json()

        for i in self.tree.get_children():
            self.tree.delete(i)

        for item in data:
            self.tree.insert("", tk.END, values=(item["id"], item["type"], item["title"], item["author"], item["year"]))

    def reset_filters(self):
        self.search_entry.delete(0, tk.END)
        if hasattr(self, "type_filter"):
            self.type_filter.set("")
        self.load_items()

    def reset_form(self):
        self.type_box.set("book")
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)

    def toggle_theme(self):
        """Toggle between dark and light themes and apply."""
        self.is_dark = not getattr(self, 'is_dark', True)
        # update theme button text
        self.theme_btn.config(text="Light Mode" if self.is_dark else "Dark Mode")
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme colors to widgets."""
        if self.is_dark:
            self.bg_color = '#222222'
            self.fg_color = '#f8fafc'
            self.input_bg = '#374151'
            search_bg = '#f59e0b'
            reset_search_bg = '#6b7280'
            add_bg = '#10b981'
            del_bg = '#ef4444'
            reset_bg = '#f59e0b'
            tree_bg = '#222222'
            tree_head = '#111827'
        else:
            self.bg_color = '#f3f6fb'
            self.fg_color = '#0f172a'
            self.input_bg = '#ffffff'
            search_bg = '#2563eb'
            reset_search_bg = '#6b7280'
            add_bg = '#16a34a'
            del_bg = '#dc2626'
            reset_bg = '#f59e0b'
            tree_bg = '#ffffff'
            tree_head = '#f3f4f6'

        # root and title
        self.root.configure(bg=self.bg_color)
        self.title.config(bg=self.bg_color, fg=self.fg_color)

        # ttk styles
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TEntry', fieldbackground=self.input_bg, foreground=self.fg_color)
        self.style.configure('Treeview', background=tree_bg, fieldbackground=tree_bg, foreground=self.fg_color)
        self.style.configure('Treeview.Heading', background=tree_head, foreground=self.fg_color)

        # entries and combobox
        self.search_entry.config(bg=self.input_bg, fg=self.fg_color, insertbackground=self.fg_color)
        try:
            self.style.configure('TCombobox', fieldbackground=self.input_bg, foreground=self.fg_color)
        except Exception:
            pass

        # buttons
        self.search_btn.config(bg=search_bg, fg='white')
        self.reset_search_btn.config(bg=reset_search_bg, fg='white')
        # keep theme toggle button orange so it remains visible in both modes
        try:
            self.theme_btn.config(bg=self.accent_orange, fg='white', activebackground='#d97706')
        except Exception:
            # fallback if widget not yet available
            pass

        self.add_btn.config(bg=add_bg, fg='white')
        self.delete_btn.config(bg=del_bg, fg='white')
        self.reset_form_btn.config(bg=reset_bg, fg='white')

        # tree rows
        if self.is_dark:
            self.tree.tag_configure('odd', background='#222222', foreground=self.fg_color)
            self.tree.tag_configure('even', background='#1a1a1a', foreground=self.fg_color)
        else:
            self.tree.tag_configure('odd', background='#ffffff', foreground=self.fg_color)
            self.tree.tag_configure('even', background='#f8fafc', foreground=self.fg_color)

    def add_item(self):
        payload = {
            "type": self.type_box.get(),
            "title": self.title_entry.get(),
            "author": self.author_entry.get(),
            "year": int(self.year_entry.get() or 0)
        }
        requests.post(API, json=payload)
        self.load_items()
        messagebox.showinfo("Success", "Item Added")

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an item to delete")
            return
        
        item_id = self.tree.item(selected[0])["values"][0]
        requests.delete(f"{API}/{item_id}")
        self.load_items()
        messagebox.showinfo("Deleted", "Item removed")


root = tk.Tk()
app = InventoryApp(root)
root.mainloop()
