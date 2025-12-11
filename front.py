import tkinter as tk
from tkinter import ttk, messagebox
import requests

API = "http://127.0.0.1:5000/items"

class InventoryApp:
    def __init__(self, root):
        self.root = root
        root.title("Reddy Book Inventory")
        root.geometry("850x500")
        root.configure(bg="#0073ff")

        title = tk.Label(root, text="📚 Reddy Book Inventory", font=("Arial", 22, "bold"), bg="#e8ecf1")
        title.pack(pady=10)

        # SEARCH BAR
        search_frame = tk.Frame(root, bg="#0073ff")
        search_frame.pack()

        tk.Label(search_frame, text="Search by Name:", bg="#e8ecf1").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(search_frame, text="   Type:", bg="#e8ecf1").pack(side=tk.LEFT)
        self.type_filter = ttk.Combobox(search_frame, values=["", "book", "magazine", "film"], width=10)
        self.type_filter.pack(side=tk.LEFT)
        self.type_filter.set("")

        tk.Button(search_frame, text="Search", command=self.load_items).pack(side=tk.LEFT)
        tk.Button(search_frame, text="Reset", command=self.reset_filters).pack(side=tk.LEFT, padx=5)

        # TABLE
        columns = ("id", "type", "title", "author", "year")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=12)

        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=120)

        self.tree.pack(pady=10)

        # FORM FRAME
        form = tk.Frame(root, bg="#e8ecf1")
        form.pack()

        tk.Label(form, text="Type:", bg="#e8ecf1").grid(row=0, column=0)
        self.type_box = ttk.Combobox(form, values=["book", "magazine", "film"], width=15)
        self.type_box.grid(row=0, column=1)
        self.type_box.set("book")

        tk.Label(form, text="Title:", bg="#e8ecf1").grid(row=1, column=0)
        self.title_entry = tk.Entry(form)
        self.title_entry.grid(row=1, column=1)

        tk.Label(form, text="Author/Director:", bg="#e8ecf1").grid(row=2, column=0)
        self.author_entry = tk.Entry(form)
        self.author_entry.grid(row=2, column=1)

        tk.Label(form, text="Year:", bg="#e8ecf1").grid(row=3, column=0)
        self.year_entry = tk.Entry(form)
        self.year_entry.grid(row=3, column=1)

        # BUTTONS
        tk.Button(form, text="Add Item", command=self.add_item, bg="#4caf50", fg="white").grid(row=4, column=0, pady=10)
        tk.Button(form, text="Delete Selected", command=self.delete_item, bg="#e53935", fg="white").grid(row=4, column=1)
        tk.Button(form, text="Reset Form", command=self.reset_form, bg="#ff9800", fg="white").grid(row=4, column=2, padx=5)

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
