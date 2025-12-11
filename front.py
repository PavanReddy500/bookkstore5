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
        root.configure(bg="#f3f6fb")

        # Styles
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except Exception:
            pass
        self.style.configure('Accent.TButton', background='#2563eb', foreground='white', padding=6)
        self.style.configure('TFrame', background='#f3f6fb')
        self.style.configure('TLabel', background='#f3f6fb', foreground='#0f172a')
        self.style.configure('TEntry', padding=4)
        self.style.configure('Treeview', rowheight=28, font=('Segoe UI', 10))
        self.style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'))

        title_font = tkfont.Font(family='Segoe UI', size=20, weight='bold')
        title = tk.Label(root, text="📚 Reddy Book Inventory", font=title_font, bg="#f3f6fb", fg="#0f172a")
        title.pack(pady=(14, 6))

        # SEARCH BAR
        search_frame = ttk.Frame(root, padding=(12, 10, 12, 10))
        search_frame.pack(fill=tk.X, padx=18)

        ttk.Label(search_frame, text="Search by Name:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=32)
        self.search_entry.pack(side=tk.LEFT, padx=8)

        ttk.Label(search_frame, text="Type:").pack(side=tk.LEFT, padx=(12, 0))
        self.type_filter = ttk.Combobox(search_frame, values=["", "book", "magazine", "film"], width=12)
        self.type_filter.pack(side=tk.LEFT, padx=(6, 8))
        self.type_filter.set("")

        ttk.Button(search_frame, text="Search", command=self.load_items, style='Accent.TButton').pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Reset", command=self.reset_filters).pack(side=tk.LEFT, padx=8)

        # placeholder behavior for search entry
        self._placeholder_text = 'Enter title or author...'
        def _add_placeholder():
            if not self.search_entry.get():
                self.search_entry.insert(0, self._placeholder_text)
                self.search_entry.configure(foreground='#94a3b8')

        def _clear_placeholder(event=None):
            if self.search_entry.get() == self._placeholder_text:
                self.search_entry.delete(0, tk.END)
                self.search_entry.configure(foreground='#0f172a')

        self.search_entry.bind('<FocusIn>', _clear_placeholder)
        self.search_entry.bind('<FocusOut>', lambda e: _add_placeholder())
        _add_placeholder()

        # TABLE
        columns = ("id", "type", "title", "author", "year")
        tree_frame = ttk.Frame(root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=(8, 6))

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        self.tree.column("id", width=60, anchor='center')
        self.tree.column("type", width=100, anchor='center')
        self.tree.column("title", width=320)
        self.tree.column("author", width=220)
        self.tree.column("year", width=80, anchor='center')

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # alternating row colors
        self.tree.tag_configure('odd', background='#ffffff')
        self.tree.tag_configure('even', background='#f8fafc')

        # FORM FRAME
        form = ttk.Frame(root, padding=(12, 10, 12, 12))
        form.pack(fill=tk.X, padx=18, pady=(4, 12))

        ttk.Label(form, text="Type:").grid(row=0, column=0, sticky='w', padx=(0,8), pady=4)
        self.type_box = ttk.Combobox(form, values=["book", "magazine", "film"], width=18)
        self.type_box.grid(row=0, column=1, sticky='w')
        self.type_box.set("book")

        ttk.Label(form, text="Title:").grid(row=1, column=0, sticky='w', padx=(0,8), pady=4)
        self.title_entry = ttk.Entry(form, width=40)
        self.title_entry.grid(row=1, column=1, sticky='w')

        ttk.Label(form, text="Author/Director:").grid(row=2, column=0, sticky='w', padx=(0,8), pady=4)
        self.author_entry = ttk.Entry(form, width=40)
        self.author_entry.grid(row=2, column=1, sticky='w')

        ttk.Label(form, text="Year:").grid(row=3, column=0, sticky='w', padx=(0,8), pady=4)
        self.year_entry = ttk.Entry(form, width=18)
        self.year_entry.grid(row=3, column=1, sticky='w')

        # Buttons (ttk for modern look)
        ttk.Button(form, text="Add Item", command=self.add_item, style='Accent.TButton').grid(row=4, column=0, pady=12)
        ttk.Button(form, text="Delete Selected", command=self.delete_item).grid(row=4, column=1, sticky='w')
        ttk.Button(form, text="Reset Form", command=self.reset_form).grid(row=4, column=2, sticky='w', padx=8)

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
