import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Warehouse Inventory Management System")
        self.root.geometry("680x560")
        
        self.current_filename = "inventory_data.json"  # Default save file
        self.inventory = {}
        
        # Load default file on startup if it exists
        self.load_default_file()

        # --- Top Menu Bar ---
        menubar = tk.Menu(root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)

        # --- UI Title ---
        title_label = tk.Label(root, text="📦 Inventory Dashboard", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # --- Input Frame ---
        input_frame = tk.LabelFrame(root, text=" Item Operations ", font=("Arial", 11, "bold"), padx=15, pady=15)
        input_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(input_frame, text="Item Name:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = tk.Entry(input_frame, font=("Arial", 10), width=22)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Quantity:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.qty_entry = tk.Entry(input_frame, font=("Arial", 10), width=22)
        self.qty_entry.grid(row=1, column=1, padx=5, pady=5)

        # Action Buttons Frame
        btn_frame = tk.Frame(input_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=12)

        tk.Button(btn_frame, text="Stock In", bg="#4CAF50", fg="white", width=11, font=("Arial", 9, "bold"), command=self.add_stock).grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text="Stock Out", bg="#F44336", fg="white", width=11, font=("Arial", 9, "bold"), command=self.remove_stock).grid(row=0, column=1, padx=4)
        tk.Button(btn_frame, text="Load Stock", bg="#FF9800", fg="white", width=11, font=("Arial", 9, "bold"), command=self.load_stock).grid(row=0, column=2, padx=4)
        tk.Button(btn_frame, text="Unload Stock", bg="#2196F3", fg="white", width=11, font=("Arial", 9, "bold"), command=self.unload_stock).grid(row=0, column=3, padx=4)

        # --- Inventory Table Display ---
        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("Item Name", "Total Quantity", "Loaded", "Unloaded")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Bottom Controls ---
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(bottom_frame, text="🔴 Check Out-of-Stock", font=("Arial", 10), command=self.check_out_of_stock).pack(side="left")
        tk.Button(bottom_frame, text="Clear Inputs", font=("Arial", 10), command=self.clear_fields).pack(side="right")

        self.update_table()

    def load_default_file(self):
        """Loads default inventory file on startup if present."""
        if os.path.exists(self.current_filename):
            try:
                with open(self.current_filename, "r") as f:
                    self.inventory = json.load(f)
            except Exception:
                self.inventory = {}

    def open_file(self):
        """Opens an existing JSON inventory file via file dialog."""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Open Inventory File"
        )
        if file_path:
            try:
                with open(file_path, "r") as f:
                    self.inventory = json.load(f)
                self.current_filename = file_path
                self.update_table()
                messagebox.showinfo("Success", f"Successfully loaded from:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not parse file:\n{e}")

    def save_file(self):
        """Saves current inventory to the active file path."""
        try:
            with open(self.current_filename, "w") as f:
                json.dump(self.inventory, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file:\n{e}")

    def auto_save(self):
        """Helper to trigger background save after any stock modification."""
        try:
            with open(self.current_filename, "w") as f:
                json.dump(self.inventory, f, indent=4)
        except Exception:
            pass

    def save_as_file(self):
        """Saves current inventory to a new user-selected file path."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialfile="my_inventory.json",
            title="Save Inventory As"
        )
        if file_path:
            self.current_filename = file_path
            self.save_file()
            messagebox.showinfo("Success", f"Successfully saved to:\n{os.path.basename(file_path)}")

    def get_inputs(self):
        name = self.name_entry.get().strip().title()
        if not name:
            messagebox.showerror("Error", "Please enter an item name.")
            return None, None
        try:
            qty = int(self.qty_entry.get().strip())
            if qty <= 0:
                raise ValueError
            return name, qty
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive integer for quantity.")
            return None, None

    def add_stock(self):
        name, qty = self.get_inputs()
        if not name: return

        if name in self.inventory:
            self.inventory[name]["quantity"] += qty
            self.inventory[name]["unloaded"] += qty
        else:
            self.inventory[name] = {"quantity": qty, "loaded": 0, "unloaded": qty}
        
        self.auto_save()
        messagebox.showinfo("Success", f"Added {qty} units of '{name}' to stock.")
        self.update_table()
        self.clear_fields()

    def remove_stock(self):
        name, qty = self.get_inputs()
        if not name: return

        if name not in self.inventory:
            messagebox.showerror("Error", f"Item '{name}' does not exist in inventory.")
            return

        current_qty = self.inventory[name]["quantity"]
        if qty > current_qty:
            messagebox.showerror("Error", f"Cannot remove {qty}. Only {current_qty} units available.")
            return

        self.inventory[name]["quantity"] -= qty
        unloaded = self.inventory[name]["unloaded"]
        if qty <= unloaded:
            self.inventory[name]["unloaded"] -= qty
        else:
            remainder = qty - unloaded
            self.inventory[name]["unloaded"] = 0
            self.inventory[name]["loaded"] = max(0, self.inventory[name]["loaded"] - remainder)

        self.auto_save()
        messagebox.showinfo("Success", f"Removed {qty} units of '{name}'.")
        self.update_table()
        self.clear_fields()

    def load_stock(self):
        name, qty = self.get_inputs()
        if not name: return

        if name not in self.inventory:
            messagebox.showerror("Error", f"Item '{name}' does not exist in inventory.")
            return

        unloaded_qty = self.inventory[name]["unloaded"]
        if qty > unloaded_qty:
            messagebox.showerror("Error", f"Cannot load {qty}. Only {unloaded_qty} units available in storage.")
            return

        self.inventory[name]["unloaded"] -= qty
        self.inventory[name]["loaded"] += qty
        
        self.auto_save()
        messagebox.showinfo("Success", f"Loaded {qty} units of '{name}'.")
        self.update_table()
        self.clear_fields()

    def unload_stock(self):
        name, qty = self.get_inputs()
        if not name: return

        if name not in self.inventory:
            messagebox.showerror("Error", f"Item '{name}' does not exist in inventory.")
            return

        loaded_qty = self.inventory[name]["loaded"]
        if qty > loaded_qty:
            messagebox.showerror("Error", f"Cannot unload {qty}. Only {loaded_qty} units are currently loaded.")
            return

        self.inventory[name]["loaded"] -= qty
        self.inventory[name]["unloaded"] += qty
        
        self.auto_save()
        messagebox.showinfo("Success", f"Returned {qty} units of '{name}' to storage.")
        self.update_table()
        self.clear_fields()

    def check_out_of_stock(self):
        out_items = [name for name, data in self.inventory.items() if data["quantity"] == 0]
        if not out_items:
            messagebox.showinfo("Out of Stock Status", "No items are currently out of stock!")
        else:
            messagebox.showwarning("Out of Stock Items", "The following items are out of stock:\n• " + "\n• ".join(out_items))

    def update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for name, data in self.inventory.items():
            self.tree.insert("", "end", values=(name, data["quantity"], data["loaded"], data["unloaded"]))

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
